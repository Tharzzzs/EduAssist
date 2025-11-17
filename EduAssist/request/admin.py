from django.contrib import admin
from .models import Category, CategoryChoice, Tag, Request

class CategoryChoiceInline(admin.TabularInline):
    model = CategoryChoice
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryChoiceInline]

@admin.register(CategoryChoice)
class CategoryChoiceAdmin(admin.ModelAdmin):
    list_display = ("value", "category")
    list_filter = ("category",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "priority", "category", "category_choice", "date")
    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description")
