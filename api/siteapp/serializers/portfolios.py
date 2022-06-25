from api.base.serializers.types import ReadOnlySerializer
from siteapp.models import Portfolio


class SimplePortfolioSerializer(ReadOnlySerializer):

    class Meta:
        model = Portfolio
        fields = ['title', 'description']

