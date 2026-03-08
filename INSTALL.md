# Austrian Football Hub - Installation Guide

## Prerequisites

- Python 3.10+
- pip
- **macOS only**: Xcode Command Line Tools (run `xcode-select --install` if not already installed)

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd atfootball

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# If you hit C++ build errors on macOS (e.g. greenlet), run:
#   xcode-select --install
# then retry. Or install with pre-built wheels only:
#   pip install --only-binary :all: -r requirements.txt

# 4. Run the application
python app.py

# 5. Open in browser
# Visit http://localhost:5000
# Click "Seed Database" to populate with Austrian Bundesliga data
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | Database ORM |
| Flask-Migrate | 4.1.0 | Database migrations |
| anthropic | >=0.40.0 | Claude AI API (for news analysis) |

## Optional: AI News Analysis

To use the AI-powered news analysis feature, set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your-api-key-here    # Linux/macOS
# set ANTHROPIC_API_KEY=your-api-key-here     # Windows
```

Get an API key at https://console.anthropic.com/

## Project Structure

```
atfootball/
├── app.py              # Flask application and API routes
├── models.py           # SQLAlchemy database models
├── seed.py             # Sample data seeder
├── news.py             # RSS news fetcher and LLM processor
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css       # Application styles
│   └── app.js          # Frontend JavaScript
├── templates/
│   └── index.html      # Main HTML template
└── instance/
    └── atfootball.db   # SQLite database (auto-created)
```

## Features

- **Teams** - All 12 Austrian Bundesliga clubs with details
- **Players** - Player profiles with filtering by team/position
- **Standings** - League table with points, goal difference
- **Matches** - Match results with clickable detailed stats
- **Match Stats** - Possession, shots, passes, cards, etc.
- **Player Match Stats** - Distance run, sprints, top speed, ratings
- **News Scanner** - RSS feed aggregation from Austrian sports sources
- **AI Analysis** - Claude-powered news summarization and insights
