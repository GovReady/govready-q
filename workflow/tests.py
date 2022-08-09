from django.test import TestCase

# Create your tests here.


# Scratch code

wfin = WorkflowInstance.objects.first()
wfin.workflow['q_plan'][wfin.workflow['cur_prompt_key']]

wfin.workflow['cur_prompt_key']

from dotwiz import DotWiz
dw = DotWiz(wfin.workflow)
dw.q_plan.cur_prompt_key

