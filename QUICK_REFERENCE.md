# ImpactBridge Quick Reference

## Installation

```bash
pip install Flask
python app.py
```

Open: `http://127.0.0.1:5000`

**Note:** Database is automatically seeded with 25 crisis cases and 15 volunteers on first run.

## Database Location

```
ImpactBridge/impactbridge.db
```

## Priority Formula

```
Priority = (Severity × 3) + (People × 2) + (Urgency × 4) - (Resources × 2)
```

## Database Schema

### Cases Table
```
id, title, description, severity (1-5), people_affected,
urgency (1-5), available_resources, required_skill,
priority_score, status, created_at
```

### Volunteers Table
```
id, name, skills, availability (0/1), registered_at
```

## Common Operations

### View Database
```bash
sqlite3 impactbridge.db
.tables
SELECT * FROM cases ORDER BY priority_score DESC LIMIT 10;
.quit
```

### Backup
```bash
cp impactbridge.db impactbridge.db.backup
```

### Reset
```bash
rm impactbridge.db
python app.py  # Recreates and reseeds database
```

## Code Patterns

### Database Query
```python
conn = get_db_connection()
result = conn.execute('SELECT * FROM cases').fetchall()
conn.close()
```

### Insert Data
```python
conn = get_db_connection()
conn.execute('INSERT INTO cases (...) VALUES (?, ?, ...)', (val1, val2, ...))
conn.commit()
conn.close()
```

## File Structure

```
app.py                  # Main application
impactbridge.db         # Database (auto-created)
templates/              # HTML files
static/style.css        # Styling
```

## Key Routes

- `/` - Command Center (dashboard)
- `/cases` - Field Operations (list)
- `/cases/new` - Report Crisis (form)
- `/volunteers` - Response Personnel (list)
- `/volunteers/register` - Register Personnel (form)

## Documentation

- `README.md` - Quick start
- `SQLITE_IMPLEMENTATION_GUIDE.md` - Detailed guide
- `DATABASE_SEEDING_GUIDE.md` - Sample data information
- `FINAL_REFACTOR_SUMMARY.md` - Complete overview

## Sample Data

On first run, the database is automatically seeded with:
- 25 realistic crisis cases (varied severity, urgency, status)
- 15 volunteers (diverse skills and availability)

This allows immediate exploration of features without manual data entry.

## Production Deployment

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Remember to:
- Change SECRET_KEY
- Set debug=False
- Enable HTTPS
- Setup backups

## Support

See documentation files for detailed information on:
- Database operations
- Code structure
- UI/UX decisions
- Copy guidelines
