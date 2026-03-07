from models import Team, Player, Standing, PlayerStats, Match, MatchStats, PlayerMatchStats
from datetime import date
import random


def seed_database(db):
    if Team.query.first():
        return

    teams_data = [
        {"name": "SK Sturm Graz", "short_name": "STU", "city": "Graz",
         "stadium": "Merkur Arena", "founded_year": 1909, "league": "Bundesliga"},
        {"name": "FC Red Bull Salzburg", "short_name": "RBS", "city": "Salzburg",
         "stadium": "Red Bull Arena", "founded_year": 1933, "league": "Bundesliga"},
        {"name": "SK Rapid Wien", "short_name": "RAP", "city": "Wien",
         "stadium": "Allianz Stadion", "founded_year": 1899, "league": "Bundesliga"},
        {"name": "FK Austria Wien", "short_name": "AUS", "city": "Wien",
         "stadium": "Generali Arena", "founded_year": 1911, "league": "Bundesliga"},
        {"name": "LASK", "short_name": "LASK", "city": "Linz",
         "stadium": "Raiffeisen Arena", "founded_year": 1908, "league": "Bundesliga"},
        {"name": "Wolfsberger AC", "short_name": "WAC", "city": "Wolfsberg",
         "stadium": "Lavanttal-Arena", "founded_year": 1931, "league": "Bundesliga"},
        {"name": "TSV Hartberg", "short_name": "HAR", "city": "Hartberg",
         "stadium": "Profertil Arena", "founded_year": 1946, "league": "Bundesliga"},
        {"name": "SCR Altach", "short_name": "ALT", "city": "Altach",
         "stadium": "Cashpoint Arena", "founded_year": 1929, "league": "Bundesliga"},
        {"name": "Austria Klagenfurt", "short_name": "KLA", "city": "Klagenfurt",
         "stadium": "Wörthersee Stadion", "founded_year": 2007, "league": "Bundesliga"},
        {"name": "WSG Tirol", "short_name": "WSG", "city": "Wattens",
         "stadium": "Gernot Langes Stadion", "founded_year": 1930, "league": "Bundesliga"},
        {"name": "FC Blau-Weiß Linz", "short_name": "BWL", "city": "Linz",
         "stadium": "Hofmann Personal Stadion", "founded_year": 1997, "league": "Bundesliga"},
        {"name": "Grazer AK 1902", "short_name": "GAK", "city": "Graz",
         "stadium": "Merkur Arena", "founded_year": 1902, "league": "Bundesliga"},
    ]

    teams = {}
    for td in teams_data:
        team = Team(**td)
        db.session.add(team)
        db.session.flush()
        teams[td["short_name"]] = team

    players_data = [
        # Sturm Graz
        {"first_name": "Kjell", "last_name": "Scherpen", "nationality": "Netherlands",
         "position": "Goalkeeper", "jersey_number": 1, "team": "STU", "height_cm": 204},
        {"first_name": "Gregory", "last_name": "Wüthrich", "nationality": "Switzerland",
         "position": "Defender", "jersey_number": 5, "team": "STU", "height_cm": 190},
        {"first_name": "Otar", "last_name": "Kiteishvili", "nationality": "Georgia",
         "position": "Midfielder", "jersey_number": 10, "team": "STU", "height_cm": 178},
        {"first_name": "Manprit", "last_name": "Sarkaria", "nationality": "Austria",
         "position": "Forward", "jersey_number": 7, "team": "STU", "height_cm": 180},
        # Red Bull Salzburg
        {"first_name": "Janis", "last_name": "Blaswich", "nationality": "Germany",
         "position": "Goalkeeper", "jersey_number": 1, "team": "RBS", "height_cm": 194},
        {"first_name": "Samson", "last_name": "Baidoo", "nationality": "Ghana",
         "position": "Defender", "jersey_number": 4, "team": "RBS", "height_cm": 183},
        {"first_name": "Lucas", "last_name": "Gourna-Douath", "nationality": "France",
         "position": "Midfielder", "jersey_number": 8, "team": "RBS", "height_cm": 178},
        {"first_name": "Karim", "last_name": "Konaté", "nationality": "Ivory Coast",
         "position": "Forward", "jersey_number": 9, "team": "RBS", "height_cm": 183},
        # Rapid Wien
        {"first_name": "Niklas", "last_name": "Hedl", "nationality": "Austria",
         "position": "Goalkeeper", "jersey_number": 1, "team": "RAP", "height_cm": 190},
        {"first_name": "Matthias", "last_name": "Suttner", "nationality": "Austria",
         "position": "Defender", "jersey_number": 24, "team": "RAP", "height_cm": 182},
        {"first_name": "Guido", "last_name": "Burgstaller", "nationality": "Austria",
         "position": "Forward", "jersey_number": 9, "team": "RAP", "height_cm": 187},
        {"first_name": "Marco", "last_name": "Grüll", "nationality": "Austria",
         "position": "Forward", "jersey_number": 11, "team": "RAP", "height_cm": 178},
        # Austria Wien
        {"first_name": "Samuel", "last_name": "Sahin-Radlinger", "nationality": "Austria",
         "position": "Goalkeeper", "jersey_number": 1, "team": "AUS", "height_cm": 192},
        {"first_name": "Lukas", "last_name": "Mühl", "nationality": "Germany",
         "position": "Defender", "jersey_number": 4, "team": "AUS", "height_cm": 186},
        {"first_name": "Dominik", "last_name": "Fitz", "nationality": "Austria",
         "position": "Midfielder", "jersey_number": 10, "team": "AUS", "height_cm": 172},
        {"first_name": "Muharem", "last_name": "Huskovic", "nationality": "Austria",
         "position": "Forward", "jersey_number": 20, "team": "AUS", "height_cm": 185},
        # LASK
        {"first_name": "Tobias", "last_name": "Lawal", "nationality": "Austria",
         "position": "Goalkeeper", "jersey_number": 1, "team": "LASK", "height_cm": 190},
        {"first_name": "Philipp", "last_name": "Ziereis", "nationality": "Germany",
         "position": "Defender", "jersey_number": 4, "team": "LASK", "height_cm": 191},
        {"first_name": "Robert", "last_name": "Žulj", "nationality": "Austria",
         "position": "Midfielder", "jersey_number": 10, "team": "LASK", "height_cm": 181},
        {"first_name": "Marin", "last_name": "Ljubičić", "nationality": "Croatia",
         "position": "Forward", "jersey_number": 27, "team": "LASK", "height_cm": 190},
        # WAC
        {"first_name": "Hendrik", "last_name": "Bonmann", "nationality": "Germany",
         "position": "Goalkeeper", "jersey_number": 1, "team": "WAC", "height_cm": 192},
        {"first_name": "Dominik", "last_name": "Baumgartner", "nationality": "Austria",
         "position": "Defender", "jersey_number": 5, "team": "WAC", "height_cm": 186},
        {"first_name": "Thierno", "last_name": "Ballo", "nationality": "Austria",
         "position": "Midfielder", "jersey_number": 10, "team": "WAC", "height_cm": 175},
        {"first_name": "Tai", "last_name": "Baribo", "nationality": "Israel",
         "position": "Forward", "jersey_number": 9, "team": "WAC", "height_cm": 185},
    ]

    players = []
    for pd_item in players_data:
        team_key = pd_item.pop("team")
        player = Player(**pd_item, team_id=teams[team_key].id)
        db.session.add(player)
        players.append(player)

    db.session.flush()

    # Standings for 2025-26 season
    standings_data = [
        {"team": "STU", "position": 1, "played": 20, "won": 14, "drawn": 3, "lost": 3,
         "goals_for": 38, "goals_against": 16, "points": 45},
        {"team": "RBS", "position": 2, "played": 20, "won": 13, "drawn": 4, "lost": 3,
         "goals_for": 42, "goals_against": 18, "points": 43},
        {"team": "RAP", "position": 3, "played": 20, "won": 11, "drawn": 5, "lost": 4,
         "goals_for": 35, "goals_against": 22, "points": 38},
        {"team": "LASK", "position": 4, "played": 20, "won": 10, "drawn": 4, "lost": 6,
         "goals_for": 30, "goals_against": 23, "points": 34},
        {"team": "AUS", "position": 5, "played": 20, "won": 9, "drawn": 5, "lost": 6,
         "goals_for": 28, "goals_against": 24, "points": 32},
        {"team": "WAC", "position": 6, "played": 20, "won": 8, "drawn": 4, "lost": 8,
         "goals_for": 27, "goals_against": 28, "points": 28},
        {"team": "KLA", "position": 7, "played": 20, "won": 7, "drawn": 3, "lost": 10,
         "goals_for": 22, "goals_against": 29, "points": 24},
        {"team": "HAR", "position": 8, "played": 20, "won": 6, "drawn": 4, "lost": 10,
         "goals_for": 23, "goals_against": 31, "points": 22},
        {"team": "BWL", "position": 9, "played": 20, "won": 5, "drawn": 5, "lost": 10,
         "goals_for": 20, "goals_against": 30, "points": 20},
        {"team": "ALT", "position": 10, "played": 20, "won": 5, "drawn": 3, "lost": 12,
         "goals_for": 18, "goals_against": 34, "points": 18},
        {"team": "WSG", "position": 11, "played": 20, "won": 4, "drawn": 4, "lost": 12,
         "goals_for": 17, "goals_against": 35, "points": 16},
        {"team": "GAK", "position": 12, "played": 20, "won": 3, "drawn": 4, "lost": 13,
         "goals_for": 15, "goals_against": 38, "points": 13},
    ]

    for sd in standings_data:
        team_key = sd.pop("team")
        standing = Standing(**sd, team_id=teams[team_key].id, season="2025-26")
        db.session.add(standing)

    # Sample player stats
    for player in players:
        stats = PlayerStats(
            player_id=player.id,
            season="2025-26",
            appearances=random.randint(10, 20),
            goals=random.randint(0, 12) if player.position in ("Forward", "Midfielder") else random.randint(0, 2),
            assists=random.randint(0, 8),
            yellow_cards=random.randint(0, 5),
            red_cards=random.randint(0, 1),
            minutes_played=random.randint(600, 1800),
        )
        db.session.add(stats)

    # Sample matches
    sample_matches = [
        {"home": "STU", "away": "RBS", "date": "2025-08-23", "round": 1, "h": 2, "a": 1},
        {"home": "RAP", "away": "AUS", "date": "2025-08-24", "round": 1, "h": 3, "a": 1},
        {"home": "LASK", "away": "WAC", "date": "2025-08-24", "round": 1, "h": 1, "a": 1},
        {"home": "RBS", "away": "RAP", "date": "2025-08-30", "round": 2, "h": 2, "a": 0},
        {"home": "AUS", "away": "STU", "date": "2025-08-31", "round": 2, "h": 0, "a": 1},
        {"home": "WAC", "away": "GAK", "date": "2025-08-31", "round": 2, "h": 3, "a": 0},
        {"home": "STU", "away": "RAP", "date": "2025-09-14", "round": 3, "h": 1, "a": 1},
        {"home": "RBS", "away": "LASK", "date": "2025-09-14", "round": 3, "h": 4, "a": 2},
        {"home": "KLA", "away": "AUS", "date": "2025-09-15", "round": 3, "h": 2, "a": 2},
    ]

    matches = []
    for md in sample_matches:
        match = Match(
            home_team_id=teams[md["home"]].id,
            away_team_id=teams[md["away"]].id,
            match_date=date.fromisoformat(md["date"]),
            season="2025-26",
            round=md["round"],
            home_score=md["h"],
            away_score=md["a"],
            status="played",
            venue=teams[md["home"]].stadium,
        )
        db.session.add(match)
        matches.append(match)

    db.session.flush()

    # Match stats for each match
    for match in matches:
        home_poss = random.randint(38, 62)
        home_shots = random.randint(6, 20)
        away_shots = random.randint(4, 18)
        stats = MatchStats(
            match_id=match.id,
            home_possession=home_poss,
            home_shots=home_shots,
            away_shots=away_shots,
            home_shots_on_target=random.randint(1, min(home_shots, 10)),
            away_shots_on_target=random.randint(1, min(away_shots, 8)),
            home_passes=random.randint(280, 550),
            away_passes=random.randint(250, 520),
            home_pass_accuracy=random.randint(72, 92),
            away_pass_accuracy=random.randint(70, 90),
            home_corners=random.randint(2, 10),
            away_corners=random.randint(1, 8),
            home_free_kicks=random.randint(8, 20),
            away_free_kicks=random.randint(6, 18),
            home_fouls=random.randint(8, 18),
            away_fouls=random.randint(6, 16),
            home_yellow_cards=random.randint(0, 4),
            away_yellow_cards=random.randint(0, 4),
            home_red_cards=random.choice([0, 0, 0, 0, 0, 0, 0, 1]),
            away_red_cards=random.choice([0, 0, 0, 0, 0, 0, 0, 1]),
            home_offsides=random.randint(0, 5),
            away_offsides=random.randint(0, 5),
            home_tackles=random.randint(12, 28),
            away_tackles=random.randint(10, 26),
            home_saves=random.randint(1, 7),
            away_saves=random.randint(1, 6),
        )
        db.session.add(stats)

    # Player match stats for each match
    for match in matches:
        home_players = [p for p in players if p.team_id == match.home_team_id]
        away_players = [p for p in players if p.team_id == match.away_team_id]

        for player in home_players + away_players:
            is_gk = player.position == "Goalkeeper"
            is_def = player.position == "Defender"
            is_fwd = player.position == "Forward"
            minutes = random.choice([90, 90, 90, 90, 75, 60, 45])
            started = minutes >= 60

            pms = PlayerMatchStats(
                player_id=player.id,
                match_id=match.id,
                minutes_played=minutes,
                started=started,
                substituted_in=None if started else random.choice([46, 55, 60, 70]),
                substituted_out=random.choice([None, None, None, 75, 80, 85]) if started else None,
                distance_km=round(random.uniform(7.5 if is_gk else 9.0, 8.5 if is_gk else 12.5), 1),
                sprints=random.randint(5 if is_gk else 15, 12 if is_gk else 35),
                top_speed_kmh=round(random.uniform(22.0, 34.0), 1),
                goals=random.choice([0, 0, 0, 0, 0, 1]) if is_fwd else random.choice([0, 0, 0, 0, 0, 0, 0, 1]),
                assists=random.choice([0, 0, 0, 0, 1]),
                shots=random.randint(0, 5) if is_fwd else random.randint(0, 2),
                shots_on_target=random.randint(0, 2) if is_fwd else random.randint(0, 1),
                chances_created=random.randint(0, 3),
                passes_completed=random.randint(15 if is_gk else 20, 40 if is_gk else 65),
                passes_attempted=random.randint(25 if is_gk else 28, 50 if is_gk else 75),
                key_passes=random.randint(0, 4),
                crosses=random.randint(0, 5) if not is_gk else 0,
                tackles=random.randint(0, 2) if is_gk else random.randint(1, 6),
                interceptions=random.randint(0, 4) if is_def else random.randint(0, 2),
                clearances=random.randint(2, 8) if is_def else random.randint(0, 2),
                blocks=random.randint(0, 3) if is_def else random.randint(0, 1),
                aerial_duels_won=random.randint(0, 5),
                aerial_duels_lost=random.randint(0, 3),
                fouls_committed=random.randint(0, 3),
                fouls_drawn=random.randint(0, 3),
                yellow_card=random.random() < 0.12,
                red_card=random.random() < 0.02,
                saves=random.randint(1, 7) if is_gk else 0,
                goals_conceded=random.randint(0, 3) if is_gk else 0,
                rating=round(random.uniform(5.5, 9.0), 1),
            )
            db.session.add(pms)

    db.session.commit()
