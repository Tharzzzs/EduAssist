# request/serializers.py - Create this new file
from rest_framework import serializers
from .models import Category, Tag, Request

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class RequestSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=False,
        allow_null=True
    )
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name',
        required=False
    )

    class Meta:
        model = Request
        fields = [
            'id', 'title', 'description', 'status', 'priority', 
            'category', 'tags', 'attachment', 'date', 'updated_at'
        ]
        read_only_fields = ['date', 'updated_at', 'user']