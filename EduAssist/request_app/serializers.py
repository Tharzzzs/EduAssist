# request/serializers.py
from rest_framework import serializers
from .models import Tag, Request, CATEGORY_CHOICES

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class RequestSerializer(serializers.ModelSerializer):
    # category is now a CharField with static choices
    category = serializers.ChoiceField(choices=[c[0] for c in CATEGORY_CHOICES], required=False, allow_null=True)
    
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
            'category', 'category_choice', 'tags', 'attachment', 'date', 'updated_at'
        ]
        read_only_fields = ['date', 'updated_at', 'user']
