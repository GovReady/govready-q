import json
import time

import logging

from django.conf import settings

logger = logging.getLogger('core')
json_logger = logging.getLogger('core_json')


class LoggingMiddleware:
    LOG_BODY_METHODS = ['POST', 'PUT', 'PATCH']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in self.LOG_BODY_METHODS:
            request.req_body = request.body
        request.start_time = time.time()
        response = self.get_response(request)

        log_data = self.extract_log_info(request=request,
                                         response=response)
        logger.info(msg='REQUEST', extra=log_data)
        if not settings.DEBUG:
            json_logger.info(msg='REQUEST', extra=log_data)

        return response

    def get_body(self, request):
        if request.content_type == 'application/x-www-form-urlencoded':
            fields = request.body.decode('utf-8', 'ignore').strip().split('&')
            data = {}
            for field in fields:
                key, value = field.split('=')
                data[key] = value
            return data
        elif hasattr(request, request.method):
            try:
                return json.loads(request.body)
            except Exception:
                return request.body.decode('utf-8', 'ignore').strip()
        return request.body.decode('utf-8', 'ignore').strip()

    def extract_log_info(self, request, response=None, exception=None):
        """Extract appropriate log info from requests/responses/exceptions."""
        log_data = {
            'remote_address': request.META['REMOTE_ADDR'],
            'request_method': request.method,
            'request_path': request.get_full_path(),
            'user': request.user.id if hasattr(request, 'user') else None,
            'status_code': response.status_code,
            'run_time': '%.3f' % (time.time() - request.start_time),
            'request_body': ''
        }
        if request.method in self.LOG_BODY_METHODS:
            log_data['request_body'] = self.get_body(request)
        return log_data
