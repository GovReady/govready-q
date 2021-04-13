from rest_framework import permissions
from rest_framework import serializers
from rest_framework import viewsets
from siteapp.models import Project, User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']
        permission_classes = [permissions.IsAuthenticated]

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        organization_id = serializers.RelatedField(source='organization', read_only=True)
        portfolio_id = serializers.RelatedField(source='portfolio', read_only=True)
        root_task_id = serializers.RelatedField(source='root_task', read_only=True)
        system_id = serializers.RelatedField(source='system', read_only=True)

        model = Project
        fields = ['url', 'organization_id', 'portfolio_id', 'system_id', 'is_organization_project', 'is_account_project', 'root_task_id', 'created', 'updated', 'extra', 'version', 'version_comment']
