"""
ImpactBridge - Crisis Coordination Platform
Refactored with proper architecture, validation, and error handling
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from logging.handlers import RotatingFileHandler
import os

from models import db, CrisisCase, Volunteer
from config import get_config
from validators import CrisisValidator, VolunteerValidator, ValidationError
from services import CrisisService, VolunteerService


def create_app(config_name=None):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created')
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for errors
        file_handler = RotatingFileHandler(
            'logs/impactbridge.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('ImpactBridge startup')


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        app.logger.warning(f'Validation error: {error}')
        flash(str(error), 'error')
        return redirect(request.referrer or url_for('index'))
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        app.logger.warning(f'404 error: {request.url}')
        flash('Page not found', 'error')
        return redirect(url_for('index'))
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Internal error: {error}')
        db.session.rollback()
        flash('An internal error occurred. Please try again.', 'error')
        return redirect(url_for('index'))
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions"""
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        db.session.rollback()
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))


def register_routes(app):
    """Register application routes"""
    
    @app.route('/')
    def index():
        """Dashboard showing overview statistics"""
        try:
            stats = CrisisService.get_dashboard_stats()
            return render_template('index.html', **stats)
        except Exception as e:
            app.logger.error(f'Error loading dashboard: {e}')
            flash('Error loading dashboard statistics', 'error')
            return render_template('index.html', 
                                 total_cases=0,
                                 high_priority_cases=0,
                                 active_volunteers=0)
    
    @app.route('/cases')
    def cases():
        """Display all crisis cases sorted by priority"""
        try:
            sorted_cases = CrisisService.get_all_cases_sorted()
            return render_template('cases.html', cases=sorted_cases)
        except Exception as e:
            app.logger.error(f'Error loading cases: {e}')
            flash('Error loading crisis cases', 'error')
            return render_template('cases.html', cases=[])
    
    @app.route('/cases/new', methods=['GET', 'POST'])
    def new_case():
        """Create a new crisis case"""
        if request.method == 'POST':
            try:
                # Validate input
                validated_data = CrisisValidator.validate_create(request.form)
                
                # Create crisis case
                case = CrisisService.create_crisis(validated_data)
                
                app.logger.info(f'Crisis case created: {case.id} - {case.title}')
                flash('Crisis report filed and prioritized', 'success')
                return redirect(url_for('cases'))
                
            except ValidationError as e:
                # Validation errors are handled by error handler
                raise
            except Exception as e:
                app.logger.error(f'Error creating crisis case: {e}')
                db.session.rollback()
                flash('Error creating crisis report. Please try again.', 'error')
        
        return render_template('new_case.html')
    
    @app.route('/volunteers')
    def volunteers():
        """Display all registered volunteers"""
        try:
            all_volunteers = VolunteerService.get_all_volunteers()
            return render_template('volunteers.html', volunteers=all_volunteers)
        except Exception as e:
            app.logger.error(f'Error loading volunteers: {e}')
            flash('Error loading personnel', 'error')
            return render_template('volunteers.html', volunteers=[])
    
    @app.route('/volunteers/register', methods=['GET', 'POST'])
    def register_volunteer():
        """Register a new volunteer"""
        if request.method == 'POST':
            try:
                # Validate input
                validated_data = VolunteerValidator.validate_register(request.form)
                
                # Register volunteer
                volunteer = VolunteerService.register_volunteer(validated_data)
                
                app.logger.info(f'Volunteer registered: {volunteer.id} - {volunteer.name}')
                flash('Personnel registered and ready for deployment', 'success')
                return redirect(url_for('volunteers'))
                
            except ValidationError as e:
                # Validation errors are handled by error handler
                raise
            except Exception as e:
                app.logger.error(f'Error registering volunteer: {e}')
                db.session.rollback()
                flash('Error registering personnel. Please try again.', 'error')
        
        return render_template('register_volunteer.html')


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
