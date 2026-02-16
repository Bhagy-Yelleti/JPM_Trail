# JPM Trail

A crisis management system designed to help coordinate response efforts by tracking cases and volunteers. Built with Flask and SQLite for simplicity and ease of use.

## What This App Does

JPM Trail helps you manage crisis cases and keep track of available volunteers. You can:
- Record new crisis cases with details about severity, urgency, and affected population
- Automatically prioritize cases based on their impact and urgency
- Maintain a roster of volunteers and their skills
- Track which volunteers are available for deployment
- See an overview of all active cases and their status

## Getting Started

### Installation

```bash
pip install Flask
python app.py
```

The database will be created automatically the first time you run the app.

### Running the App

```bash
python app.py
```

Then open your browser and go to:
```
http://127.0.0.1:5000
```

You'll see some sample data already loaded so you can explore the app right away.

## How Cases Get Prioritized

Cases are scored automatically based on four factors:

```
Priority Score = (Severity × 3) + (Population × 2) + (Urgency × 4) - (Resources × 2)
```

- **Severity** (1-5): How serious is the crisis
- **Population** (×2): How many people are affected
- **Urgency** (1-5): How time-sensitive is the response
- **Resources** (subtracted): What resources are already available

Higher scores mean the case needs attention sooner. Cases are sorted by this score so responders see the most critical situations first.

## What's Inside

### Cases
Each crisis case records:
- What happened and why it matters (title and description)
- How severe the situation is (severity, 1-5 scale)
- How many people are affected
- How urgent the response needs to be
- What kind of help is needed (required skill)
- Current resources available to help
- Status tracking (Pending, Active, Completed)

### Volunteers
The system tracks volunteers and:
- Their name and contact info
- What skills they have
- Whether they're currently available
- When they registered

## Project Layout

```
JPM_Trail/
├── app.py                    # Main application
├── impactbridge.db           # Database (created when you first run the app)
├── requirements.txt          # Dependencies
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── services.py               # Helper functions
├── validators.py             # Input validation
├── templates/                # HTML pages
│   ├── base.html            # Base template (header, nav styling)
│   ├── index.html           # Home/dashboard
│   ├── cases.html           # View all cases
│   ├── new_case.html        # Add a new case
│   ├── volunteers.html      # View all volunteers
│   └── register_volunteer.html  # Register a new volunteer
└── static/
    └── style.css            # Styling for the app
```

## How to Use It

1. **Add Cases**: Fill out the form to report a new crisis case. The priority score is calculated automatically.
2. **View Cases**: See all cases sorted by priority. The most urgent ones appear first.
3. **Register Volunteers**: Add volunteers and list their skills.
4. **Update Status**: Mark cases as active or completed as you respond to them.
5. **Check Availability**: See which volunteers are available to help.

## The Tech Stack

- **Python Flask**: Simple web framework to handle requests and responses
- **SQLite**: Database stored as a single file on your computer
- **HTML & CSS**: Simple interface to interact with the system

No complicated extras. Just the core tools needed to manage cases and volunteers.

## Database Management

Query the database directly:

```bash
sqlite3 impactbridge.db
```

```sql
SELECT * FROM cases ORDER BY priority_score DESC;
SELECT * FROM volunteers;
.quit
```

Reset database:
```bash
rm impactbridge.db
python app.py
```

Backup:
```bash
cp impactbridge.db impactbridge.db.backup
```

## Modifying the Code

File structure:
- `app.py` - Main application & routes
- `models.py` - Database queries
- `services.py` - Helper functions & calculations
- `validators.py` - Data validation
- `config.py` - Settings
- `templates/` - HTML pages
- `static/` - CSS styling

## Deployment

Database is a single file (`impactbridge.db`), making it portable and easy to back up or move.
