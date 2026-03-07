import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import html
from datetime import datetime


# ── RSS Feed Sources ───────────────────────────────────────────────────

FEEDS = [
    {
        "name": "ORF Sport - Fußball",
        "url": "https://rss.orf.at/sport.xml",
        "lang": "de",
    },
    {
        "name": "Laola1 - Bundesliga",
        "url": "https://www.laola1.at/de/rss/fussball/",
        "lang": "de",
    },
    {
        "name": "Kurier Sport",
        "url": "https://kurier.at/xml/rssd/sport",
        "lang": "de",
    },
]

# Austrian football keywords for filtering
AT_FOOTBALL_KEYWORDS = [
    "bundesliga", "rapid", "austria wien", "sturm graz", "salzburg",
    "lask", "wolfsberger", "wac", "hartberg", "altach", "klagenfurt",
    "wsg tirol", "blau-weiß linz", "blau-weiss linz", "gak",
    "grazer ak", "öfb", "oefb", "fußball", "fussball",
    "red bull salzburg", "austria klagenfurt",
]


def fetch_rss_feed(url, timeout=10):
    """Fetch and parse an RSS feed, returning a list of article dicts."""
    articles = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ATFootballHub/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        root = ET.fromstring(data)

        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate", "").strip()

            # Clean HTML from description
            description = re.sub(r"<[^>]+>", "", html.unescape(description))

            if title:
                articles.append({
                    "title": title,
                    "link": link,
                    "description": description[:500],
                    "pub_date": pub_date,
                    "source_url": url,
                })
    except Exception as e:
        print(f"Error fetching {url}: {e}")

    return articles


def is_austrian_football(article):
    """Check if an article is about Austrian football."""
    text = (article["title"] + " " + article["description"]).lower()
    return any(kw in text for kw in AT_FOOTBALL_KEYWORDS)


def fetch_all_news(filter_relevant=True):
    """Fetch news from all feeds, optionally filtering for Austrian football."""
    all_articles = []
    for feed in FEEDS:
        articles = fetch_rss_feed(feed["url"])
        for a in articles:
            a["source_name"] = feed["name"]
            a["lang"] = feed["lang"]
        all_articles.extend(articles)

    if filter_relevant:
        all_articles = [a for a in all_articles if is_austrian_football(a)]

    return all_articles


# ── LLM Processing with Claude ────────────────────────────────────────

def get_anthropic_client():
    """Get an Anthropic client. Requires ANTHROPIC_API_KEY env var."""
    try:
        import anthropic
        return anthropic.Anthropic()
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Anthropic client: {e}")


def process_articles_with_llm(articles, teams=None, players=None):
    """Process news articles with Claude to extract structured insights."""
    if not articles:
        return {"summary": "No articles to process.", "articles": []}

    client = get_anthropic_client()

    team_names = ", ".join(teams) if teams else "all Austrian Bundesliga teams"
    player_names = ", ".join(players) if players else "all players"

    articles_text = ""
    for i, a in enumerate(articles[:20], 1):
        articles_text += f"\n--- Article {i} ---\n"
        articles_text += f"Title: {a['title']}\n"
        articles_text += f"Source: {a.get('source_name', 'Unknown')}\n"
        articles_text += f"Date: {a.get('pub_date', 'Unknown')}\n"
        articles_text += f"Description: {a['description']}\n"

    prompt = f"""Analyze these Austrian football news articles. Focus on teams: {team_names}, and players: {player_names}.

{articles_text}

Provide a JSON response with this structure:
{{
    "summary": "A 2-3 sentence overview of the main Austrian football news",
    "articles": [
        {{
            "title": "Original or improved title",
            "summary": "1-2 sentence summary of the article",
            "teams_mentioned": ["team names mentioned"],
            "players_mentioned": ["player names mentioned"],
            "sentiment": "positive/neutral/negative",
            "category": "transfer/match_result/injury/general/league_news",
            "relevance_score": 1-10
        }}
    ],
    "transfer_rumors": ["Any transfer-related news snippets"],
    "injury_updates": ["Any injury-related news snippets"],
    "key_highlights": ["Top 3-5 bullet point highlights"]
}}

Respond ONLY with valid JSON, no markdown formatting."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        result_text = response.content[0].text
        # Try to parse as JSON
        return json.loads(result_text)
    except (json.JSONDecodeError, IndexError):
        return {
            "summary": response.content[0].text if response.content else "No response",
            "articles": [],
            "raw_response": True,
        }


def scan_news_for_team(team_name):
    """Scan news specifically for a team."""
    articles = fetch_all_news(filter_relevant=False)
    team_articles = [
        a for a in articles
        if team_name.lower() in (a["title"] + " " + a["description"]).lower()
    ]
    # Fall back to all Austrian football news if no team-specific articles
    if not team_articles:
        team_articles = [a for a in articles if is_austrian_football(a)]
    return team_articles


def scan_news_for_player(player_name):
    """Scan news specifically for a player."""
    articles = fetch_all_news(filter_relevant=False)
    player_articles = [
        a for a in articles
        if player_name.lower() in (a["title"] + " " + a["description"]).lower()
    ]
    return player_articles
