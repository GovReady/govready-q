from api.base.serializers.types import ReadOnlySerializer
from api.controls.serializers.system import DetailedSystemSerializer
from api.guidedmodules.serializers.tasks import DetailedTaskSerializer
from api.siteapp.serializers.assets import AssetMixinSerializer
from api.siteapp.serializers.organizations import DetailedOrganizationSerializer
from api.siteapp.serializers.portfolios import SimplePortfolioSerializer
from api.siteapp.serializers.tags import TagSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from siteapp.models import Project, ProjectMembership, ProjectAsset


class SimpleProjectsSerializer(ReadOnlySerializer):
    class Meta:
        model = Project
        fields = ['is_account_project', 'is_account_project', 'extra', 'version', 'version_comment']


class DetailedProjectsSerializer(SimpleProjectsSerializer):
    organization = DetailedOrganizationSerializer()
    portfolio = SimplePortfolioSerializer()
    tags = TagSerializer(many=True)
    system = DetailedSystemSerializer()
    root_task = DetailedTaskSerializer()

    class Meta:
        model = Project
        fields = SimpleProjectsSerializer.Meta.fields + ['organization', 'portfolio',  'system', 'root_task', 'tags']


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
