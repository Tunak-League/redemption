from server.models import Projects, UserProfiles, Skills, Types
from server.serializers import ProjectsSerializer, UserProfilesSerializer, TypesSerializer, SkillsSerializer

from django.http import Http404
from django.db.models import Count

from rest_framework import generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from datetime import date

class UserSearch(APIView):
    authentication_classes = (TokenAuthentication,) # Use token for authentication
    permission_classes = (IsAuthenticated,) # Only authenticated users may view the list of other users
    
    def getProject(self, pk): # Helper function for get; handles error checking
        try:
            return Projects.objects.get(pk = pk)
        except Projects.DoesNotExist:
            raise Http404
    '''
        Lists all users that a project's required skills category matches. The more relevant skills the user has, 
        the user is prioritized in the list
    '''
    def get(self, request, pk, format = None):
        project = self.getProject(pk) # Get the project using its primary key
        skills = Skills.objects.filter(projects = project.id) # All skills related to the project
        skillsList = [skill.id for skill in skills] # Make a list containing skill ids of all skills related to the project 
        skills_users = Skills.user_profiles.through # skills / users pivot table

        # Get the userprofiles_ids which have the skills required by the project in the skills_users table 
        users = skills_users.objects.filter(skills_id__in = skillsList).values('userprofiles_id')
        userProfile_ids = users.annotate(count = Count('userprofiles_id')).order_by('-count') # order by the count of userprofiles_ids in descending order
        user_list = [userProfile_id['userprofiles_id'] for userProfile_id in userProfile_ids] # Put the ids into a list
        userProfiles = UserProfiles.objects.filter(pk__in = user_list) # get those users' user profiles
        userProfiles_list = list(userProfiles) # Make a user profiles list
        userProfiles_list.sort(key = lambda profile: user_list.index(profile.id)) # Sort the user profiles list in the order that user-list is sorted
        
        userProfilesSerializer = UserProfilesSerializer(userProfiles_list, many = True, context = {'request': request}) # serialize the data
        return Response(userProfilesSerializer.data) # Return the response

class ProjectSearch(APIView):
    '''
        Returns a list of all projects the requesting user might be interested in based on their preference Types
        stored in the database
    '''
    #Set authentication and permission classes so only authorized users can request for projects
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        profile = UserProfiles.objects.get(user_id=request.user.id) #obtain UserProfile from the requesting User's id 
        types_profiles = Types.user_profiles.through #the types_profiles pivot table
        preferredTypes = types_profiles.objects.filter( userprofiles_id= profile.id ) #obtain all Types preferred by the requesting user
        preferredTypes = [x.types_id for x in preferredTypes] #list of IDs of preferred types

        types_projects = Types.projects.through #the types_projects pivot table
        rawResults = types_projects.objects.filter(types_id__in=preferredTypes).values('projects_id') #All projects that match preferred types (with duplicate projects)
        projectIDs = rawResults.annotate(count=Count('projects_id')).order_by('-count') #Get the IDs of the projects in descending order of most "Type" matches
        projectIDs = [x['projects_id'] for x in projectIDs] #Put the IDs into a flat list
        projects = Projects.objects.filter(pk__in=projectIDs) #Get the actual project instances from the IDs
        projects_list = list(projects) #turn queryset into a list
        projects_list.sort(key=lambda project: projectIDs.index(project.id)) #Sort projects back to proper order based on projectIDs

        #Serialize the data and return it
        serializer = ProjectsSerializer(projects_list, many=True, context={'request': request})
        return Response( serializer.data )



class ProjectList(generics.GenericAPIView, mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner = UserProfiles.objects.get(user_id = self.request.user.id))
    
    def get(self, request, *args, **kwargs):
        profile = UserProfiles.objects.get(user_id = request.user.id)
        projects = Projects.objects.filter(owner_id = profile.id)
        serializer = ProjectsSerializer(projects, many = True, context = {'request': request})
        return Response(serializer.data)

    #Creates a new Project with the specified fields
    def post(self, request, *args, **kwargs ):
        request.data['date_created'] = date.today()
        skillsList = request.data.getlist('skills') #Get a list of all skills associated with this project

        #Check if skills exist in database, create them if they don't. Check for errors after
        if check_skills(skillsList) == False: 
            return Response( status=status.HTTP_400_BAD_REQUEST ) #TODO: Change to correct code + MORE SPECIFIC DETAILS FOR CLIENT '''
        
        return self.create(request, *args, **kwargs ) #Use CreateModelMixin to create the Project

class ProjectDetail(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer

    #Update data for a specific Project
    def put( self, request, *args, **kwargs ): 
        skillsList = request.data.getlist('skills') #Get a list of all skills associated with this project

        #Check if skills exist in database, create them if they don't. Check for errors after
        if check_skills(skillsList) == False: 
            return Response( status=status.HTTP_400_BAD_REQUEST ) #TODO: Change to correct code + MORE SPECIFIC DETAILS FOR CLIENT '''

        return self.update(request, *args, **kwargs )
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

'''
    Helper function to check if a list of Skills exist in the database and create them if they don't
    @param skillsList - list of skills 
    @postcondition - Return true if skills either all exist OR were successfully created. False if an error occurs when creating a skill
'''
def check_skills( skillsList ): 
    for skill in skillsList: 
        try:
            Skills.objects.get(skill_name=skill) #Check if this skill exists in database
        except Skills.DoesNotExist:
            skillData = {}
            skillData['skill_name'] = skill #Format the skill as a dictionary to pass to SkillsSerializer
            serializer = SkillsSerializer( data=skillData )
            if( serializer.is_valid() ): 
                serializer.save() #Save newly created skill to database
            else:
                return False #Data was invalid 
    return True #all skills either creatd or already exist
