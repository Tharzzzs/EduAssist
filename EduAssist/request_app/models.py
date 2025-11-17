from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

# ------------------------
# Static Categories
# ------------------------
CATEGORY_CHOICES = [
    ('Academic', 'Academic'),
    ('Course Material', 'Course Material'),
    ('Grades', 'Grades'),
    ('Assignments', 'Assignments'),
    ('Exam Schedule', 'Exam Schedule'),
    ('Finance', 'Finance'),
    ('Tuition Fee', 'Tuition Fee'),
    ('Scholarship', 'Scholarship'),
    ('Refund', 'Refund'),
    ('Technical', 'Technical'),
    ('Login Issue', 'Login Issue'),
    ('Software Installation', 'Software Installation'),
    ('Wi-Fi / Network Issue', 'Wi-Fi / Network Issue'),
    ('Administrative', 'Administrative'),
    ('ID Card', 'ID Card'),
    ('Room Allocation', 'Room Allocation'),
    ('Library Access', 'Library Access'),
]

# ------------------------
# Tag Model
# ------------------------
class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(regex='^[A-Za-z0-9-]+$', message='Tags can only contain letters, numbers, and hyphens.')]
    )
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# ------------------------
# Request Model
# ------------------------
class Request(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('cancelled', 'Cancelled')]
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()
    attachment = models.FileField(upload_to='request_attachments/%Y/%m/%d/', blank=True, null=True)

    # Fixed category field
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Academic',
        blank=False,
        null=False
    )

    tags = models.ManyToManyField(Tag, related_name='requests', blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
