from server.models import Projects, UserProfiles, Skills, Types, Swipes
from server.serializers import UsersSerializer, ProjectsSerializer, UserProfilesSerializer, TypesSerializer, SkillsSerializer, SwipesSerializer, ProjectMatchSerializer

from django.http import Http404
from django.db.models import Count
from django.contrib.auth.models import User

from rest_framework import generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from datetime import date

'''
    Lists all users that a project's required skills category matches. The more relevant skills the user has, 
    the user is prioritized in the list
'''
class UserSearch(APIView):
    authentication_classes = (TokenAuthentication,) # Use token for authentication
    permission_classes = (IsAuthenticated,) # Only authenticated users may view the list of other users
    
    def getProject(self, pk): # Helper function for get; handles error checking
        try:
            return Projects.objects.get(pk = pk)
        except Projects.DoesNotExist:
            raise Http404

    def get(self, request, pk, format = None):
        project = self.getProject(pk) # Get the project using its primary key
        skills = Skills.objects.filter(projects = project.id) # All skills related to the project
        skillsList = [skill.id for skill in skills] # Make a list containing skill ids of all skills related to the project 
        
        # If no preferred skills are specified on the requesting project, return all users
        if not skillsList:
            userProfiles = UserProfiles.objects.all()
            serializer = UserProfilesSerializer(userProfiles, many = True) 
            return Response(serializer.data)
         
        skills_users = Skills.user_profiles.through # skills / users pivot table
        
        # Get the userprofiles_ids which have the skills required by the project in the skills_users table 
        users = skills_users.objects.filter(skills_id__in = skillsList).values('userprofiles_id')
        userProfile_ids = users.annotate(count = Count('userprofiles_id')).order_by('-count') # Order by the count of userprofiles_ids in descending order
        user_list = [userProfile_id['userprofiles_id'] for userProfile_id in userProfile_ids] # Put the ids into a list
        userProfiles = UserProfiles.objects.filter(pk__in = user_list) # Get those users' user profiles
        userProfiles_list = list(userProfiles) # Make a user profiles list
        userProfiles_list.sort(key = lambda profile: user_list.index(profile.id)) # Sort the user profiles list in the order that user-list is sorted
        
        userProfilesSerializer = UserProfilesSerializer(userProfiles_list, many = True, context = {'request': request}) # Deserialize the data
        return Response(userProfilesSerializer.data) # Return the response with data

'''
    Returns a list of all projects the requesting user might be interested in based on their preference Types
    stored in the database
'''
class ProjectSearch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format = None):
        profile = UserProfiles.objects.get(user_id = request.user.id) # Obtain UserProfile from the requesting User's id 
        types_profiles = Types.user_profiles.through # The types_profiles pivot table
        preferredTypes = types_profiles.objects.filter(userprofiles_id = profile.id) # Obtain all Types preferred by the requesting user
        preferredTypes = [x.types_id for x in preferredTypes] # Put into a list of IDs of preferred types
        
        # If user did not specify a preferred type, return all projects
        if not preferredTypes:
            projects = Projects.objects.all()
            serializer = ProjectsSerializer(projects, many = True)
            return Response(serializer.data)
        
        types_projects = Types.projects.through # Types_projects pivot table
        rawResults = types_projects.objects.filter(types_id__in=preferredTypes).values('projects_id') # All projects that match preferred types (with duplicate projects)
        projectIDs = rawResults.annotate(count=Count('projects_id')).order_by('-count') # Get the IDs of the projects in descending order of most "Type" matches
        projectIDs = [x['projects_id'] for x in projectIDs] # Put the IDs into a flat list
        projects = Projects.objects.filter(pk__in = projectIDs) # Get the actual project instances from the IDs
        projects_list = list(projects) # Turn queryset into a list
        projects_list.sort(key = lambda project: projectIDs.index(project.id)) #Sort projects back to proper order based on projectIDs
        
        # Deserialize the data and return it
        serializer = ProjectsSerializer(projects_list, many=True, context={'request': request})
        return Response(serializer.data)

'''
    Creates and retrieves a project
'''
class ProjectList(generics.GenericAPIView, mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    
    # Override the perform_create function to automatically set the project's owner as the requesting user 
    def perform_create(self, serializer):
        serializer.save(owner = UserProfiles.objects.get(user_id = self.request.user.id))
    
    # Retrieves all projects a user owns
    def get(self, request, *args, **kwargs):
        profile = UserProfiles.objects.get(user_id = request.user.id) # Get the requesting user's profile
        projects = Projects.objects.filter(owner_id = profile.id) # get projects owned by the requesting user
        serializer = ProjectsSerializer(projects, many = True, context = {'request': request}) # deserialize the data
        return Response(serializer.data) # return the requested data
    
    # Creates a new Project with the specified fields
    def post(self, request, *args, **kwargs ):
        request.data['date_created'] = date.today() # Set the date_created field as today's date
        skillsList = request.data.getlist('skills') # Get a list of all skills associated with this project

        # Check if skills exist in database, create them if they don't. Check for errors after
        if check_skills(skillsList) == False: 
            return Response( status=status.HTTP_400_BAD_REQUEST ) #TODO: Change to correct code + MORE SPECIFIC DETAILS FOR CLIENT '''
    
        return self.create(request, *args, **kwargs ) # Use CreateModelMixin to create the Project

'''
    Update, Retrieve or Delete an existing project specified by its primary key 
'''
class ProjectDetail(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer

    # Update data for a specific Project
    def put(self, request, *args, **kwargs): 
        skillsList = request.data.getlist('skills') #Get a list of all skills associated with this project

        #Check if skills exist in database, create them if they don't. Check for errors after
        if check_skills(skillsList) == False: 
            return Response( status=status.HTTP_400_BAD_REQUEST ) #TODO: Change to correct code + MORE SPECIFIC DETAILS FOR CLIENT '''

        return self.update(request, *args, **kwargs )
    
    # Get data for a specific project
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    # Delete a specific project
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

'''
    Checks if a list of Skills exist in the database and create them if they don't
    @param skillsList - list of skills 
    @postcondition - Return true if skills either all exist OR were successfully created. False if an error occurs when creating a skill
'''
def check_skills(skillsList): 
    for skill in skillsList: 
        try:
            Skills.objects.get(skill_name=skill) # Check if this skill exists in database
        except Skills.DoesNotExist:
            skillData = {}
            skillData['skill_name'] = skill # Format the skill as a dictionary to pass to SkillsSerializer
            serializer = SkillsSerializer(data=skillData)
            if serializer.is_valid(): 
                serializer.save() # Save newly created skill to database
            else:
                return False # Data was invalid 
    return True # all skills either creatd or already exist

'''
    Returns all projects matched with the requesting user
'''
@api_view(['GET'])
def project_matches(request):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    profile = UserProfiles.objects.get(user = request.user) # Get the requesting user's profile
    matched_swipes = Swipes.objects.filter(user_profile=profile, user_likes=Swipes.YES, project_likes=Swipes.YES) # Get all swipes that user is involved in with mutual likes
    serializer = ProjectMatchSerializer(matched_swipes, many=True, context = {'request': request})
    return Response(serializer.data)

'''
    Returns all users matched with the requesting project owner
'''
@api_view(['GET'])
def user_matches(request):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    profile = UserProfiles.objects.get(user = request.user) # Get the requesting user's profile
    projects = Projects.objects.filter(owner = profile) # Get the projects owned by this user
    projectsList = [project.id for project in projects] # Put the project ids into a list
    matched_swipes = Swipes.objects.filter(project_id__in = projectsList, user_likes = Swipes.YES, project_likes = Swipes.YES) # Query the swipes which contain the projects in the project list
    serializer = UserMatchSerializer(matched_swipes, many = True, context = {'request': request}) # Deserialize and return the data
    return Response(serializer.data)

'''
    Makes a new user and user profile in the database
'''
@api_view(['POST'])
def user_list(request):
    serializer = UsersSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.get(username = request.data.get('username'))
    requestData = request.data.copy() # Make a mutable copy of the request
    requestData['user'] = user.id # Set the user field to requesting user
    
    skillsList = request.data.getlist('skills') # Get a list of all skills associated with this user
    if not check_skills(skillsList): 
        return Response(status = status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfilesSerializer(data = requestData)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

'''
    Modifies or deletes a user
'''
class UserDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Modifies the profile of the requesting user
    def put(self, request, format = None):
        profile = UserProfiles.objects.get(user_id = request.user.id)
        requestData = request.data.copy() # Make a mutable copy of the request
        requestData['user'] = profile.user_id # Set the user field to requesting user

        skillsList = request.data.getlist('skills') # Get a list of all skills associated with this user
        if not check_skills(skillsList): 
            return Response(status = status.HTTP_400_BAD_REQUEST)

        serializer = UserProfilesSerializer(profile, data = requestData)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    # Deletes a user and the corresponding user profile
    def delete(self, request, format = None):
        user = User.objects.get(id = request.user.id) # Get the instance of the requesting user and the user profile
        profile = UserProfiles.objects.get(user_id = user.id)
        user.delete() # Delete both the user and the user profile
        profile.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
