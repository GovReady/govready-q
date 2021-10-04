from api.base.serializers.types import ReadOnlySerializer
from api.siteapp.serializers.organizations import DetailedOrganizationSerializer
from api.siteapp.serializers.projects import DetailedProjectsSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from siteapp.models import Folder


class SimpleFolderSerializer(ReadOnlySerializer):

    class Meta:
        model = Folder
        fields = ['title', 'description', 'extra']


class DetailedFolderSerializer(SimpleFolderSerializer):

    organization = DetailedOrganizationSerializer()
    admin_users = SimpleUserSerializer(many=True)
    projects = DetailedProjectsSerializer(many=True)

    class Meta:
        model = Folder
        fields = SimpleFolderSerializer.Meta.fields + ['organization', 'admin_users', 'projects']
