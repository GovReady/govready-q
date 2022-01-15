import functools
import logging
import operator
import pathlib
import shutil
import tempfile
from collections import defaultdict
from datetime import datetime
from itertools import groupby
from pathlib import PurePath
from urllib.parse import quote, urlunparse
from uuid import uuid4

import rtyaml
import trestle.oscal.component as trestlecomponent
import trestle.oscal.ssp as trestlessp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, \
    HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views import View
from django.views.generic import ListView
from django.urls import reverse
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError as SchemaValidationError
from urllib.parse import quote

from api.siteapp.serializers.tags import SimpleTagSerializer
from guidedmodules.models import Task, Module, AppVersion, AppSource
from siteapp.model_mixins.tags import TagView
from simple_history.utils import update_change_reason

from siteapp.models import Project, Organization, Tag
from siteapp.settings import GOVREADY_URL
from system_settings.models import SystemSettings

logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

# Create your views here.

def index(request):
    """Index page for controls"""

    # Get catalog
    # catalog = Catalog()

    context = {
        # "catalog": catalog,
        "data": None,
    }
    return render(request, "nlp/index.html", context)

