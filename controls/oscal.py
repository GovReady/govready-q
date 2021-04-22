from collections import defaultdict
import os
import json
import yaml
import re
from pathlib import Path
import sys

CATALOG_PATH = os.path.join(os.path.dirname(__file__), 'data', 'catalogs')
EXTERNAL_CATALOG_PATH = os.path.join(f"{os.getcwd()}",'local', 'controls', 'data', 'catalogs')

class Catalogs(object):
    """Represent list of catalogs"""

    # well known catalog identifiers

    NIST_SP_800_53_rev4 = 'NIST_SP-800-53_rev4'
    NIST_SP_800_53_rev5 = 'NIST_SP-800-53_rev5'
    NIST_SP_800_171_rev1 = 'NIST_SP-800-171_rev1'

    def __init__(self):
        self.catalog_path = CATALOG_PATH
        # self.catalog = None
        self.catalog_keys = self._list_catalog_keys()
        self.index = self._build_index()

    def extend_external_catalogs(self, catalog_info, extendtype):
        """
        Add external catalogs to list of catalogs
        """
        os.makedirs(EXTERNAL_CATALOG_PATH, exist_ok=True)
        external_catalogs = [file for file in os.listdir(EXTERNAL_CATALOG_PATH) if
                  file.endswith('.json')]
        catalog_info = check_and_extend(catalog_info, external_catalogs, extendtype, "_catalog")

        return catalog_info

    def _list_catalog_files(self):
        return self.extend_external_catalogs([
            'NIST_SP-800-53_rev4_catalog.json',
            'NIST_SP-800-53_rev5_catalog.json',
            'NIST_SP-800-171_rev1_catalog.json'
        ], "files")

    def _list_catalog_keys(self):

        return self.extend_external_catalogs([
            Catalogs.NIST_SP_800_53_rev4,
            Catalogs.NIST_SP_800_53_rev5,
            Catalogs.NIST_SP_800_171_rev1
        ], "keys")

    def _load_catalog_json(self, catalog_key):
        catalog = Catalog(catalog_key)
        #print(catalog_key, catalog._load_catalog_json())
        return catalog._load_catalog_json()

    def _build_index(self):
        """Build a small catalog_index from metadata"""
        index = []
        for catalog_key in self._list_catalog_keys():
            catalog = self._load_catalog_json(catalog_key)
            index.append(
                {'id': catalog['id'], 'catalog_key': catalog_key, 'catalog_key_display': catalog_key.replace("_", " "),
                 'metadata': catalog['metadata']})
        return index

    def list(self):
        catalog_titles = [item['metadata']['title'] for item in self.index]
        return catalog_titles

    def list_catalogs(self):
        """
        List catalog objects
        """
        return [Catalog(key) for key in Catalogs()._list_catalog_keys()]


def uhash(obj):
    """Return a positive hash code"""
    h = hash(obj)
    return h + sys.maxsize + 1

def check_and_extend(values, external_values, extendtype, splitter):
    """
    Modularize value to extend
    """
    if extendtype == "keys":
        keys = [key.split(f'{splitter}.json')[0] for key in external_values]
        values.extend(keys)
    elif extendtype == "files":
        files = [file for file in external_values]
        values.extend(files)
    return values

class Catalog(object):
    """Represent a catalog"""

    # Create a singleton instance of this class per catalog. GetInstance returns
    # that singleton instance. Instead of doing
    # `cg = Catalog(catalog_key=Catalogs.NIST_SP_800_53_rev4)`,
    # do `cg = Catalog.GetInstance(catalog_key=Catalogs.NIST_SP_800_53_rev4')`.
    @classmethod
    def GetInstance(cls, catalog_key=Catalogs.NIST_SP_800_53_rev4, parameter_values=dict()):
        # Create a new instance of Catalog() the first time for each
        # catalog key / parameter combo
        # this method is called. Keep it in memory indefinitely.
        # Clear cache only if a catalog itself changes

        catalog_instance_key = Catalog._catalog_instance_key(catalog_key, parameter_values)

        if not hasattr(cls, catalog_instance_key):
            new_catalog = Catalog(catalog_key=catalog_key, parameter_values=parameter_values)
            setattr(cls, catalog_instance_key, new_catalog)
        return getattr(cls, catalog_instance_key)

    @staticmethod
    def _catalog_instance_key(catalog_key, parameter_values):
        catalog_instance_key = '_cached_instance_' + catalog_key
        if parameter_values:
            parameter_values_hash = uhash(frozenset(parameter_values.items()))
            catalog_instance_key += '_' + str(parameter_values_hash)
        return catalog_instance_key.replace('-', '_')

    def __init__(self, catalog_key=Catalogs.NIST_SP_800_53_rev4, parameter_values=dict()):
        self.catalog_key = catalog_key
        self.catalog_key_display = catalog_key.replace("_", " ")
        self.catalog_path = CATALOG_PATH
        self.external_catalog_path = EXTERNAL_CATALOG_PATH
        self.catalog_file = catalog_key + "_catalog.json"
        try:
            self.oscal = self._load_catalog_json()
            self.status = "ok"
            self.status_message = "Success loading catalog"
            self.catalog_id = self.oscal['id']
            self.info = {}
            self.info['groups'] = self.get_groups()
        except Exception as e:
            self.oscal = None
            self.status = "error"
            self.status_message = "Error loading catalog"
            self.catalog_id = None
            self.info = {}
            self.info['groups'] = None
        # Precalculate the flattened versions of controls to improve performance
        # WARNING TODO: This precalculation along with instance caching of controls
        # may cause a problem in multi-tenant environment where different tenants have
        # have different organizational defined parameters.
        self.parameter_values = parameter_values
        self.flattened_controls_all_as_dict = self.get_flattened_controls_all_as_dict()
        self.parameters_by_control = self._cache_parameters_by_control()

    def _load_catalog_json(self):
        """Read catalog file - JSON"""
        catalog_file = os.path.join(self.catalog_path, self.catalog_file)
        # Does file exist?
        if not os.path.isfile(catalog_file):
            # Check if there any external oscal catalog files
            try:
                catalog_file = os.path.join(self.external_catalog_path, self.catalog_file)
            except:
                print(f"ERROR: {catalog_file} does not exist")
                return False
        # Load file as json
        with open(catalog_file, 'r') as json_file:
            data = json.load(json_file)
            oscal = data['catalog']
        return oscal

    def find_dict_by_value(self, search_array, search_key, search_value):
        """Return the dictionary in an array of dictionaries with a key matching a value"""
        result_dict = next((sub for sub in search_array if sub[search_key] == search_value), None)
        return result_dict

    # def ids(self, search_collection):
    #     """Return the array of ids for a collection"""
    #     return [item['id'] for item in search_collection if 'id' in item]

    def get_groups(self):
        return self.oscal['groups']

    def get_group_ids(self):
        search_collection = self.get_groups()
        return [item['id'] for item in search_collection]

    def get_group_title_by_id(self, id):
        group = self.find_dict_by_value(self.get_groups(), 'id', id)
        if group is None:
            return None
        return group['title']

    def get_group_id_by_control_id(self, control_id):
        """Return group id given id of a control"""

        # For 800-53, 800-171, we can match by first few characters of control ID
        group_ids = self.get_group_ids()
        for group_id in group_ids:
            if group_id.lower() in control_id.lower():
                return group_id

        # Group ID was not matched
        return None

    def get_controls(self):
        controls = []
        for group in self.get_groups():
            controls += [control for control in group['controls']]
        return controls

    def get_control_ids(self):
        search_collection = self.get_controls()
        return [item['id'] for item in search_collection]

    def get_controls_all(self):
        controls = []
        for group in self.get_groups():
            for control in group['controls']:
                controls.append(control)
                if 'controls' in control:
                    controls += [control_e for control_e in control['controls']]
        return controls

    def get_controls_all_ids(self):
        search_collection = self.get_controls_all()
        return [item['id'] for item in search_collection]

    def get_control_by_id(self, control_id):
        """Return the dictionary in an array of dictionaries with a key matching a value"""
        search_array = self.get_controls_all()
        search_key = 'id'
        search_value = control_id
        result_dict = next((sub for sub in search_array if sub[search_key] == search_value), None)
        return result_dict

    def get_control_property_by_name(self, control, property_name):
        """Return value of a property of a control by name of property"""
        prop = self.find_dict_by_value(control['properties'], "name", property_name)
        if prop is None:
            return None
        return prop['value']

    def get_control_parameter_label_by_id(self, control, param_id):
        """Return value of a parameter of a control by id of parameter"""
        param = self.find_dict_by_value(control['parameters'], "id", param_id)
        return param['label']

    def get_control_prose_as_markdown(self, control_data, part_types={"statement"}, parameter_values=dict()):
        # Concatenate the prose text of all of the 'parts' of this control
        # in Markdown. Filter out the parts that are not wanted.
        # Example 'statement'
        #   python3 -c "import oscal; cg = oscal.Catalog(); print(cg.get_control_prose_as_markdown(cg.get_control_by_id('ac-6')))"
        # Example 'guidance'
        #   python3 -c "import oscal; cg = oscal.Catalog(); print(cg.get_control_prose_as_markdown(cg.get_control_by_id('ac-6'), part_types={'guidance'}))"

        # Is this control withdrawn?
        status = self.get_control_property_by_name(control_data, 'status')
        if status == "Withdrawn":
            return "Withdrawn"

        text = self.format_part_as_markdown(control_data, filter_name=part_types)

        text_params_replaced = self.substitute_parameter_text(control_data, text, parameter_values)

        return text_params_replaced

    def format_part_as_markdown(self, part, indentation_level=-1, indentation_string="    ", filter_name=None,
            hide_first_label=True):
        # Format part, which is either a control or a part, as Markdown.

        # First construct the prose text of this part. If there is a
        # label, put it at the start.

        md = ""

        # If this part has a label (i.e. "a."), get the label.
        label = ""
        label_property = self.find_dict_by_value(part.get('properties', []), 'name', 'label')
        if label_property:
            label = label_property['value'] + " "
        # Hide first label to avoid showing control_id
        if indentation_level == -1 and hide_first_label:
            label = ""
        # Emit the label, if any.
        md += label

        # If it has a 'prose' key, then add that. The 'prose' is a string
        # that may contain Markdown formatting, so we don't touch it much
        # because we are supposed to produce markdown.
        #
        # OSCAL defines "markup-multiline" to use two escaped \n's to
        # denote paragraph boundaries, so we replace the literal "\n\n"
        # with two actual newline characters.
        if 'prose' in part:
            prose = part['prose']
            prose = prose.replace("\\n\\n", "\n\n")
            md += prose

        # If prose is multiple lines and if there is a label, then to be
        # valid Markdown, all lines after the first should be indented
        # the number of characters in the label (plus its space).
        if label:
            md = md.split("\n")
            for i in range(1, len(md)):
                md[i] = (" " * len(label)) + md[i]
            md = "\n".join(md)

        # Apply indentation. Each line of the prose should be indented
        # (not just the first line). Break the prose up into lines,
        # add the indentation at the start of each line, and then put
        # the lines back together again.
        # In Python, a string times an integer repeats it.
        md = "\n".join([
            (indentation_level * indentation_string) + line
            for line in md.split("\n")
        ])

        # If there was any prose text, add a paragraph boundary.
        if md != "":
            md += "\n\n"

        # If it has sub-parts, then emit those.
        if "parts" in part:
            for part in part["parts"]:
                # If filter_name is given, filter out the parts that don't have
                # one of the givne names.
                if filter_name and part.get('name') not in filter_name:
                    continue

                # Append this part.
                md += self.format_part_as_markdown(part,
                                                   indentation_string=indentation_string,
                                                   indentation_level=indentation_level + 1)

        return md

    def substitute_parameter_text(self, control, text, parameter_values):
        # Fill in parameter_values with control parameter labels for any
        # parameters that are not specified.
        parameter_values = dict(parameter_values)  # clone so that we don't modify the caller's dict

        if "parameters" not in control:
            return text

        for parameter in control['parameters']:
            if parameter["id"] not in parameter_values:
                parameter_values[parameter["id"]] = f"[{parameter.get('label', parameter['id'])}]"

        for parameter_key, parameter_value in parameter_values.items():
            text = re.sub(r"{{ " + re.escape(parameter_key) + " }}", parameter_value, text)

        return text

    def get_flattened_control_as_dict(self, control):
        """
        Return a control as a simplified, flattened Python dictionary.
        If parameter_values is supplied, it will override any paramters set
        in the catalog.
        """
        family_id = self.get_group_id_by_control_id(control['id'])
        description = self.get_control_prose_as_markdown(control, part_types={"statement"},
                                                        parameter_values=self.parameter_values)
        description_print = description.replace("\n", "<br/>")
        cl_dict = {
            "id": control['id'],
            "id_display": re.sub(r'^([A-Za-z][A-Za-z]-)([0-9]*)\.([0-9]*)$', r'\1\2 (\3)', control['id']),
            "title": control['title'],
            "family_id": family_id,
            "family_title": self.get_group_title_by_id(family_id),
            "class": control['class'],
            "description": description,
            "description_print": description_print,
            "guidance": self.get_control_prose_as_markdown(control, part_types={"guidance"}),
            "catalog_file": self.catalog_file,
            "catalog_id": self.catalog_id,
            "sort_id": self.get_control_property_by_name(control, "sort-id"),
            "label": self.get_control_property_by_name(control, "label")
        }
        # cl_dict = {"id": "te-1", "title": "Test Control"}
        return cl_dict

    def get_flattened_controls_all_as_dict(self):
        """Return all controls as a simplified flattened Python dictionary indexed by control ids"""
        # Create an empty dictionary
        cl_all_dict = {}
        # Get all the controls
        for cl in self.get_controls_all():
            # Get flattened control and add to dictionary of controls
            cl_dict = self.get_flattened_control_as_dict(cl)
            cl_all_dict[cl_dict['id']] = cl_dict
        return cl_all_dict

    def _cache_parameters_by_control(self):
        cache = defaultdict(list)
        if self.oscal:
            groups = self.oscal["groups"]
            for family in groups:
                for control in family["controls"]:
                    control_id = control["id"]
                    for parameter in control.get("parameters", []):
                        cache[control_id].append(parameter["id"])
        return dict(cache)

    def get_parameter_ids_for_control(self, control_id):
        return self.parameters_by_control.get(control_id, [])

