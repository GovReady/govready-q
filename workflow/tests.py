from django.test import TestCase

from guidedmodules.tests import TestCaseWithFixtureData
from siteapp.models import (Organization, Portfolio, Project,
                            ProjectMembership, User)
from controls.models import System, Element
from .models import WorkflowImage, WorkflowInstanceSet, WorkflowInstance, WorkflowRecipe
from .factories import FlowImageFactory, FlowImage
import os

# Create your tests here.

class WorkflowUnitTests(TestCase):

    def setUp(self):
        # def true, false to make json and python dict equivalent
        true = True
        false = False
        # create WorkflowImage
        wfimage = WorkflowImage.objects.create(name="Monthly POAM Review")
        wfimage.workflow = {
          "name": "Monthly POAM Review",
          "type": "flow_image",
          "uuid": "5d777289-906a-4b72-8fad-89077e5a15e5",
          "status": "red",
          "complete": false,
          "feature_order": ["start_review", "review_poams", "submit_review"],
          "curr_feature": "start_review",
          "features": {
            "start_review": {
              "id": "start_review",
              "cmd": "STEP",
              "text": "Start Monthly Review",
              "props": [
                {
                  "id": "system.url"
                },
                {
                  "type": "str"
                }
              ],
              "complete": false,
              "status": "not-started",
              "skip": false,
              "feature_descriptor": ""
            },
            "review_poams": {
              "id": "review_poams",
              "cmd": "STEP",
              "text": "Review POAMs",
              "props": [
                {
                  "id": "system.data"
                },
                {
                  "type": "text"
                }
              ],
              "complete": false,
              "status": "not-started",
              "skip": false,
              "feature_descriptor": ""
            },
            "submit_review": {
              "id": "submit_review",
              "cmd": "STEP",
              "text": "Submit updated POAMs",
              "props": [
                {
                  "id": "system.name"
                },
                {
                  "type": "str"
                }
              ],
              "complete": false,
              "status": "not-started",
              "skip": false,
              "feature_descriptor": ""
            }
          }
        }
        wfimage.save()

        # create 2 Users
        self.u1 = u1 = User.objects.create(username="Jane1", email="jane1@example.com")
        self.u2 = u2 = User.objects.create(username="Jane2", email="jane2@example.com")
        self.u3 = u3 = User.objects.create(username="Jane3", email="jane3@example.com")

        # create 2 Systems
        sre1 = Element.objects.create(name="New Element 1", full_name="New Element Full Name 1", element_type="system")
        s1   = System.objects.create(root_element=sre1)
        sre2 = Element.objects.create(name="New Element 2", full_name="New Element Full Name 2", element_type="system")
        s2   = System.objects.create(root_element=sre2)
        sre3 = Element.objects.create(name="New Element 3", full_name="New Element Full Name 3", element_type="system")
        s3   = System.objects.create(root_element=sre3)

        # assign owner permissions
        s1.assign_owner_permissions(u1)
        s2.assign_owner_permissions(u2)
        s3.assign_owner_permissions(u3)

    def test_workflowimage_attributes(self):
        """WorkflowImage attributes working"""

        wfimage = WorkflowImage.objects.first()
        self.assertEqual(wfimage.name, "Monthly POAM Review")
        self.assertEqual(len(wfimage.workflow['features']), 3)
    
    def test_workflowimage_methods(self):
        """WorkflowImage methods working"""

        wfimage = WorkflowImage.objects.first()
        wfimage.create_system_worflowinstances("ALL", name="August Monthly POAM Review")

        wfinstancesets = WorkflowInstanceSet.objects.all()
        self.assertEqual(len(wfinstancesets), 1)
        wfinstanceset = wfinstancesets[0]
        self.assertEqual(wfinstanceset.name, "August Monthly POAM Review")
        self.assertEqual(wfinstanceset.description, f'Set created from {wfinstanceset.name}')

        wfinstances = WorkflowInstance.objects.all()
        self.assertEqual(len(wfinstances), 3)
        wfinstance = wfinstances[0]
        self.assertEqual(wfinstance.name, "August Monthly POAM Review")
        self.assertEqual(len(wfinstance.workflow['features']), 3)
        
    def test_workflowinstance_methods(self):

        wfimage = WorkflowImage.objects.first()
        self.assertEqual(wfimage.name, "Monthly POAM Review")
        self.assertEqual(len(wfimage.workflow['features']), 3)

        wfimage = WorkflowImage.objects.first()
        wfimage.create_system_worflowinstances("ALL", name="August Monthly POAM Review")

        wfinstances = WorkflowInstance.objects.all()
        self.assertEqual(len(wfinstances), 3)
        wfinstance = wfinstances[0]

        # test advance()
        # curr_feature = wfinstance.workflow['curr_feature']
        self.assertEqual(wfinstance.workflow['curr_feature'], "start_review")
        wfinstance.advance_feature()
        wfinstance.save()
        self.assertEqual(wfinstance.workflow['curr_feature'], "review_poams")

        # check if advance saved to database
        uuid = wfinstance.uuid
        wfinstance_copy = WorkflowInstance.objects.get(uuid=uuid)
        self.assertEqual(wfinstance_copy.workflow['curr_feature'], "review_poams")

    def test_flowimagefactory(self):
        """Test factories"""
        
        # create workflow recipe
        name = "Monthly POAM Reviewx"
        description  = "Simple test recipe for monthly review of POAMs"
        # recipe_text_simple = """STEP Start Monthly Reviewx id(Start)
        # STEP Review Monthly POAMsx id(Review)
        # STEP Submit updated POAMsx id(Submit)
        # rule: Hide small org internal SOC question +viewque:(org.internal_soc, False) -SETANSX:(org.internal_soc, some value) id(rule1)
        # rule: Do something else +viewque:(org.internal_soc, False) -SETANSX:(org.internal_soc, some value) id(rule2)
        # """
        recipe_text = """<step prompt="Start Monthly Reviewx" id="Start">
        <step prompt="Review Monthly POAMsx" id="Review">
        <step prompt="Submit updated POAMsx" id="Submit">
        <rule comment="Hide small org internal SOC question" test="1 == 1" true="viewque(org.internal_soc, False)" id="rule1">
        <rule comment="Do something else" test="1 == 1" true="viewque=(org.internal_soc, False)" id="rule2">
        """
        wfr = WorkflowRecipe.objects.create(name=name, description=description,recipe=recipe_text)

        fac_name = "Monthly POAM Review 2"
        fif = FlowImageFactory(fac_name)
        # fif.feature_descriptor_text = wfr.recipe
        # fif.split_feature_descriptor_text()
        # fif.prepare_features()
        workflowimage = fif.update_or_create_workflowimage_from_flowtext(recipe_text)
        print(f'[DEBUG] created workflowimage: ', workflowimage)
        self.assertEqual(len(workflowimage.workflow['features']), 3)
        
        # test retrieving flowimage
        # flow_image_filename = f"{fi1.flow_image['name']}__{fi1.flow_image['uuid']}.fim"
        # data_dir = os.path.join(f"{os.getcwd()}", 'data')
        # filepath = os.path.join(data_dir, flow_image_filename)
        wfi2 = WorkflowImage.objects.get(name=fac_name)
        print(f'[DEBUG] retrieved workflowimage: ', wfi2.name)
        self.assertEqual(wfi2.workflow['name'], fac_name)
        self.assertEqual(len(wfi2.workflow['features']), 3)
        self.assertEqual(wfi2.workflow['feature_order'], ['Start', 'Review', 'Submit'])

        # test parsing of rules
        self.assertEqual(len(wfi2.rules['features']), 2)
        self.assertEqual(wfi2.rules['features']['rule2']['params']['comment'], 'Do something else')
        # test rule order
        self.assertEqual(len(wfi2.rules['rule_order']), 2)
        self.assertEqual(wfi2.rules['rule_order'][1], 'rule2')

        # test marking step complete
        # create workflowinstance
        wfinst2 = wfi2.create_orphan_worflowinstance()
        # Need a user
        user = self.u2
        wfinst2.set_curr_feature_completed(user)
        # wfinst2.save() - # saving causes a raise TypeError(f'Object of type {o.__class__.__name__} 'TypeError: Object of type DeferredAttribute is not JSON serializable

        wfinst3 = wfinst2.rule_proc_rules()
        wfinst2.advance_feature(self.u2)
        self.assertEqual(wfinst3.workflow['curr_feature'], wfinst3.workflow['feature_order'][1])

        # test rule_proc_rules appear in log
        log_event_names = [log_event['name'] for log_event in wfinst3.log]
        print("log_event_names:", log_event_names)
        self.assertIn('rule_proc_rules', log_event_names)


# Scratch code

# wfin = WorkflowInstance.objects.first()
# wfin.workflow['q_plan'][wfin.workflow['cur_prompt_key']]

# wfin.workflow['cur_prompt_key']

# from dotwiz import DotWiz
# dw = DotWiz(wfin.workflow)
# dw.q_plan.cur_prompt_key

