import datetime
from system_settings.models import Sitename
from django.conf import settings

def get_theme(request):
    """Retrieve site theme from database"""
    if Sitename.objects.exists():
        sn = Sitename.objects.first()
        if sn.theme in settings.THEME_DIRS:
            theme = f"{sn.theme}/"
        else:
            print(f"Theme '{sn.theme}' not found in available themes {settings.THEME_DIRS}.")
            theme = ""
    else:
        theme = ""
    return {
        'theme': theme
    }

def get_current_year_to_context(request):
    current_datetime = datetime.datetime.now()
    return {
        'current_year': current_datetime.year
    }