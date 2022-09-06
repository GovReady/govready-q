import random
import os
import re
import json
import uuid

class ActionFunc():
    """Base class for Action Functions"""
    
    def __init__(self, func_params, workflow):
        self.params = func_params
        self.workflow = workflow
        
    def parse_params(self):
        """Parse function params"""
        # Each subclass should define
        pass
    
    def update_workflow(self):
        pass
    
    # def log_exception(self, func_name):
    #     """Log an exception"""
    #     pass

        return exception


class SETANSX(ActionFunc):
    
    def __init__(self, func_params, workflow):
        super().__init__(func_params, workflow)
        self.parse_params()

    def parse_params(self):
        """Parse function params"""

        # Rule validated so we know params pattern for function
        self.ans, self.val = self.params.split(',')
        self.ans = self.ans.strip()
        self.val = self.val.strip()
        
    def update_workflow(self):
        """Do action"""
        
        # Update workflow
        print("PROCESSING SETANS")
        try:
            if self.val.startswith("'") or self.val.startswith('"'):
                # literal
                ans_val = self.val.strip("'").strip('"')
            else:
                # reference
                ans_val = self.workflow[self.val]['ans']
            self.workflow[self.ans]['ans'] = ans_val
        except:
            print(f"[ERROR] SETANS problem with {self.ans}")
            # self.log_exception('SETANS')
        
        # Return updated workflow
        return self.workflow

    # def log_exception(self, func_name):
    #     """Log an exception"""
    #     if 'exceptions' not in self.workflow.keys():
    #         self.workflow['exceptions'] = []
    #         self.workflow['exceptions'].append({'func': func_name})


class SETANS(ActionFunc):
    
    def __init__(self, func_params, workflow):
        super().__init__(func_params, workflow)
        self.parse_params()

    def parse_params(self):
        """Parse function params"""

        # Rule validated so we know params pattern for function
        self.ans, self.val = self.params.split(',')
        self.ans = self.ans.strip()
        self.val = self.val.strip()
        
    def update_workflow(self):
        """Do action"""
        
        # Update workflow
        print("PROCESSING SETANS")
        try:
            if self.val.startswith("'") or self.val.startswith('"'):
                # literal
                ans_val = self.val.strip("'").strip('"')
            else:
                # reference
                ans_val = self.workflow[self.val]['ans']
            self.workflow[self.ans]['ans'] = ans_val
        except:
            print(f"[ERROR] SETANS problem with {self.ans}")
            # self.log_exception('SETANS')
        
        # Return updated workflow
        return self.workflow

    # def log_exception(self, func_name):
    #     """Log an exception"""
    #     if 'exceptions' not in self.workflow.keys():
    #         self.workflow['exceptions'] = []
    #         self.workflow['exceptions'].append({'func': func_name})


class VIEWQUE(ActionFunc):
    
    def __init__(self, func_params, workflow):
        super().__init__(func_params, workflow)
        self.parse_params()
    
    def parse_params(self):
        """Parse function params"""

        # Rule validated so we know params pattern for function
        self.ans, self.val = self.params.split(',')
        self.ans = self.ans.strip()
        self.val = self.val.strip()
        
    def update_workflow(self):
        """Do action"""
        
        # Set
        print("PROCESSING VIEWQUE")
        try:
            if self.val == 'True':
                self.workflow[self.ans]['ask'] = True
            else:
                self.workflow[self.ans]['ask'] = False
        except:
            # self.log_exception('VIEWQUE')
            print(f"[ERROR] SETANS problem with {self.ans}")
            
        # Return updated workflow
        return self.workflow

    # def log_exception(self, func_name):
    #     """Log an exception"""
    #     if 'exceptions' not in self.workflow.keys():
    #         self.workflow['exceptions'] = []
    #         self.workflow['exceptions'].append({'func': func_name})


class SENDEMAIL(ActionFunc):
    """Test class to log sending an email

    format: SENDEMAIL('person@example.com', "This is an alert that FOO happened.")
    """

    def __init__(self, func_params, workflow):
        super().__init__(func_params, workflow)
        self.parse_params()

    def parse_params(self):
        """Parse functions params"""

        # Rule validated so we know params pattern for function
        self.email_str, self.msg_str = self.params.split(',')
        self.email_str = self.email_str.strip()
        self.msg_str = self.msg_str.strip()

    def update_workflow(self):
        """Do action"""
        
        # Set
        print("PROCESSING SENDEMAIL")
        try:
            print(f"[INFO] Sending email to '{self.email_str}' stating: '{self.msg_str}'")
        except:
            # self.log_exception('VIEWQUE')
            print(f"[ERROR] SENDEMAIL problem with '{self.msg_str}'")
            
        # Return updated workflow
        return self.workflow

