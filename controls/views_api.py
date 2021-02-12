from itertools import groupby
import logging
from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models.functions import Lower
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, \
    HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views import View
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError as SchemaValidationError
from urllib.parse import quote
from siteapp.models import Project, User
from .forms import *
from .models import *
from .utilities import *

logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


@csrf_exempt
def manage_system_assessment_result_api(request, system_id, sar_id=None, methods=['GET', 'POST']):
    """Create or edit system assessment result"""
    #
    # Example curl POST to api
    #  curl --header "Authorization: <api_key>" \
    #  -F "name=test_sar_api" \
    #  -F "system_id=86" \
    #  -F "deployment_id=23" \
    #  -F "data=@controls/data/test_data/test_sar1.json" \
    #  localhost:8000/api/v1/systems/86/assessment/new
    #

    from collections import OrderedDict

    # Get user from API key.
    api_key = request.META.get("HTTP_AUTHORIZATION", "").strip()
    if len(api_key) < 32: # prevent null values from matching against users without api keys
        return JsonResponse(OrderedDict([("status", "error"), ("error", "An API key was not present in the Authorization header.")]), json_dumps_params={ "indent": 2 }, status=403)
    # Check API key permissions and get user
    from django.db.models import Q
    # from siteapp.models import User, Project
    try:
        user = User.objects.get(Q(api_key_rw=api_key)|Q(api_key_ro=api_key)|Q(api_key_wo=api_key))
    except User.DoesNotExist:
        return JsonResponse(OrderedDict([("status", "error"), ("error", "A valid API key was not present in the Authorization header.")]), json_dumps_params={ "indent": 2 }, status=403)

    # TODO
    # - Data validation - Can I reintegrate with form
    # - write tests
    # - does a sar with this id already exist? Update existing sar
    # - Maybe create a blank sar then upload to that ID: create sar, get sar_id, post to that sar_id
    # - should we post with UUID? match with name?
    # - sari = get_object_or_404(SystemAssessmentResult, pk=sar_id) if sar_id else None
    if request.method == 'POST':
        sar = SystemAssessmentResult(
                name=request.POST.get('name'),
                system_id=request.POST.get('system_id'),
                deployment_id=request.POST.get('deployment_id'),
                assessment_results=json.loads(request.FILES.get('data').read().decode("utf8", "replace"))
            )
        # Need to check of person has access to post to system?
        # Can user view this system?
        system = System.objects.get(id=request.POST.get('system_id'))
        # if not request.user.has_perm('view_system', system):
        #     # User does not have permission to this system
        #     raise Http404
        sar.save()
        # messages.add_message(request, messages.INFO, f'System assessment result "{sar.name}" created.')
        logger.info(
            event="create_system_assessment_result",
            object={"object": "system_assessment_result", "id": sar.id, "name":sar.name},
            # user={"id": request.user.id, "username": request.user.username}
        )

        # form = SystemAssessmentResultForm(request.POST, instance=sari)
        # if form.is_valid():
        #     form.save()
        #     sar = form.instance
        #     # Create message to display to user
        #     if sari:
        #         messages.add_message(request, messages.INFO, f'System assessment result "{sar.name}" edited.')
        #         logger.info(
        #             event="edit_system_assessment_result",
        #             object={"object": "system_assessment_result", "id": sar.id, "name":sar.name},
        #             user={"id": request.user.id, "username": request.user.username}
        #         )
        #     else:
        #         messages.add_message(request, messages.INFO, f'System assessment result "{sar.name}" created.')
        #         logger.info(
        #             event="create_system_assessment_result",
        #             object={"object": "system_assessment_result", "id": sar.id, "name":sar.name},
        #             user={"id": request.user.id, "username": request.user.username}
        #         )
        #     return redirect('system_assessment_results_list', system_id=system_id)
    else:
        if sari is None:
            sari = SystemAssessmentResult(system_id=system_id)
        form = SystemAssessmentResultForm(instance=sari)

    # Send simple response
    # TODO: Improve the response
    ok = True
    return JsonResponse(OrderedDict([
        ("status", "ok" if ok else "error"),
        # ("details", log),
    ]), json_dumps_params={ "indent": 2 })

