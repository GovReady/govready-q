from api.base.serializers.base import BaseSerializer
from api.siteapp.serializers.users import UserSerializer
from siteapp.models import Project, Organization


class OrganizationSerializer(BaseSerializer):
    help_squad = UserSerializer(many=True)
    reviewers = UserSerializer(many=True)

    class Meta:
        model = Organization
        fields = BaseSerializer.Meta.fields + ['name', 'slug', 'help_squad', 'reviewers', 'extra']


class DetailedProjectSerializer(BaseSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = Project
        fields = BaseSerializer.Meta.fields + ['organization', 'portfolio', 'system', 'is_organization_project',
                                               'is_account_project', 'root_task', 'extra', 'version',
                                               'version_comment', 'tags']
