from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # --- Role Choices ---
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('SUPERADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(
        max_length=15, 
        choices=ROLE_CHOICES, 
        default='STUDENT'
    )

    # --- Program Choices ---
    # Moving choices here makes them the "source of truth" for the entire app
    PROGRAM_CHOICES = [
        ('BS Architecture', 'BS Architecture'),
        ('BS Chemical Engineering', 'BS Chemical Engineering'),
        ('BS Civil Engineering', 'BS Civil Engineering'),
        ('BS Computer Engineering', 'BS Computer Engineering'),
        ('BS Computer Science', 'BS Computer Science'),
        ('BS Electrical Engineering', 'BS Electrical Engineering'),
        ('BS Electronics Engineering', 'BS Electronics Engineering'),
        ('BS Industrial Engineering', 'BS Industrial Engineering'),
        ('BS Information Technology', 'BS Information Technology'),
        ('BS Mechanical Engineering with Computational Science', 'BS Mechanical Engineering with Computational Science'),
        ('BS Mechanical Engineering with Mechatronics', 'BS Mechanical Engineering with Mechatronics'),
        ('BS Mining Engineering', 'BS Mining Engineering'),
    ]
    
    # --- Year Level Choices ---
    YEAR_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    # --- Fields ---
    contact = models.CharField(max_length=15)
    
    program = models.CharField(
        max_length=100, 
        choices=PROGRAM_CHOICES, # Link choices here
        blank=True, 
        null=True
    )
    
    year_level = models.CharField(
        max_length=5, 
        choices=YEAR_CHOICES,    # Link choices here
        blank=True, 
        null=True
    )

    # Added these because your HTML template specifically asks for 'bio' and 'address'
    bio = models.TextField(blank=True, null=True, help_text="Short bio about yourself")
    address = models.TextField(blank=True, null=True, help_text="Permanent address")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    # --- Helper Properties ---
    @property
    def is_superadmin(self):
        return self.role == "SUPERADMIN"

    @property
    def is_admin(self):
        return self.role == "ADMIN"

    @property
    def is_student(self):
        return self.role == "STUDENT"