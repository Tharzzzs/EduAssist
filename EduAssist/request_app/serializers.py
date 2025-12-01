from rest_framework import serializers
from .models import Tag, Request, Category

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class RequestSerializer(serializers.ModelSerializer):
    # Use Category model dynamically instead of static choices
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
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
