from django.contrib import admin

import django.contrib.auth.admin as contribauthadmin

from .models import User

def all_user_fields_still_exist(fieldlist):
    for f in fieldlist:
        try:
            User._meta.get_field(f)
        except:
            return False
    return True

class UserAdmin(contribauthadmin.UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'id', 'date_joined') # base has first_name, etc. fields that we don't have on our model
    fieldsets = [
        (None, {'fields': ('email', 'password')}),
    ] + [fs for fs in contribauthadmin.UserAdmin.fieldsets if all_user_fields_still_exist(fs[1]['fields'])]

    pass

admin.site.register(User, UserAdmin)
