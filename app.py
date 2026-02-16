"""
ImpactBridge - Crisis Coordination Platform
Simple SQLite-based application for managing crisis cases and volunteers
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'impactbridge.db')


# ============================================================================
# DATABASE SETUP AND CONNECTION
# ============================================================================

def get_db_connection():
    """
    Create a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_database():
    """
    Initialize the database with required tables.
    Creates tables if they don't exist.
    
    Schema:
    -------
    cases table:
        - id: Primary key (auto-increment)
        - title: Crisis title (TEXT)
        - description: Detailed description (TEXT)
        - severity: Severity level 1-5 (INTEGER)
        - people_affected: Number of people affected (INTEGER)
        - urgency: Urgency level 1-5 (INTEGER)
        - available_resources: Current resource units (INTEGER)
        - required_skill: Required expertise (TEXT)
        - priority_score: Calculated priority (INTEGER)
        - status: Case status - Pending/Active/Completed (TEXT)
        - created_at: Timestamp (TEXT)
    
    volunteers table:
        - id: Primary key (auto-increment)
        - name: Volunteer name (TEXT)
        - skills: Comma-separated skills (TEXT)
        - availability: Available for deployment (INTEGER: 0=No, 1=Yes)
        - registered_at: Timestamp (TEXT)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity INTEGER NOT NULL CHECK(severity >= 1 AND severity <= 5),
            people_affected INTEGER NOT NULL CHECK(people_affected >= 0),
            urgency INTEGER NOT NULL CHECK(urgency >= 1 AND urgency <= 5),
            available_resources INTEGER NOT NULL CHECK(available_resources >= 0),
            required_skill TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create volunteers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT NOT NULL,
            availability INTEGER NOT NULL DEFAULT 1,
            registered_at TEXT NOT NULL
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_priority_score 
        ON cases(priority_score DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_status 
        ON cases(status)
    ''')
    
    conn.commit()
    conn.close()


def seed_database():
    """
    Seed the database with realistic sample data.
    Only runs if the cases table is empty (prevents duplicate inserts).
    
    Inserts:
        - 25 realistic crisis cases with varied parameters
        - 15 volunteers with diverse skills and availability
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if database is already seeded
    case_count = cursor.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
    
    if case_count > 0:
        print('Database already seeded. Skipping seed data insertion.')
        conn.close()
        return
    
    print('Seeding database with sample data...')
    
    # Seed crisis cases
    crisis_cases = [
        # High severity, high urgency cases
        ('Severe Flooding in District 7', 'Heavy rainfall caused river overflow affecting residential areas. Immediate evacuation needed. Water levels rising rapidly.', 5, 850, 5, 12, 'Emergency Medicine, Rescue Operations', 'Active'),
        ('Building Collapse - Downtown', 'Multi-story residential building collapsed. Multiple casualties reported. Search and rescue operations underway.', 5, 120, 5, 8, 'Structural Engineering, Emergency Medicine', 'Active'),
        ('Wildfire Approaching Settlement', 'Forest fire spreading rapidly toward populated area. Evacuation orders issued. Air quality hazardous.', 5, 2400, 5, 15, 'Firefighting, Logistics', 'Active'),
        ('Mass Food Poisoning Event', 'Contaminated water supply affecting entire neighborhood. Hospital capacity exceeded. Urgent medical intervention required.', 4, 450, 5, 6, 'Emergency Medicine, Public Health', 'Active'),
        ('Chemical Plant Leak', 'Toxic gas leak from industrial facility. Evacuation zone established. Decontamination protocols activated.', 5, 680, 5, 10, 'Hazmat Response, Emergency Medicine', 'Active'),
        
        # Medium-high severity cases
        ('Earthquake Aftershock Zone', 'Multiple aftershocks following major earthquake. Infrastructure damage assessment ongoing. Shelter needs critical.', 4, 1200, 4, 18, 'Structural Engineering, Logistics', 'Active'),
        ('Refugee Camp Overcrowding', 'Sudden influx of displaced persons. Sanitation facilities inadequate. Disease outbreak risk high.', 4, 3500, 4, 25, 'Public Health, Logistics', 'Pending'),
        ('Bridge Infrastructure Failure', 'Major bridge showing structural weakness. Traffic rerouted. Inspection and repair urgent to prevent collapse.', 4, 0, 4, 8, 'Structural Engineering, Civil Engineering', 'Active'),
        ('Hospital Power Outage', 'Main hospital lost power during storm. Backup generators failing. Patient care compromised.', 4, 280, 5, 5, 'Electrical Engineering, Emergency Medicine', 'Completed'),
        ('Landslide Road Blockage', 'Major highway blocked by landslide. Communities isolated. Supply routes cut off.', 3, 950, 4, 12, 'Civil Engineering, Logistics', 'Active'),
        
        # Medium severity cases
        ('Water Supply Contamination', 'Municipal water system contaminated. Boil water advisory issued. Alternative water sources needed.', 3, 5200, 3, 20, 'Public Health, Water Engineering', 'Pending'),
        ('School Building Damage', 'Elementary school damaged in storm. 400 students displaced. Temporary facilities needed urgently.', 3, 400, 3, 15, 'Civil Engineering, Education Coordination', 'Completed'),
        ('Elderly Care Facility Evacuation', 'Nursing home requires evacuation due to structural concerns. 85 residents need relocation and medical support.', 3, 85, 4, 10, 'Emergency Medicine, Logistics', 'Active'),
        ('Agricultural Pest Outbreak', 'Locust swarm destroying crops. Food security threatened. Immediate intervention required.', 3, 8000, 3, 8, 'Agriculture, Logistics', 'Pending'),
        ('Telecommunications Outage', 'Cell tower damage affecting emergency communications. Repair crews mobilizing.', 2, 15000, 3, 25, 'Telecommunications, Electrical Engineering', 'Completed'),
        
        # Lower severity but significant cases
        ('Community Center Flood Damage', 'Local community center flooded. Serves as emergency shelter. Repairs needed before next storm.', 2, 0, 2, 18, 'Civil Engineering, Construction', 'Pending'),
        ('Medical Supply Shortage', 'Regional hospital running low on critical medications. Supply chain disruption.', 3, 1200, 3, 12, 'Supply Chain, Medical Logistics', 'Completed'),
        ('Temporary Housing Setup', 'Need to establish temporary housing for displaced families. Site preparation required.', 2, 320, 2, 22, 'Logistics, Construction', 'Pending'),
        ('Food Distribution Coordination', 'Organizing food distribution for affected neighborhoods. Volunteers and logistics support needed.', 2, 2800, 2, 35, 'Logistics, Supply Chain', 'Active'),
        ('Psychological Support Services', 'Trauma counseling needed for disaster survivors. Mental health resources deployment.', 2, 650, 2, 15, 'Mental Health, Social Services', 'Completed'),
        
        # Lower priority cases
        ('Infrastructure Assessment', 'Post-disaster infrastructure survey needed. Non-urgent but important for recovery planning.', 2, 0, 1, 40, 'Civil Engineering, Urban Planning', 'Pending'),
        ('Community Recovery Planning', 'Long-term recovery strategy development. Stakeholder meetings and resource allocation.', 1, 4500, 1, 45, 'Urban Planning, Community Development', 'Completed'),
        ('Debris Removal Operations', 'Clearing debris from residential areas. Coordinating heavy equipment and disposal.', 2, 1800, 2, 30, 'Logistics, Heavy Equipment Operation', 'Active'),
        ('Utility Restoration Coordination', 'Coordinating power and water restoration efforts. Multiple utility companies involved.', 2, 3200, 2, 28, 'Electrical Engineering, Project Management', 'Completed'),
        ('Volunteer Coordination Hub', 'Establishing central coordination point for volunteer activities. Training and deployment logistics.', 1, 0, 1, 50, 'Project Management, Communications', 'Completed'),
    ]
    
    # Insert crisis cases with calculated priority scores
    for title, description, severity, people_affected, urgency, resources, skill, status in crisis_cases:
        priority_score = calculate_priority(severity, people_affected, urgency, resources)
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO cases (
                title, description, severity, people_affected, urgency,
                available_resources, required_skill, priority_score, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, severity, people_affected, urgency,
              resources, skill, priority_score, status, created_at))
    
    print(f'✓ Inserted {len(crisis_cases)} crisis cases')
    
    # Seed volunteers
    volunteers = [
        ('Dr. Sarah Chen', 'Emergency Medicine, Trauma Care, Triage', 1),
        ('Marcus Rodriguez', 'Structural Engineering, Building Assessment, Safety Inspection', 1),
        ('Emily Thompson', 'Public Health, Epidemiology, Disease Prevention', 1),
        ('James Wilson', 'Logistics, Supply Chain Management, Distribution', 1),
        ('Dr. Aisha Patel', 'Emergency Medicine, Pediatrics, Field Surgery', 1),
        ('David Kim', 'Civil Engineering, Infrastructure, Water Systems', 1),
        ('Rachel Foster', 'Mental Health, Trauma Counseling, Crisis Intervention', 1),
        ('Carlos Mendez', 'Firefighting, Rescue Operations, Hazmat Response', 1),
        ('Dr. Lisa Anderson', 'Public Health, Sanitation, Water Quality', 0),  # Unavailable
        ('Michael Chang', 'Telecommunications, Network Engineering, Emergency Communications', 1),
        ('Jennifer Brooks', 'Project Management, Coordination, Resource Allocation', 1),
        ('Ahmed Hassan', 'Heavy Equipment Operation, Construction, Debris Removal', 1),
        ('Dr. Rebecca Martinez', 'Emergency Medicine, Disaster Response, Field Operations', 1),
        ('Thomas O\'Brien', 'Electrical Engineering, Power Systems, Generator Maintenance', 0),  # Unavailable
        ('Sophia Nguyen', 'Social Services, Community Outreach, Volunteer Coordination', 1),
    ]
    
    # Insert volunteers
    for name, skills, availability in volunteers:
        registered_at = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO volunteers (name, skills, availability, registered_at)
            VALUES (?, ?, ?, ?)
        ''', (name, skills, availability, registered_at))
    
    print(f'✓ Inserted {len(volunteers)} volunteers')
    
    conn.commit()
    conn.close()
    
    print('✓ Database seeding completed successfully!')
    print(f'  - Total cases: {len(crisis_cases)}')
    print(f'  - Active cases: {sum(1 for c in crisis_cases if c[7] == "Active")}')
    print(f'  - Pending cases: {sum(1 for c in crisis_cases if c[7] == "Pending")}')
    print(f'  - Completed cases: {sum(1 for c in crisis_cases if c[7] == "Completed")}')
    print(f'  - Available volunteers: {sum(1 for v in volunteers if v[2] == 1)}')
    print(f'  - Unavailable volunteers: {sum(1 for v in volunteers if v[2] == 0)}')
    
    # Calculate and display metrics
    completed = sum(1 for c in crisis_cases if c[7] == "Completed")
    resolution_rate = round((completed / len(crisis_cases)) * 100, 1)
    print(f'  - Resolution rate: {resolution_rate}%')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_priority(severity, people_affected, urgency, available_resources):
    """
    Calculate priority score for a crisis case.
    
    Formula: (severity × 3) + (people_affected × 2) + (urgency × 4) - (resources × 2)
    
    Higher scores indicate higher priority.
    
    Args:
        severity (int): Severity level (1-5)
        people_affected (int): Number of people affected
        urgency (int): Urgency level (1-5)
        available_resources (int): Available resource units
    
    Returns:
        int: Calculated priority score
    """
    return (severity * 3) + (people_affected * 2) + (urgency * 4) - (available_resources * 2)


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Dashboard showing overview statistics.
    
    Displays:
        - Total number of cases
        - Number of high priority cases (priority >= 20)
        - Number of active volunteers (availability = 1)
        - Resolution rate (percentage of completed cases)
        - Volunteer utilization (percentage of volunteers deployed)
    """
    conn = get_db_connection()
    
    # Get total cases
    total_cases = conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
    
    # Get high priority cases (priority_score >= 20)
    high_priority_cases = conn.execute(
        'SELECT COUNT(*) FROM cases WHERE priority_score >= 20'
    ).fetchone()[0]
    
    # Get active volunteers (availability = 1)
    active_volunteers = conn.execute(
        'SELECT COUNT(*) FROM volunteers WHERE availability = 1'
    ).fetchone()[0]
    
    # Calculate resolution rate (completed cases / total cases * 100)
    completed_cases = conn.execute(
        "SELECT COUNT(*) FROM cases WHERE status = 'Completed'"
    ).fetchone()[0]
    
    resolution_rate = 0
    if total_cases > 0:
        resolution_rate = round((completed_cases / total_cases) * 100, 1)
    
    # Calculate volunteer utilization
    # For demo purposes: Active cases / Available volunteers * 100
    # (Assumes each active case needs ~1 volunteer)
    active_cases = conn.execute(
        "SELECT COUNT(*) FROM cases WHERE status = 'Active'"
    ).fetchone()[0]
    
    volunteer_utilization = 0
    if active_volunteers > 0:
        volunteer_utilization = round((active_cases / active_volunteers) * 100, 1)
        # Cap at 100% for display purposes
        if volunteer_utilization > 100:
            volunteer_utilization = 100
    
    conn.close()
    
    return render_template('index.html',
                         total_cases=total_cases,
                         high_priority_cases=high_priority_cases,
                         active_volunteers=active_volunteers,
                         resolution_rate=resolution_rate,
                         volunteer_utilization=volunteer_utilization)


@app.route('/cases')
def cases():
    """
    Display all crisis cases sorted by priority (highest first).
    
    Returns cases with all fields including calculated priority score.
    """
    conn = get_db_connection()
    
    # Get all cases ordered by priority score (descending)
    cases = conn.execute('''
        SELECT * FROM cases 
        ORDER BY priority_score DESC, created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('cases.html', cases=cases)


@app.route('/cases/new', methods=['GET', 'POST'])
def new_case():
    """
    Create a new crisis case.
    
    GET: Display the crisis report form
    POST: Process form data and create new case
    
    Form fields:
        - title: Crisis title
        - description: Detailed situation assessment
        - severity: Severity level (1-5)
        - urgency: Urgency level (1-5)
        - people_affected: Number of people affected
        - available_resources: Current resource units
        - required_skill: Required expertise
    """
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        description = request.form['description']
        severity = int(request.form['severity'])
        people_affected = int(request.form['people_affected'])
        urgency = int(request.form['urgency'])
        available_resources = int(request.form['available_resources'])
        required_skill = request.form['required_skill']
        
        # Calculate priority score
        priority_score = calculate_priority(
            severity, people_affected, urgency, available_resources
        )
        
        # Get current timestamp
        created_at = datetime.utcnow().isoformat()
        
        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO cases (
                title, description, severity, people_affected, 
                urgency, available_resources, required_skill, 
                priority_score, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, severity, people_affected, 
              urgency, available_resources, required_skill, 
              priority_score, 'Pending', created_at))
        
        conn.commit()
        conn.close()
        
        flash('Crisis report filed and prioritized', 'success')
        return redirect(url_for('cases'))
    
    return render_template('new_case.html')


@app.route('/volunteers')
def volunteers():
    """
    Display all registered volunteers.
    
    Shows volunteers ordered by registration date (newest first).
    """
    conn = get_db_connection()
    
    # Get all volunteers ordered by registration date
    volunteers = conn.execute('''
        SELECT * FROM volunteers 
        ORDER BY registered_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('volunteers.html', volunteers=volunteers)


@app.route('/volunteers/register', methods=['GET', 'POST'])
def register_volunteer():
    """
    Register a new volunteer.
    
    GET: Display the registration form
    POST: Process form data and register volunteer
    
    Form fields:
        - name: Volunteer name
        - skills: Comma-separated skills
        - availability: Deployment capacity (stored as text, converted to boolean)
    """
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        skills = request.form['skills']
        availability_text = request.form['availability']
        
        # Convert availability to boolean (1 = available, 0 = not available)
        # All deployment types are considered available
        availability = 1
        
        # Get current timestamp
        registered_at = datetime.utcnow().isoformat()
        
        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO volunteers (name, skills, availability, registered_at)
            VALUES (?, ?, ?, ?)
        ''', (name, skills, availability, registered_at))
        
        conn.commit()
        conn.close()
        
        flash('Personnel registered and ready for deployment', 'success')
        return redirect(url_for('volunteers'))
    
    return render_template('register_volunteer.html')


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

if __name__ == '__main__':
    # Initialize database tables on startup
    init_database()
    print(f'Database initialized at: {DATABASE_PATH}')
    
    # Seed database with sample data (only runs once)
    seed_database()
    
    # Run the application
    app.run(debug=True)
