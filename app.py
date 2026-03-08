import json
from flask import Flask, request, jsonify, render_template
from models import db, Team, Player, Match, MatchStats, PlayerMatchStats, Standing, PlayerStats, NewsArticle
from seed import seed_database
from news import fetch_all_news, process_articles_with_llm, scan_news_for_team, scan_news_for_player
from datetime import date


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///atfootball.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


# ── Pages ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Teams API ──────────────────────────────────────────────────────────

@app.route("/api/teams", methods=["GET"])
def get_teams():
    league = request.args.get("league")
    query = Team.query
    if league:
        query = query.filter_by(league=league)
    teams = query.order_by(Team.name).all()
    return jsonify([t.to_dict() for t in teams])


@app.route("/api/teams/<int:team_id>", methods=["GET"])
def get_team(team_id):
    team = db.get_or_404(Team, team_id)
    data = team.to_dict()
    data["players"] = [p.to_dict() for p in team.players]
    return jsonify(data)


@app.route("/api/teams", methods=["POST"])
def create_team():
    data = request.get_json()
    team = Team(
        name=data["name"],
        short_name=data.get("short_name"),
        city=data.get("city"),
        stadium=data.get("stadium"),
        founded_year=data.get("founded_year"),
        league=data.get("league", "Bundesliga"),
        logo_url=data.get("logo_url"),
    )
    db.session.add(team)
    db.session.commit()
    return jsonify(team.to_dict()), 201


@app.route("/api/teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    team = db.get_or_404(Team, team_id)
    data = request.get_json()
    for field in ["name", "short_name", "city", "stadium", "founded_year", "league", "logo_url"]:
        if field in data:
            setattr(team, field, data[field])
    db.session.commit()
    return jsonify(team.to_dict())


@app.route("/api/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    team = db.get_or_404(Team, team_id)
    db.session.delete(team)
    db.session.commit()
    return "", 204


# ── Players API ────────────────────────────────────────────────────────

@app.route("/api/players", methods=["GET"])
def get_players():
    team_id = request.args.get("team_id", type=int)
    position = request.args.get("position")
    nationality = request.args.get("nationality")
    query = Player.query
    if team_id:
        query = query.filter_by(team_id=team_id)
    if position:
        query = query.filter_by(position=position)
    if nationality:
        query = query.filter_by(nationality=nationality)
    players = query.order_by(Player.last_name).all()
    return jsonify([p.to_dict() for p in players])


@app.route("/api/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = db.get_or_404(Player, player_id)
    data = player.to_dict()
    data["stats"] = [s.to_dict() for s in player.stats]
    return jsonify(data)


@app.route("/api/players", methods=["POST"])
def create_player():
    data = request.get_json()
    dob = None
    if data.get("date_of_birth"):
        dob = date.fromisoformat(data["date_of_birth"])
    player = Player(
        first_name=data["first_name"],
        last_name=data["last_name"],
        date_of_birth=dob,
        nationality=data.get("nationality"),
        position=data.get("position"),
        jersey_number=data.get("jersey_number"),
        team_id=data.get("team_id"),
        height_cm=data.get("height_cm"),
        preferred_foot=data.get("preferred_foot"),
    )
    db.session.add(player)
    db.session.commit()
    return jsonify(player.to_dict()), 201


@app.route("/api/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    player = db.get_or_404(Player, player_id)
    data = request.get_json()
    for field in ["first_name", "last_name", "nationality", "position",
                  "jersey_number", "team_id", "height_cm", "preferred_foot"]:
        if field in data:
            setattr(player, field, data[field])
    if "date_of_birth" in data:
        player.date_of_birth = date.fromisoformat(data["date_of_birth"]) if data["date_of_birth"] else None
    db.session.commit()
    return jsonify(player.to_dict())


@app.route("/api/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    player = db.get_or_404(Player, player_id)
    db.session.delete(player)
    db.session.commit()
    return "", 204


# ── Matches API ────────────────────────────────────────────────────────

@app.route("/api/matches", methods=["GET"])
def get_matches():
    season = request.args.get("season")
    team_id = request.args.get("team_id", type=int)
    query = Match.query
    if season:
        query = query.filter_by(season=season)
    if team_id:
        query = query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
    matches = query.order_by(Match.match_date.desc()).all()
    return jsonify([m.to_dict() for m in matches])


@app.route("/api/matches", methods=["POST"])
def create_match():
    data = request.get_json()
    match = Match(
        home_team_id=data["home_team_id"],
        away_team_id=data["away_team_id"],
        match_date=date.fromisoformat(data["match_date"]),
        season=data.get("season"),
        round=data.get("round"),
        home_score=data.get("home_score"),
        away_score=data.get("away_score"),
        status=data.get("status", "scheduled"),
        venue=data.get("venue"),
    )
    db.session.add(match)
    db.session.commit()
    return jsonify(match.to_dict()), 201


@app.route("/api/matches/<int:match_id>", methods=["PUT"])
def update_match(match_id):
    match = db.get_or_404(Match, match_id)
    data = request.get_json()
    for field in ["home_score", "away_score", "status", "venue", "round", "season"]:
        if field in data:
            setattr(match, field, data[field])
    if "match_date" in data:
        match.match_date = date.fromisoformat(data["match_date"])
    if "home_team_id" in data:
        match.home_team_id = data["home_team_id"]
    if "away_team_id" in data:
        match.away_team_id = data["away_team_id"]
    db.session.commit()
    return jsonify(match.to_dict())


# ── Match Stats API ───────────────────────────────────────────────────

MATCH_STATS_FIELDS = [
    "home_possession", "home_shots", "away_shots",
    "home_shots_on_target", "away_shots_on_target",
    "home_passes", "away_passes", "home_pass_accuracy", "away_pass_accuracy",
    "home_corners", "away_corners", "home_free_kicks", "away_free_kicks",
    "home_fouls", "away_fouls", "home_yellow_cards", "away_yellow_cards",
    "home_red_cards", "away_red_cards", "home_offsides", "away_offsides",
    "home_tackles", "away_tackles", "home_saves", "away_saves",
]


@app.route("/api/matches/<int:match_id>/stats", methods=["GET"])
def get_match_stats(match_id):
    db.get_or_404(Match, match_id)
    stats = MatchStats.query.filter_by(match_id=match_id).first()
    if not stats:
        return jsonify({"error": "No stats recorded for this match"}), 404
    return jsonify(stats.to_dict())


@app.route("/api/matches/<int:match_id>/stats", methods=["POST"])
def create_match_stats(match_id):
    db.get_or_404(Match, match_id)
    existing = MatchStats.query.filter_by(match_id=match_id).first()
    if existing:
        return jsonify({"error": "Stats already exist for this match. Use PUT to update."}), 409
    data = request.get_json()
    stats = MatchStats(match_id=match_id)
    for field in MATCH_STATS_FIELDS:
        if field in data:
            setattr(stats, field, data[field])
    db.session.add(stats)
    db.session.commit()
    return jsonify(stats.to_dict()), 201


@app.route("/api/matches/<int:match_id>/stats", methods=["PUT"])
def update_match_stats(match_id):
    db.get_or_404(Match, match_id)
    stats = MatchStats.query.filter_by(match_id=match_id).first()
    if not stats:
        return jsonify({"error": "No stats found. Use POST to create."}), 404
    data = request.get_json()
    for field in MATCH_STATS_FIELDS:
        if field in data:
            setattr(stats, field, data[field])
    db.session.commit()
    return jsonify(stats.to_dict())


# ── Player Match Stats API ────────────────────────────────────────────

@app.route("/api/matches/<int:match_id>/player-stats", methods=["GET"])
def get_player_match_stats(match_id):
    db.get_or_404(Match, match_id)
    stats = PlayerMatchStats.query.filter_by(match_id=match_id).all()
    return jsonify([s.to_dict() for s in stats])


@app.route("/api/matches/<int:match_id>/player-stats", methods=["POST"])
def create_player_match_stats(match_id):
    db.get_or_404(Match, match_id)
    data = request.get_json()
    stats = PlayerMatchStats(match_id=match_id, player_id=data["player_id"])
    stat_fields = [
        "minutes_played", "started", "substituted_in", "substituted_out",
        "distance_km", "sprints", "top_speed_kmh",
        "goals", "assists", "shots", "shots_on_target", "chances_created",
        "passes_completed", "passes_attempted", "key_passes", "crosses",
        "tackles", "interceptions", "clearances", "blocks",
        "aerial_duels_won", "aerial_duels_lost",
        "fouls_committed", "fouls_drawn", "yellow_card", "red_card",
        "saves", "goals_conceded", "rating",
    ]
    for field in stat_fields:
        if field in data:
            setattr(stats, field, data[field])
    db.session.add(stats)
    db.session.commit()
    return jsonify(stats.to_dict()), 201


@app.route("/api/players/<int:player_id>/match-stats", methods=["GET"])
def get_player_all_match_stats(player_id):
    db.get_or_404(Player, player_id)
    stats = PlayerMatchStats.query.filter_by(player_id=player_id).all()
    return jsonify([s.to_dict() for s in stats])


# ── Standings API ──────────────────────────────────────────────────────

@app.route("/api/standings", methods=["GET"])
def get_standings():
    season = request.args.get("season", "2025-26")
    standings = (
        Standing.query.filter_by(season=season)
        .join(Team)
        .order_by(Standing.points.desc(), (Standing.goals_for - Standing.goals_against).desc())
        .all()
    )
    return jsonify([s.to_dict() for s in standings])


# ── Player Stats API ──────────────────────────────────────────────────

@app.route("/api/player-stats", methods=["GET"])
def get_player_stats():
    season = request.args.get("season")
    query = PlayerStats.query
    if season:
        query = query.filter_by(season=season)
    stats = query.order_by(PlayerStats.goals.desc()).all()
    return jsonify([s.to_dict() for s in stats])


@app.route("/api/player-stats", methods=["POST"])
def create_player_stats():
    data = request.get_json()
    stats = PlayerStats(
        player_id=data["player_id"],
        season=data["season"],
        appearances=data.get("appearances", 0),
        goals=data.get("goals", 0),
        assists=data.get("assists", 0),
        yellow_cards=data.get("yellow_cards", 0),
        red_cards=data.get("red_cards", 0),
        minutes_played=data.get("minutes_played", 0),
    )
    db.session.add(stats)
    db.session.commit()
    return jsonify(stats.to_dict()), 201


# ── News API ──────────────────────────────────────────────────────────

@app.route("/api/news/scan", methods=["POST"])
def scan_news():
    """Fetch latest news from RSS feeds about Austrian football."""
    data = request.get_json() or {}
    team_name = data.get("team")
    player_name = data.get("player")

    if team_name:
        articles = scan_news_for_team(team_name)
    elif player_name:
        articles = scan_news_for_player(player_name)
    else:
        articles = fetch_all_news(filter_relevant=True)

    # Store raw articles in DB
    for a in articles[:30]:
        existing = NewsArticle.query.filter_by(title=a["title"], link=a.get("link")).first()
        if not existing:
            article = NewsArticle(
                title=a["title"],
                link=a.get("link"),
                description=a.get("description"),
                source_name=a.get("source_name"),
                pub_date=a.get("pub_date"),
            )
            db.session.add(article)
    db.session.commit()

    return jsonify({
        "count": len(articles),
        "articles": articles[:30],
    })


@app.route("/api/news/analyze", methods=["POST"])
def analyze_news():
    """Fetch news and process with Claude LLM for structured insights."""
    data = request.get_json() or {}
    team_name = data.get("team")
    player_name = data.get("player")

    # Gather context from DB
    teams = [t.name for t in Team.query.all()]
    players = [f"{p.first_name} {p.last_name}" for p in Player.query.all()]

    if team_name:
        articles = scan_news_for_team(team_name)
        teams = [team_name]
    elif player_name:
        articles = scan_news_for_player(player_name)
        players = [player_name]
    else:
        articles = fetch_all_news(filter_relevant=True)

    if not articles:
        return jsonify({
            "summary": "No relevant Austrian football news found at this time.",
            "articles": [],
            "key_highlights": [],
        })

    try:
        result = process_articles_with_llm(articles[:20], teams=teams, players=players)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    # Store LLM-processed articles in DB
    if "articles" in result:
        for processed in result["articles"]:
            existing = NewsArticle.query.filter_by(title=processed.get("title", "")).first()
            if existing:
                existing.llm_summary = processed.get("summary")
                existing.sentiment = processed.get("sentiment")
                existing.category = processed.get("category")
                existing.teams_mentioned = json.dumps(processed.get("teams_mentioned", []))
                existing.players_mentioned = json.dumps(processed.get("players_mentioned", []))
                existing.relevance_score = processed.get("relevance_score")
        db.session.commit()

    return jsonify(result)


@app.route("/api/news", methods=["GET"])
def get_stored_news():
    """Get previously fetched and analyzed news from the database."""
    team = request.args.get("team")
    category = request.args.get("category")
    query = NewsArticle.query

    if team:
        query = query.filter(NewsArticle.teams_mentioned.contains(team))
    if category:
        query = query.filter_by(category=category)

    articles = query.order_by(NewsArticle.fetched_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in articles])


# ── Seed endpoint ─────────────────────────────────────────────────────

@app.route("/api/seed", methods=["POST"])
def seed():
    seed_database(db)
    return jsonify({"message": "Database seeded with Austrian football data"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
