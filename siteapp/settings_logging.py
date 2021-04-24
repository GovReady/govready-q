import sys

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main': {
            'format': '[%(asctime)s] <%(module)s.py %(levelname)s> %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'core': {
            'format': '[%(asctime)s][Duration:%(run_time)s][Status Code:%(status_code)s][User:%(user)s] %(request_method)s %(request_path)s ReqBody:[%(request_body)s]',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        "json": {
            '()': 'json_log_formatter.JSONFormatter',
        }
    },

    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'log_to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'main',
        },
        'core_handler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'core',
        },
        'json_handler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'json',
        }
    },
    'loggers': {
        # '': {
        #     'handlers': ['core_handler'],
        #     'level': 'DEBUG',
        #     'propagate': True
        # },
        'main': {
            'handlers': ['log_to_stdout'],
            'level': 'DEBUG',
        },
        'core': {
            'handlers': ['core_handler'],
            'level': 'DEBUG',
        },
        'core_json': {
            'handlers': ['json_handler'],
            'level': 'DEBUG',
        },
        'nplusone': {
            'handlers': ['console'],
            'level': 'WARN',
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['dev'],
        # },
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
