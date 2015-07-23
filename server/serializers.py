from django.forms import widgets
from rest_framework import serializers
from server.models import UserProfiles, Skills, Types, Projects
from django.contrib.auth.models import User

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'user_permissions')

class UserProfilesSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField (
        many = True,
        read_only = True,
        slug_field = 'skill_name',
    )
    class Meta:
        model = UserProfiles
        fields = ('id', 'user_summary', 'location', 'image_path', 'skills')

class SkillsSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many = True, read_only=True)
    projects = serializers.PrimaryKeyRelatedField(many = True, read_only=True)
    class Meta:
        model = Skills
        fields = ('id', 'skill_name', 'users', 'projects')

class TypesSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many = True, read_only=True)
    class Meta:
        model = Types
        fields = ('id', 'type_name', 'users')

class ProjectsSerializer(serializers.ModelSerializer):
    types = serializers.SlugRelatedField(
        many = True,
        queryset = Projects.types,
        slug_field = 'type_name',
    )
    class Meta:
        model = Projects
        fields = ('id', 'project_name', 'project_summary', 'owner', 'date_created', 'image_path','types')

