from rest_framework import serializers

from api.base.serializers.types import ReadOnlySerializer
from api.siteapp.serializers.portfolios import SimplePortfolioSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from siteapp.models import Invitation


class SimpleInvitationSerializer(ReadOnlySerializer):
    class Meta:
        model = Invitation
        fields = ['into_project', 'target_object_id', 'extra', 'target_info', 'to_email', 'text', 'sent_at',
                  'accepted_at', 'revoked_at', 'email_invitation_code', 'extra']


class DetailedInvitationSerializer(SimpleInvitationSerializer):
    from_user = SimpleUserSerializer()
    from_project = serializers.SerializerMethodField()  # Circular Dependency

    from_portfolio = SimplePortfolioSerializer()
    # target_content_type # todo
    # target # todo
    to_user = SimpleUserSerializer()
    accepted_user = SimpleUserSerializer()

    def get_from_project(self, obj):
        from api.siteapp.serializers.projects import DetailedProjectsSerializer
        return DetailedProjectsSerializer(obj)

    class Meta:
        model = Invitation
        fields = SimpleInvitationSerializer.Meta.fields + ['from_user', 'from_project', 'from_portfolio',
                                                           'target_content_type', 'target', 'to_user', 'accepted_user']
