from django.contrib import messages

class ActionFunc():
    """Base class for Action Functions"""
    
    def __init__(self, func_params, workflow, request):
        self.params = func_params
        self.workflow = workflow
        self.request = request
        
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
    
    def __init__(self, func_params, workflow, request):
        super().__init__(func_params, workflow, request)
        self.parse_params()
        self.workflow = workflow
        self.request = request

    def parse_params(self):
        """Parse function params"""

        # Rule validated so we know params pattern for function
        self.ans, self.val = self.params.split(',')
        self.ans = self.ans.strip()
        self.val = self.val.strip()
        
    def update_workflow(self):
        """Do action"""
        
        # Update workflow
        print("[DEBUG] [RULE FUNCTION] PROCESSING SETANSX")
        # try:
        #     if self.val.startswith("'") or self.val.startswith('"'):
        #         # literal
        #         ans_val = self.val.strip("'").strip('"')
        #     else:
        #         # reference
        #         ans_val = self.workflow[self.val]['ans']
        #     self.workflow[self.ans]['ans'] = ans_val
        # except:
        #     print(f"[ERROR] SETANS problem with {self.ans}")
            # self.log_exception('SETANS')
        
        # Return updated workflow
        return self.workflow

    # def log_exception(self, func_name):
    #     """Log an exception"""
    #     if 'exceptions' not in self.workflow.keys():
    #         self.workflow['exceptions'] = []
    #         self.workflow['exceptions'].append({'func': func_name})


class SETANS(ActionFunc):
    
    def __init__(self, func_params, workflow, request):
        super().__init__(func_params, workflow, request)
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
        print("PROCESSING SETANS 2")
        messages.add_message(self.request, messages.INFO, f"Setting answer via SETANS action")
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
    
    def __init__(self, func_params, workflow, request):
        super().__init__(func_params, workflow, request)
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
        print("[DEBUG] [RULE FUNCTION] PROCESSING VIEWQUE")
        messages.add_message(self.request, messages.INFO, f"VIEWQUE action")
        # try:
        #     if self.val == 'True':
        #         self.workflow[self.ans]['ask'] = True
        #     else:
        #         self.workflow[self.ans]['ask'] = False
        # except:
        #     # self.log_exception('VIEWQUE')
        #     print(f"[ERROR] SETANS problem with {self.ans}")
            
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

    def __init__(self, func_params, workflow, request):
        super().__init__(func_params, workflow, request)
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
        messages.add_message(self.request, messages.INFO, f"Sending email via SENDEMAIL action")
        try:
            print(f"[INFO] Sending email to '{self.email_str}' stating: '{self.msg_str}'")
        except:
            # self.log_exception('VIEWQUE')
            print(f"[ERROR] SENDEMAIL problem with '{self.msg_str}'")
            
        # Return updated workflow
        return self.workflow

