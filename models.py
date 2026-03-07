from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    short_name = db.Column(db.String(10))
    city = db.Column(db.String(80))
    stadium = db.Column(db.String(120))
    founded_year = db.Column(db.Integer)
    league = db.Column(db.String(80), default="Bundesliga")
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    players = db.relationship("Player", backref="team", lazy=True)
    home_matches = db.relationship(
        "Match", foreign_keys="Match.home_team_id", backref="home_team", lazy=True
    )
    away_matches = db.relationship(
        "Match", foreign_keys="Match.away_team_id", backref="away_team", lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "city": self.city,
            "stadium": self.stadium,
            "founded_year": self.founded_year,
            "league": self.league,
            "logo_url": self.logo_url,
        }


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(60))
    position = db.Column(db.String(30))
    jersey_number = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    height_cm = db.Column(db.Integer)
    preferred_foot = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    stats = db.relationship("PlayerStats", backref="player", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "nationality": self.nationality,
            "position": self.position,
            "jersey_number": self.jersey_number,
            "team_id": self.team_id,
            "team_name": self.team.name if self.team else None,
            "height_cm": self.height_cm,
            "preferred_foot": self.preferred_foot,
        }


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    match_date = db.Column(db.Date, nullable=False)
    season = db.Column(db.String(10))
    round = db.Column(db.Integer)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    status = db.Column(db.String(20), default="scheduled")
    venue = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    match_stats = db.relationship("MatchStats", backref="match", uselist=False, lazy=True)

    def to_dict(self):
        data = {
            "id": self.id,
            "home_team": self.home_team.to_dict() if self.home_team else None,
            "away_team": self.away_team.to_dict() if self.away_team else None,
            "match_date": self.match_date.isoformat() if self.match_date else None,
            "season": self.season,
            "round": self.round,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "status": self.status,
            "venue": self.venue,
        }
        if self.match_stats:
            data["stats"] = self.match_stats.to_dict()
        return data


class MatchStats(db.Model):
    __tablename__ = "match_stats"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False, unique=True)

    # Possession (percentage for home, away = 100 - home)
    home_possession = db.Column(db.Integer)

    # Shots
    home_shots = db.Column(db.Integer, default=0)
    away_shots = db.Column(db.Integer, default=0)
    home_shots_on_target = db.Column(db.Integer, default=0)
    away_shots_on_target = db.Column(db.Integer, default=0)

    # Passes
    home_passes = db.Column(db.Integer, default=0)
    away_passes = db.Column(db.Integer, default=0)
    home_pass_accuracy = db.Column(db.Integer)  # percentage
    away_pass_accuracy = db.Column(db.Integer)

    # Set pieces
    home_corners = db.Column(db.Integer, default=0)
    away_corners = db.Column(db.Integer, default=0)
    home_free_kicks = db.Column(db.Integer, default=0)
    away_free_kicks = db.Column(db.Integer, default=0)

    # Discipline
    home_fouls = db.Column(db.Integer, default=0)
    away_fouls = db.Column(db.Integer, default=0)
    home_yellow_cards = db.Column(db.Integer, default=0)
    away_yellow_cards = db.Column(db.Integer, default=0)
    home_red_cards = db.Column(db.Integer, default=0)
    away_red_cards = db.Column(db.Integer, default=0)

    # Other
    home_offsides = db.Column(db.Integer, default=0)
    away_offsides = db.Column(db.Integer, default=0)
    home_tackles = db.Column(db.Integer, default=0)
    away_tackles = db.Column(db.Integer, default=0)
    home_saves = db.Column(db.Integer, default=0)
    away_saves = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "match_id": self.match_id,
            "home_possession": self.home_possession,
            "away_possession": (100 - self.home_possession) if self.home_possession else None,
            "home_shots": self.home_shots,
            "away_shots": self.away_shots,
            "home_shots_on_target": self.home_shots_on_target,
            "away_shots_on_target": self.away_shots_on_target,
            "home_passes": self.home_passes,
            "away_passes": self.away_passes,
            "home_pass_accuracy": self.home_pass_accuracy,
            "away_pass_accuracy": self.away_pass_accuracy,
            "home_corners": self.home_corners,
            "away_corners": self.away_corners,
            "home_free_kicks": self.home_free_kicks,
            "away_free_kicks": self.away_free_kicks,
            "home_fouls": self.home_fouls,
            "away_fouls": self.away_fouls,
            "home_yellow_cards": self.home_yellow_cards,
            "away_yellow_cards": self.away_yellow_cards,
            "home_red_cards": self.home_red_cards,
            "away_red_cards": self.away_red_cards,
            "home_offsides": self.home_offsides,
            "away_offsides": self.away_offsides,
            "home_tackles": self.home_tackles,
            "away_tackles": self.away_tackles,
            "home_saves": self.home_saves,
            "away_saves": self.away_saves,
        }


class PlayerMatchStats(db.Model):
    __tablename__ = "player_match_stats"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)

    # Time
    minutes_played = db.Column(db.Integer, default=0)
    started = db.Column(db.Boolean, default=False)
    substituted_in = db.Column(db.Integer)   # minute subbed in
    substituted_out = db.Column(db.Integer)  # minute subbed out

    # Physical
    distance_km = db.Column(db.Float)        # total distance run
    sprints = db.Column(db.Integer, default=0)
    top_speed_kmh = db.Column(db.Float)

    # Attacking
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    chances_created = db.Column(db.Integer, default=0)

    # Passing
    passes_completed = db.Column(db.Integer, default=0)
    passes_attempted = db.Column(db.Integer, default=0)
    key_passes = db.Column(db.Integer, default=0)
    crosses = db.Column(db.Integer, default=0)

    # Defending
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    aerial_duels_won = db.Column(db.Integer, default=0)
    aerial_duels_lost = db.Column(db.Integer, default=0)

    # Discipline
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_drawn = db.Column(db.Integer, default=0)
    yellow_card = db.Column(db.Boolean, default=False)
    red_card = db.Column(db.Boolean, default=False)

    # Goalkeeper specific
    saves = db.Column(db.Integer, default=0)
    goals_conceded = db.Column(db.Integer, default=0)

    # Rating
    rating = db.Column(db.Float)  # match rating out of 10

    player = db.relationship("Player", backref="match_performances")
    match = db.relationship("Match", backref="player_stats")

    __table_args__ = (
        db.UniqueConstraint("player_id", "match_id", name="uq_player_match"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "player_name": f"{self.player.first_name} {self.player.last_name}" if self.player else None,
            "player_position": self.player.position if self.player else None,
            "player_jersey": self.player.jersey_number if self.player else None,
            "match_id": self.match_id,
            "minutes_played": self.minutes_played,
            "started": self.started,
            "substituted_in": self.substituted_in,
            "substituted_out": self.substituted_out,
            "distance_km": self.distance_km,
            "sprints": self.sprints,
            "top_speed_kmh": self.top_speed_kmh,
            "goals": self.goals,
            "assists": self.assists,
            "shots": self.shots,
            "shots_on_target": self.shots_on_target,
            "chances_created": self.chances_created,
            "passes_completed": self.passes_completed,
            "passes_attempted": self.passes_attempted,
            "pass_accuracy": round(self.passes_completed / self.passes_attempted * 100) if self.passes_attempted else None,
            "key_passes": self.key_passes,
            "crosses": self.crosses,
            "tackles": self.tackles,
            "interceptions": self.interceptions,
            "clearances": self.clearances,
            "blocks": self.blocks,
            "aerial_duels_won": self.aerial_duels_won,
            "aerial_duels_lost": self.aerial_duels_lost,
            "fouls_committed": self.fouls_committed,
            "fouls_drawn": self.fouls_drawn,
            "yellow_card": self.yellow_card,
            "red_card": self.red_card,
            "saves": self.saves,
            "goals_conceded": self.goals_conceded,
            "rating": self.rating,
        }


class Standing(db.Model):
    __tablename__ = "standings"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    season = db.Column(db.String(10), nullable=False)
    position = db.Column(db.Integer)
    played = db.Column(db.Integer, default=0)
    won = db.Column(db.Integer, default=0)
    drawn = db.Column(db.Integer, default=0)
    lost = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    team = db.relationship("Team", backref="standings")

    __table_args__ = (
        db.UniqueConstraint("team_id", "season", name="uq_team_season"),
    )

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    def to_dict(self):
        return {
            "id": self.id,
            "team": self.team.to_dict() if self.team else None,
            "season": self.season,
            "position": self.position,
            "played": self.played,
            "won": self.won,
            "drawn": self.drawn,
            "lost": self.lost,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "goal_difference": self.goal_difference,
            "points": self.points,
        }


class PlayerStats(db.Model):
    __tablename__ = "player_stats"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    season = db.Column(db.String(10), nullable=False)
    appearances = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    minutes_played = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint("player_id", "season", name="uq_player_season"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "player_name": f"{self.player.first_name} {self.player.last_name}" if self.player else None,
            "season": self.season,
            "appearances": self.appearances,
            "goals": self.goals,
            "assists": self.assists,
            "yellow_cards": self.yellow_cards,
            "red_cards": self.red_cards,
            "minutes_played": self.minutes_played,
        }


class NewsArticle(db.Model):
    __tablename__ = "news_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(500))
    description = db.Column(db.Text)
    source_name = db.Column(db.String(120))
    pub_date = db.Column(db.String(100))
    llm_summary = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    category = db.Column(db.String(30))
    teams_mentioned = db.Column(db.Text)  # JSON array
    players_mentioned = db.Column(db.Text)  # JSON array
    relevance_score = db.Column(db.Integer)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "source_name": self.source_name,
            "pub_date": self.pub_date,
            "llm_summary": self.llm_summary,
            "sentiment": self.sentiment,
            "category": self.category,
            "teams_mentioned": json.loads(self.teams_mentioned) if self.teams_mentioned else [],
            "players_mentioned": json.loads(self.players_mentioned) if self.players_mentioned else [],
            "relevance_score": self.relevance_score,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
