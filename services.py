"""
Business logic layer for ImpactBridge
Separates business logic from routes and database operations
"""

from models import CrisisCase, Volunteer, db


class CrisisService:
    """Service for crisis case operations"""
    
    @staticmethod
    def calculate_priority(severity, people_affected, urgency, available_resources):
        """
        Calculate priority score for a crisis
        
        Formula: (severity × 3) + (people × 2) + (urgency × 4) - (resources × 2)
        
        Args:
            severity: Severity level (1-5)
            people_affected: Number of people affected
            urgency: Urgency level (1-5)
            available_resources: Available resource units
            
        Returns:
            int: Priority score
        """
        return (severity * 3) + (people_affected * 2) + (urgency * 4) - (available_resources * 2)
    
    @staticmethod
    def create_crisis(validated_data):
        """
        Create a new crisis case
        
        Args:
            validated_data: Dictionary of validated crisis data
            
        Returns:
            CrisisCase: Created crisis case
            
        Raises:
            Exception: If database operation fails
        """
        # Calculate priority score
        priority_score = CrisisService.calculate_priority(
            validated_data['severity'],
            validated_data['people_affected'],
            validated_data['urgency'],
            validated_data['available_resources']
        )
        
        # Create crisis case
        case = CrisisCase(
            title=validated_data['title'],
            description=validated_data['description'],
            severity=validated_data['severity'],
            people_affected=validated_data['people_affected'],
            urgency=validated_data['urgency'],
            available_resources=validated_data['available_resources'],
            required_skill=validated_data['required_skill'],
            priority_score=priority_score
        )
        
        db.session.add(case)
        db.session.commit()
        
        return case
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get dashboard statistics
        
        Returns:
            dict: Dashboard statistics
        """
        total_cases = CrisisCase.query.count()
        
        # Efficient query for high priority cases
        high_priority_cases = CrisisCase.query.filter(
            CrisisCase.priority_score >= 20
        ).count()
        
        active_volunteers = Volunteer.query.count()
        
        return {
            'total_cases': total_cases,
            'high_priority_cases': high_priority_cases,
            'active_volunteers': active_volunteers
        }
    
    @staticmethod
    def get_all_cases_sorted():
        """
        Get all crisis cases sorted by priority
        
        Returns:
            list: List of CrisisCase objects sorted by priority (descending)
        """
        return CrisisCase.query.order_by(
            CrisisCase.priority_score.desc(),
            CrisisCase.created_at.desc()
        ).all()
    
    @staticmethod
    def get_case_by_id(case_id):
        """
        Get a crisis case by ID
        
        Args:
            case_id: Crisis case ID
            
        Returns:
            CrisisCase or None
        """
        return CrisisCase.query.get(case_id)


class VolunteerService:
    """Service for volunteer operations"""
    
    @staticmethod
    def register_volunteer(validated_data):
        """
        Register a new volunteer
        
        Args:
            validated_data: Dictionary of validated volunteer data
            
        Returns:
            Volunteer: Created volunteer
            
        Raises:
            Exception: If database operation fails
        """
        volunteer = Volunteer(
            name=validated_data['name'],
            skills=validated_data['skills'],
            availability=validated_data['availability']
        )
        
        db.session.add(volunteer)
        db.session.commit()
        
        return volunteer
    
    @staticmethod
    def get_all_volunteers():
        """
        Get all volunteers sorted by registration date
        
        Returns:
            list: List of Volunteer objects
        """
        return Volunteer.query.order_by(
            Volunteer.registered_at.desc()
        ).all()
    
    @staticmethod
    def get_volunteer_by_id(volunteer_id):
        """
        Get a volunteer by ID
        
        Args:
            volunteer_id: Volunteer ID
            
        Returns:
            Volunteer or None
        """
        return Volunteer.query.get(volunteer_id)
    
    @staticmethod
    def search_by_skill(skill):
        """
        Search volunteers by skill
        
        Args:
            skill: Skill to search for
            
        Returns:
            list: List of matching volunteers
        """
        return Volunteer.query.filter(
            Volunteer.skills.ilike(f'%{skill}%')
        ).all()
