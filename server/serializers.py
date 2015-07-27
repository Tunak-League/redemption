from django.forms import widgets
from rest_framework import serializers
from server.models import UserProfiles, Skills, Types, Projects, Swipes
from django.contrib.auth.models import User

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'user_permissions')

class UserProfilesSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField (
        many = True,
        queryset = Skills.objects.all(),
        slug_field = 'skill_name',
    )
    types = serializers.SlugRelatedField (
        many = True,
        queryset = Types.objects.all(),
        slug_field = 'type_name'
    )
    last_name = serializers.ReadOnlyField(source = 'user.last_name')
    first_name= serializers.ReadOnlyField(source = 'user.first_name')
    email = serializers.ReadOnlyField(source = 'user.email')
    username = serializers.ReadOnlyField(source = 'user.username')
    class Meta:
        model = UserProfiles
        fields = ('id', 'last_name', 'first_name', 'email', 'username', 'user_summary', 'location', 'image_path', 'skills', 'types', 'user')

class SkillsSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many = True, read_only = True)
    projects = serializers.PrimaryKeyRelatedField(many = True, read_only = True)
    class Meta:
        model = Skills
        fields = ('id', 'skill_name', 'users', 'projects')

class TypesSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many = True, read_only = True)
    class Meta:
        model = Types
        fields = ('id', 'type_name', 'users')

class ProjectsSerializer(serializers.ModelSerializer):
    types = serializers.SlugRelatedField (
        many = True,
        queryset = Types.objects.all(),
        slug_field = 'type_name',
    )
    skills = serializers.SlugRelatedField (
        many = True,
        queryset = Skills.objects.all(),
        slug_field = 'skill_name',
    )
    owner_name = serializers.ReadOnlyField( source='owner.user.username' )
    class Meta:
        model = Projects
        fields = ('id', 'project_name', 'project_summary', 'owner', 'date_created', 'image_path','types', 'skills', 'owner_name')
        read_only_fields = ('owner',)

class SwipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Swipes
        fields = ('id', 'user_profile', 'project', 'user_likes', 'project_likes')

class ProjectMatchSerializer( serializers.ModelSerializer ):
    project_name = serializers.ReadOnlyField( source='project.project_name' )
    owner = serializers.ReadOnlyField( source='project.owner.user.username')
    class Meta:
        model = Swipes
        fields = ('project', 'project_name', 'owner' ) 

class UserMatchSerializer( serializers.ModelSerializer ):
    username = serializers.ReadOnlyField( source='user_profile.user.username' )
    project_name = serializers.ReadOnlyField(source='project.project_name')
    class Meta:
        model = Swipes
        fields = ('user_profile', 'username', 'project_name' )
