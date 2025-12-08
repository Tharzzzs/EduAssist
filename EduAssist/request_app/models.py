from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.text import slugify
from django.contrib.auth.models import User

User = get_user_model()

# ------------------------
# Category Model
# ------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# ------------------------
# CategoryChoice / Query Type Model
# ------------------------
class CategoryChoice(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='choices')
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} - {self.value}"

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    category_choice = models.ForeignKey(CategoryChoice, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='requests', blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Use a string 'Request' if the Request model is in this same file to avoid errors
    related_request = models.ForeignKey('Request', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username}"