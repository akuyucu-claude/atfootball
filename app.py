from flask import Flask, request, jsonify, render_template
from models import db, Team, Player, Match, Standing, PlayerStats
from seed import seed_database
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


# ── Seed endpoint ─────────────────────────────────────────────────────

@app.route("/api/seed", methods=["POST"])
def seed():
    seed_database(db)
    return jsonify({"message": "Database seeded with Austrian football data"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
