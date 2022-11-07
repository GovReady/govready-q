from api.siteapp.serializers.projects import DetailedProjectsSerializer
from django.db import transaction
from siteapp.models import Project, ProjectMembership
from controls.models import Element, System, Statement, Deployment

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

