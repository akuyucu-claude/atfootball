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

    def to_dict(self):
        return {
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
