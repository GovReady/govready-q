# Utility functions
import re
import sys
from structlog import get_logger
from datetime import date, datetime

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

def uhash(obj):
    """Return a positive hash code"""
    h = hash(obj)
    return h + sys.maxsize + 1

def de_oscalize_control_id(control_id, catalog_key=None):
    """ return the conventional control formatting from an oscalized version of the control id.
        de_oscalize_control("ac-2")     --> AC-2
        de_oscalize_control("ac-2.3")   --> AC-2(3)
        de_oscalize_control("3.1.3")    --> 3.1.3
        de_oscalize_control("c3.1.3", 'NIST_SP-800-171_rev1')   --> 3.1.3
    """

    if catalog_key and catalog_key == 'NIST_SP-800-171_rev1':
        control_id = control_id.lower().lstrip('c')
    return re.sub(r'^([A-Za-z][A-Za-z]-)([0-9]*)\.([0-9]*)$', r'\1\2(\3)', control_id).upper()

def oscalize_control_id(cl_id):
    """ output an oscal standard control id from various common formats for control ids """

    # Handle improperly formatted control id
    # Recognize properly formatted control 800-53 id:
    #   at-1, at-01, ac-2.3, ac-02.3, ac-2 (3), ac-02 (3), ac-2(3), ac-02 (3)
    # Recognize 800-171 control id:
    #   3.1.1, 3.2.4
    # Recognize CMMC control id:
    #   ac.1.001
    pattern = re.compile("^[A-Za-z][A-Za-z]-[0-9() .]*$|^3\.[0-9]{1,2}\.[0-9]{1,2}$|^[A-Za-z][A-Za-z][.][0-9][.][0-9]{1,3}")
    if not pattern.match(cl_id):
        logger = get_logger()
        logger.warning(
            event=f"The given control could not be parsed given the Control ID structure",
            object={"object": "control", "id": cl_id, "pattern_result": ""}
        )
        return cl_id

    # Handle properly formatted existing id
    # Transform various patterns of control ids into OSCAL format
    # Fix leading zero in at-01, ac-02.3, ac-02 (3)
    cl_id = cl_id = re.sub(r'^([A-Za-z][A-Za-z]-)0(.*)$', r'\1\2', cl_id)
    # Change paranthesis into a dot
    cl_id = re.sub(r'^([A-Za-z][A-Za-z]-)([0-9]*)([ ]*)\(([0-9]*)\)$', r'\1\2.\4', cl_id)
    # Remove trailing space
    cl_id = cl_id.strip(" ")
    # makes sure lowercase
    cl_id = cl_id.lower()

    return cl_id

def oscalize_catalog_key(catalogkey=None):
    """Outputs an oscal standard catalog key from various common formats for catalog keys
    Covers empty catalog key case
    Example: NIST_SP_800_53_rev4 --> NIST_SP-800-53_rev4
    """
    DEFAULT_CATALOG_KEY = 'NIST_SP-800-53_rev5'
    if catalogkey is None or catalogkey=='':
        return DEFAULT_CATALOG_KEY
    # If coming with reference to some path to catalog json file
    # (e.g. '../../../nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json', 'FedRAMP_rev4_HIGH-baseline_profile.json')
    if ".json" in catalogkey:
        catalogkey = catalogkey.split('/')[-1].split('_catalog.json')[0].split(".json")[0]
    # Handle the default improperly formatted control id
    if catalogkey.count("_") > 2 and "800" in catalogkey:
        split_key_list = catalogkey.split("_800_")
        catalogkey = split_key_list[0] + "-800-" + split_key_list[1]
    # TODO: Handle other cases
    #if catalogkey in ['NIST_SP-800-53_rev4', 'NIST_SP-800-53_rev4', 'CMMC_ver1', 'NIST_SP-800-171_rev1']:

    return catalogkey

def get_control_statement_part(control_stmnt_id):
    """ Parses part from control statement id
    ra-5_smt.a --> a
    """

    if "." not in control_stmnt_id and "_" not in control_stmnt_id:
        return control_stmnt_id

    # Portion after the '_smt.' is the part, au-2_smt.b --> sid au-2, part b
    split_stmnt = control_stmnt_id.split("_smt.")
    if len(split_stmnt) <= 1:
        # ac-2.3.a --> sid ac-2, part 3
        split_stmnt = control_stmnt_id.split(".")
    return split_stmnt[1] if len(split_stmnt) > 1 else ""


def increment_element_name(component_name):
    """Increments an Element's name to avoid naming conflicts for a system or component"""

    if re.search("\((\d+)\)$", component_name):
        new_component_name = re.sub("\((\d+)\)$", lambda m: " (" + str(int(m.groups()[0])+1) + ")", component_name)
        # Also remove any extra spaces
        new_component_name = re.sub("\s\s+", " ", new_component_name)
    else:
        new_component_name = component_name + " (1)"

    return new_component_name

def json_serializer(obj):
    """JSON Serializer for objects that are not serializable by default settings i.e., datetime objects"""
    # Get Object
    # Check each field if it is json serializable
    # if not, change object format to one that is
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = json_serializer(value)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj
