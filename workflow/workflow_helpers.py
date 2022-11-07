from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import WorkflowImage, WorkflowInstanceSet, WorkflowInstance
from control.models import System
from siteapp.models import Project, Organization



