# This module tests integrations between projects and systems.
# This is a separate file because the tests cut across modules.

import os
import os.path
import re
from unittest import skip

from django.conf import settings
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.crypto import get_random_string

from siteapp.models import (Organization, Portfolio, Project,
                            ProjectMembership, User)

from controls.oscal import Catalogs, Catalog
from controls.models import *


class ProjectSystemPermissionsUnitTests(TestCase):
    def test_project_system_element_permission_non_admin_user(self):
        """Test non-admin user inviting another non-admin correctly assigns project, system and root_element permissions
           This only tests assignments, does not test experience in interface."""

        # Create non-admin users nau1, nau2
        self.nau1 = User.objects.create(username="non-admin-user-1", email="nau1@example.com")
        self.nau1.clear_password = get_random_string(16)
        self.nau1.set_password(self.nau1.clear_password)
        self.nau1.save()

        self.nau2 = User.objects.create(username="non-admin-user-2", email="nau2@example.com")
        self.nau2.clear_password = get_random_string(16)
        self.nau2.set_password(self.nau2.clear_password)
        self.nau2.save()

        # Login in nau1
        self.client.login(username=self.nau1.username, password=self.nau1.clear_password)

        # nau1 starts a project
        p = Project.objects.create()
        p.save()
        e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        self.assertTrue(e.id is not None)
        self.assertTrue(e.name == "New Element")
        self.assertTrue(e.full_name == "New Element Full Name")
        self.assertTrue(e.element_type == "system")
        s = System(root_element=e)
        s.save()
        p.system = s
        p.save()

        p.assign_edit_permissions(self.nau1)

        # nau2 invites nau2 to the project
        # request.POST.get("user_id")

        send_invitation_data = {'project':p.id,
                                'user_id':self.nau2.id
                                }
        # send POST request.
        # url(r'^invitation/_send$', views.send_invitation, name="send_invitation"),
        response = self.client.post(path='/invitation/_send', data=send_invitation_data)

        print("response", response)
        from pprint import pprint
        print("response.__dict__", pprint(response.__dict__))
        # print("response.message", response.message)

        # Test if nau2 has proper permissions on project, system, root_element
        # e = Element.objects.create(name="New Element", full_name="New Element Full Name", element_type="system")
        # self.assertTrue(e.id is not None)
        # self.assertTrue(e.name == "New Element")
        # self.assertTrue(e.full_name == "New Element Full Name")
        # self.assertTrue(e.element_type == "system")
        # s = System(root_element=e)
        # s.save()
        # self.assertEqual(s.root_element.name,e.name)

        # u2 = User.objects.create(username="Jane2", email="jane@example.com")
        # # Test no permissions for user
        # perms = get_user_perms(u2, s)
        # self.assertTrue(len(perms) == 0)

        # # Assign owner permissions
        # s.assign_owner_permissions(u2)
        # perms = get_user_perms(u2, s)
        # self.assertTrue(len(perms) == 4)
        # self.assertIn('add_system', perms)
        # self.assertIn('change_system', perms)
        # self.assertIn('delete_system', perms)
        # self.assertIn('view_system', perms)

