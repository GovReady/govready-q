# Parsers
import re
import json

# utilities
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
    #    from controls.parsers import CliControlImporter
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

    import xlrd

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

class StatementParser_TaggedTextWithElementsInBrackets(object):
    """Parses statements from a text file with serially listed controls where control ids and elements are enclosed in brackets"""

    # Example text file format to be parsed
    #    meta:
    #       system_name:  My IT System
    #       system_id:    id_in_my_database_if_importing
    #
    #    [AU-2]
    #
    #
    #    The [CloudOps ISSO] has access to the audit logs in [Kibana] however responses are based on artifacts provided
    #    by the [LMO team].
    #
    #
    #    (b) The [LMO Team] and the [ISSO] coordinates the security audit function with other organizational entities 
    #    requiring audit-related information to enhance mutual support and to help guide the selection of auditable events;
    #
    # Notes:
    #    - Goal is to save statement of whatever length and list of system elements involved with process
    #    - Ignore multiple intervening lines
    #    - System name must be entered manually
    #    - Script makes one pass to build search dictionary with bracketed strings
    #      then uses dictionary to find all instances of strings in statements. This makes it
    #    - unnecessary to place all instances of elements regardless of brackets.
    #

    # Example snippet of code using this Class
    # Note how the field_map must be defined and probably some customization of the class itself
    #
    #    # Start Python shell with `python shell`
    #
    #    from parsers_i import StatementParser_TaggedTextWithElementsInBrackets
    #    fp = "data/test_data/TaggedTextWithElementsInBrackets_example.txt"
    #    par = StatementParser_TaggedTextWithElementsInBrackets(fp)
    #
    #    par.statements[0]['sid'], par.statements[0]['elements']
    #
    # from parsers_i import StatementParser_TaggedTextWithElementsInBrackets;fp = "data/test_data/TaggedTextWithElementsInBrackets_example.txt"; par = StatementParser_TaggedTextWithElementsInBrackets(fp)
    # from parsers_i import StatementParser_TaggedTextWithElementsInBrackets;fp = "data/test_data/TaggedTextWithElementsInBrackets_example.txt"; par = StatementParser_TaggedTextWithElementsInBrackets(fp); s = par.statements_by_control_id(); s.keys()
    # par.create_statement_dict("[AC-2]", s["[AC-2]"])


    def __init__(self, file_path):
        self.file_path = file_path
        # self.catalog = None
        self.text = self._read_file()
        self.elements = self.all_terms_in_brackets_distinct()
        self.statements = []
        statements = self.statements_by_control_id()
        for sid in statements.keys():
            self.statements.append(self.create_statement_dict(sid,statements[sid]))

    def _read_file(self):
        # does file exist?
        # TODO Handle missing file
        with open(self.file_path, 'r') as filehandle:
            filecontent = filehandle.read()
        return filecontent

    def all_terms_in_brackets(self):
        import re
        # Non-gready pattern match for bracket items
        bracketed_terms = re.findall(r'\[(.*?)\]', self.text)
        return bracketed_terms

    def all_terms_in_brackets_distinct(self):
        import re
        # Non-gready pattern match for bracket items
        bracketed_terms = set(re.findall(r'\[(.*?)\]', self.text))
        return bracketed_terms

    def statements_by_control_id(self):
        """Split text into separate statements by control ids from a catalog"""

        # Temporary catalog
        control_ids = ["[AC-2]", "[AU-2]", "[CM-5]"]

        cnt = 0
        statements = {}
        statement = ""
        cur_id = "[XX-0]"
        # Read text line by line and aggregate content by control_id
        lines = self.text.split("\n")

        for line in lines:
            cnt += 1
            # print("{}|{}|".format(cnt, line))
            # is this  control_id on this line?
            if line in control_ids and line != cur_id:
                # Add current statement to statements dictionary
                # Start new statement and update cur_id
                cur_id = line
                statements[cur_id] = ""
                # statements[cur_id] = {"sid": cur_id, "statement": "", "elements": [], "element_counts": {}}
            else:
                if len(statements.keys()) > 0 :
                    statements[cur_id] += "\n" + line
        return statements

    def create_statement_dict(self, sid, statement):
        """Creates a proper statement dictionary profiling the statement by element terms"""
        # {"sid": cur_id, "statement": "", "elements": [], "element_counts": {}}

        sd = {"sid": sid, "statement": statement, "elements": [], "element_counts": {}}
        import re
        # Count matches of bracketed terms
        for t in self.all_terms_in_brackets_distinct():
            t_found = re.findall(r'{}'.format(t), statement)
            if len(t_found) > 0:
                sd['elements'].append(t)
                sd['element_counts'][t] = len(t_found)
        return sd

