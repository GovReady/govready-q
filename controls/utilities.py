# Utility functions
import re
import json

from .models import CommonControlProvider, CommonControl

def replace_line_breaks(text, break_src="\n", break_trg="<br />"):
    """ replace one type of line break with another in text block """
    if text is None:
    	return ""
    if break_src in text:
        return break_trg.join(text.split(break_src))
    else:
        return text

def replace_unicodes(text):
	""" replace various unicodes characters """
	text = text.replace(u'\ufffd', "'")
	return text

def use_org_name(text, org_name):
    """ replace 'The organization' with org_name """
    if org_name is not None:
        text = text.replace(u'The organization', "The organization %s" % org_name)
        return text
    else:
        return text

def replace_assignments(text, project):
    """ if assigments are defined replace them with value from system-security-plan.yaml """
    # for now do something hacking to prove it works
    text = text.replace(u'[Assignment: organization-defined audit record storage requirements]', project['assignments']['organization-defined-audit-record-storage-requirements'] )
    return text

def replace_colons(text, project):
    """ replace colons with &colon; """
    # for now do something hacking to prove it works
    text = text.replace(u':', "&colon;")
    return text

def oscalize_control_id(cl_id):
    """ output an oscal standard control id from various common formats for control ids """

    # Handle improperly formatted control id
    # Recognize properly formatted control 800-53 id:
    #   at-1, at-01, ac-2.3, ac-02.3, ac-2 (3), ac-02 (3), ac-2(3), ac-02 (3)
    # Recognize 800-171 control id:
    #   3.1.1, 3.2.4
    pattern = re.compile("^[A-Za-z][A-Za-z]-[0-9() .]*$|^3\.[0-9]{1,2}\.[0-9]{1,2}$")
    if not pattern.match(cl_id):
        return ""

    # Handle properly formatted existing id
    # Transform various patterns of control ids into OSCAL format
    # Fix leading zero in at-01, ac-02.3, ac-02 (3)
    cl_id = cl_id = re.sub(r'^([A-Za-z][A-Za-z]-)0(.*)$', r'\1\2', cl_id)
    # Change paranthesis into a dot
    cl_id = re.sub(r'^([A-Za-z][A-Za-z]-)([0-9]*)([ ]*)\(([0-9]*)\)$', r'\1\2.\4', cl_id)
    # Remove trailing space
    cl_id = cl_id.strip(" ")
    # makes ure lowercase
    cl_id = cl_id.lower()

    return cl_id


def oscalize_catalog_key(catalogkey):
    """ Covers empty catalog key case. Otherwise, outputs an oscal standard catalog key from various common formats for catalog keys
    NIST_SP_800_53_rev4 --> NIST_SP-800-53_rev4
    """

    # A default catalog key
    if catalogkey=='':
        catalogkey = 'NIST_SP-800-53_rev4'
    # Handle improperly formatted control id
    if catalogkey.count("_") > 2:
        split_key_list = catalogkey.split("_800_")
        catalogkey = split_key_list[0] + "-800-" + split_key_list[1]

    return catalogkey


def get_control_statement_part(control_stmnt_id):
    """ Parses part from control statement id
    ra-5_smt.a --> a
    """

    if "." not in control_stmnt_id and "_" not in control_stmnt_id:
        return control_stmnt_id

    # Portion after the '_smt.' is the part
    split_stmnt = control_stmnt_id.split("_smt.")
    return split_stmnt[1] if len(split_stmnt) > 1 else ""


def increment_element_name(component_name):
    """Increments an Element's name to avoid naming conflicts for a system or component"""

    if re.search("\((\d+)\)$", component_name):
        new_component_name = re.sub("\((\d+)\)$", lambda m: " (" + str(int(m.groups()[0])+1) + ")", component_name)
    else:
        new_component_name = component_name + " (1)"

    return new_component_name
