from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 🔑 FIX: Re-add the 'role' field with a default value
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        # Add any other roles you need
    ]
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='STUDENT' # <-- Crucial for new profile creation
    )
    
    contact = models.CharField(max_length=15)
    program = models.CharField(max_length=100)
    year_level = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.user.username}'s Profile"