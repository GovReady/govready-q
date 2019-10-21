from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

import re

# from .models import Module, ModuleQuestion, Task, TaskAnswer, TaskAnswerHistory, InstrumentationEvent

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the itsystems index.")
