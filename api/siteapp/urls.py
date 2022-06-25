from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from api.siteapp.views.organizations import OrganizationViewSet
from api.siteapp.views.portfolios import PortfolioViewSet
from api.siteapp.views.projects import ProjectViewSet
from api.siteapp.views.support import SupportViewSet
from api.siteapp.views.tags import TagViewSet
from api.siteapp.views.users import UsersViewSet
from api.siteapp.views.role import RoleViewSet
from api.siteapp.views.party import PartyViewSet
from api.siteapp.views.appointment import AppointmentViewSet
from api.siteapp.views.request import RequestViewSet
from api.siteapp.views.proposal import ProposalViewSet

router = routers.DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'portfolios', PortfolioViewSet)
router.register(r'support', SupportViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', UsersViewSet)

router.register(r'roles', RoleViewSet)
router.register(r'parties', PartyViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'proposals', ProposalViewSet)

project_router = NestedSimpleRouter(router, r'projects', lookup='projects')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(project_router.urls)),
]
