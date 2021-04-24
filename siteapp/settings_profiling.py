from .settings import *


if DEBUG and not TESTING_MODE:
    MIDDLEWARE = [
        'querycount.middleware.QueryCountMiddleware',
        'nplusone.ext.django.NPlusOneMiddleware'
    ] + MIDDLEWARE

    INSTALLED_APPS += [
        'nplusone.ext.django'
    ]

    import logging

    NPLUSONE_LOGGER = logging.getLogger('nplusone')
    NPLUSONE_LOG_LEVEL = logging.WARN

    QUERYCOUNT = {
        'THRESHOLDS': {
            'MEDIUM': 50,
            'HIGH': 200,
            'MIN_TIME_TO_LOG': 0,
            'MIN_QUERY_COUNT_TO_LOG': 0
        },
        'IGNORE_REQUEST_PATTERNS': [r'^/livereload'],
        'IGNORE_SQL_PATTERNS': [],
        'DISPLAY_DUPLICATES': True,
        'RESPONSE_HEADER': 'X-DjangoQueryCount-Count'
    }
