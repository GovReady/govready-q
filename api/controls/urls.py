from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter
from api.controls.views.element import ElementViewSet
from api.controls.views.system import SystemViewSet, SystemControlsViewSet, SystemAssessmentViewSet, SystemPoamViewSet

router = routers.DefaultRouter()
router.register(r'elements', ElementViewSet)
router.register(r'systems', SystemViewSet)

systems_router = NestedSimpleRouter(router, r'systems', lookup='systems')
systems_router.register(r'controls', SystemControlsViewSet, basename='systems-controls')
systems_router.register(r'assessments', SystemAssessmentViewSet, basename='systems-assessments')
systems_router.register(r'poams', SystemPoamViewSet, basename='systems-poams')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(systems_router.urls))
]
