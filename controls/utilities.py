# Utility functions
import re
import xlrd
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
    # Recognize only properly formmated control id:
    #   at-1, at-01, ac-2.3, ac-02.3, ac-2 (3), ac-02 (3), ac-2(3), ac-02 (3)
    pattern = re.compile("^[A-Za-z][A-Za-z]-[0-9() .]*$")
    if not pattern.match(cl_id):
        return render(request, "controls/detail.html", { "control": {} })

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

class CliControlImporter(object):
    """Command Line Importer into Controls from an .xlsx file"""

    # Example snippet of code using this Class
    # Note how the field_map must be defined and probably some customization of the class itself
    #
    #    from controls.utilities import CliControlImporter
    #    fp = "~/Downloads/Copy of Controls_Implementation_Securit.xlsx"
    #    cci = CliControlImporter(fp)
    #
    #    field_map = {'oscal_ctl_id': 'Paragraph/ReqID', 'legacy_imp_smt': 'Private Implementation'}
    #    r = cci.rows[33]
    #    cci.build_common_control_from_row(r, field_map)
    #    x = cci.build_common_control_from_row(r, field_map)
    #    cci.create_common_control(x)
    #
    #    r = cci.rows[37]
    #    x = cci.create_common_control(cci.build_common_control_from_row(r, field_map), field_map)
    #    cci.create_common_control(x)
    #
    #    # loop through rows
    #    field_map = {'oscal_ctl_id': 'Paragraph/ReqID', 'legacy_imp_smt': 'Private Implementation'}
    #    for r in cci.rows:
    #        if len(r['Private Implementation']) < 10:
    #            continue
    #        x = cci.build_common_control_from_row(r, field_map)
    #        x['oscal_ctl_id']
    #        cci.create_common_control(x)


    def __init__(self, file_path):
        self.xlsx_path = file_path
        # self.catalog = None
        self.fields = self._read_fields()
        self.rows = self._read_rows()

    def _read_fields(self):
        self.wb = xlrd.open_workbook(self.xlsx_path)
        self.ws = self.wb.sheet_by_index(0);
        return [ self.ws.cell_value(0,i) for i in range(0,16) ]

    def _read_rows(self):
        # NOTE This script will change according to import source
        #~/Downloads/Copy\ of\ Controls_Implementation_Securit.xlsx
        # fp = "~/Downloads/Copy of Controls_Implementation_Securit.xlsx"
        cliall = []
        for r in range(1,175):
            cli = {}
            for i in range(0, len(self.fields)):
                cli[self.fields[i]] = self.ws.cell_value(r,i)
                if i < 2 and cli[self.fields[i]] == "":
                    cli[self.fields[i]] = self.ws.cell_value(r-1,i)
            # print(json.dumps(cli, indent=4, sort_keys=False))
            cliall.append(cli)
        return cliall

    def get_common_control_provider_by_id(self, ccp_id):
        """Return a CommonControlProvider object by its id"""
        return CommonControlProvider.objects.get(id=ccp_id)

    def build_common_control_from_row(self, row_obj, field_map):
        """Build a common control from rows based on field_mapping"""
        cc_obj = {}
        for key in field_map.keys():
            cc_obj[key] = row_obj[field_map[key]]
        # Add in missing fields
        cc_obj['name'] = "CACE " + cc_obj['oscal_ctl_id']
        cc_obj['description'] = cc_obj['name']
        cc_obj['common_control_provider'] = self.get_common_control_provider_by_id(1)
        # standardize oscal_ctl_id
        cc_obj['oscal_ctl_id'] = oscalize_control_id(cc_obj['oscal_ctl_id'])
        return cc_obj

    def create_common_control(self, cc_obj):
        """Create and save a CommonControl object from a properly formatted dictionary"""
        cc_new = CommonControl( name = cc_obj['name'],
                                description = cc_obj['description'],
                                common_control_provider = cc_obj['common_control_provider'],
                                oscal_ctl_id = cc_obj['oscal_ctl_id'],
                                legacy_imp_smt = cc_obj['legacy_imp_smt'])
        try:
            if CommonControl.objects.filter(name=cc_new.name).exists():
                # Common control already exists with same name
                return {"status": False, "message": "Common Control with name {} exists".format(cc_new.name), "obj": cc_new, "data": None}
            else:
                # CommonControl does not exist, save it
                cc_new.save()
                # print("new cc: {}".format(cc_new))
                return {"status": True, "message": "CommonControl id {} created".format(cc_new.name), "obj": cc_new, "data": cc_new.id}
        except Exception as e:
            return {"status": False, "message": e, "obj": cc_new, "data": None}

    # Notes

