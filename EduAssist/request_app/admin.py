from django.contrib import admin
from .models import Tag, Request, Notification  # <--- Added Notification here

# ------------------------
# Tag Admin
# ------------------------
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}  # automatically populate slug from name

# ------------------------
# Request Admin
# ------------------------
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "priority", "category", "date")
    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description", "category")
    ordering = ("-date",)
    filter_horizontal = ("tags",)  # optional, for easier tag selection in admin

# ------------------------
# Notification Admin
# ------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")