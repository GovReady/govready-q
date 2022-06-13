from rest_framework.relations import PrimaryKeyRelatedField

from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from api.controls.serializers.system import SimpleSystemSerializer
from api.guidedmodules.serializers.tasks import DetailedTaskSerializer, SimpleTaskSerializer, TaskSerializer
from api.siteapp.serializers.assets import AssetMixinSerializer
from api.siteapp.serializers.organizations import DetailedOrganizationSerializer
from api.siteapp.serializers.portfolios import SimplePortfolioSerializer
from api.siteapp.serializers.tags import SimpleTagSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from siteapp.models import Project, ProjectMembership, ProjectAsset, Tag


class SimpleProjectsSerializer(ReadOnlySerializer):
    class Meta:
        model = Project
        fields = ['is_account_project', 'is_deletable', 'extra', 'version', 'version_comment']


class DetailedProjectsSerializer(SimpleProjectsSerializer):
    organization = DetailedOrganizationSerializer()
    portfolio = SimplePortfolioSerializer()
    tags = SimpleTagSerializer(many=True)
    # system = SimpleSystemSerializer()
    root_task = TaskSerializer()

    class Meta:
        model = Project
        fields = SimpleProjectsSerializer.Meta.fields + ['organization', 'portfolio', 'tags', 'root_task']


class SimpleProjectMembershipSerializer(ReadOnlySerializer):
    class Meta:
        model = ProjectMembership
        fields = ['is_admin']


class DetailedProjectMembershipSerializer(ReadOnlySerializer):
    project = DetailedProjectsSerializer()
    user = SimpleUserSerializer()

    class Meta:
        model = ProjectMembership
        fields = SimpleProjectsSerializer.Meta.fields + ['project', 'user']


class DetailedProjectAssetSerializer(AssetMixinSerializer):
    project = DetailedProjectsSerializer()

    class Meta:
        model = ProjectAsset
        fields = AssetMixinSerializer.Meta.fields + ['project', 'default']


class WriteProjectTagsSerializer(WriteOnlySerializer):
    tag_ids = PrimaryKeyRelatedField(source='tags', many=True, queryset=Tag.objects)

    class Meta:
        model = Project
        fields = ['tag_ids']
