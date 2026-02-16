"""
Input validation for ImpactBridge
Validates form data before database operations
"""

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class CrisisValidator:
    """Validates crisis case data"""
    
    @staticmethod
    def validate_create(data):
        """
        Validate crisis case creation data
        
        Args:
            data: Dictionary of form data
            
        Returns:
            dict: Validated and cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = []
        
        # Title validation
        title = data.get('title', '').strip()
        if not title:
            errors.append('Situation title is required')
        elif len(title) < 5:
            errors.append('Situation title must be at least 5 characters')
        elif len(title) > 200:
            errors.append('Situation title must not exceed 200 characters')
        
        # Description validation
        description = data.get('description', '').strip()
        if not description:
            errors.append('Situation assessment is required')
        elif len(description) < 20:
            errors.append('Situation assessment must be at least 20 characters')
        elif len(description) > 5000:
            errors.append('Situation assessment must not exceed 5000 characters')
        
        # Severity validation
        try:
            severity = int(data.get('severity', 0))
            if not 1 <= severity <= 5:
                errors.append('Severity must be between 1 and 5')
        except (ValueError, TypeError):
            errors.append('Severity must be a valid number')
            severity = None
        
        # Urgency validation
        try:
            urgency = int(data.get('urgency', 0))
            if not 1 <= urgency <= 5:
                errors.append('Urgency must be between 1 and 5')
        except (ValueError, TypeError):
            errors.append('Urgency must be a valid number')
            urgency = None
        
        # People affected validation
        try:
            people_affected = int(data.get('people_affected', 0))
            if people_affected < 0:
                errors.append('Population impact cannot be negative')
            elif people_affected > 10000000:  # 10 million cap
                errors.append('Population impact exceeds maximum value')
        except (ValueError, TypeError):
            errors.append('Population impact must be a valid number')
            people_affected = None
        
        # Available resources validation
        try:
            available_resources = int(data.get('available_resources', 0))
            if available_resources < 0:
                errors.append('Current resources cannot be negative')
            elif available_resources > 1000000:  # 1 million cap
                errors.append('Current resources exceeds maximum value')
        except (ValueError, TypeError):
            errors.append('Current resources must be a valid number')
            available_resources = None
        
        # Required skill validation
        required_skill = data.get('required_skill', '').strip()
        if not required_skill:
            errors.append('Critical expertise is required')
        elif len(required_skill) < 3:
            errors.append('Critical expertise must be at least 3 characters')
        elif len(required_skill) > 100:
            errors.append('Critical expertise must not exceed 100 characters')
        
        # If there are errors, raise exception
        if errors:
            raise ValidationError('; '.join(errors))
        
        # Return validated data
        return {
            'title': title,
            'description': description,
            'severity': severity,
            'urgency': urgency,
            'people_affected': people_affected,
            'available_resources': available_resources,
            'required_skill': required_skill
        }


class VolunteerValidator:
    """Validates volunteer data"""
    
    VALID_AVAILABILITY = ['Full-time', 'Part-time', 'Weekends', 'On-call']
    
    @staticmethod
    def validate_register(data):
        """
        Validate volunteer registration data
        
        Args:
            data: Dictionary of form data
            
        Returns:
            dict: Validated and cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = []
        
        # Name validation
        name = data.get('name', '').strip()
        if not name:
            errors.append('Full name is required')
        elif len(name) < 2:
            errors.append('Full name must be at least 2 characters')
        elif len(name) > 100:
            errors.append('Full name must not exceed 100 characters')
        
        # Skills validation
        skills = data.get('skills', '').strip()
        if not skills:
            errors.append('Professional expertise is required')
        elif len(skills) < 3:
            errors.append('Professional expertise must be at least 3 characters')
        elif len(skills) > 200:
            errors.append('Professional expertise must not exceed 200 characters')
        
        # Availability validation
        availability = data.get('availability', '').strip()
        if not availability:
            errors.append('Deployment capacity is required')
        elif availability not in VolunteerValidator.VALID_AVAILABILITY:
            errors.append(f'Deployment capacity must be one of: {", ".join(VolunteerValidator.VALID_AVAILABILITY)}')
        
        # If there are errors, raise exception
        if errors:
            raise ValidationError('; '.join(errors))
        
        # Return validated data
        return {
            'name': name,
            'skills': skills,
            'availability': availability
        }
