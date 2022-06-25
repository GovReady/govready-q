from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadOnlyViewSet
from api.siteapp.serializers.portfolios import SimplePortfolioSerializer
from siteapp.models import Portfolio


class PortfolioViewSet(ReadOnlyViewSet):
    queryset = Portfolio.objects.all()
    serializer_classes = SerializerClasses(retrieve=SimplePortfolioSerializer,
                                           list=SimplePortfolioSerializer)
