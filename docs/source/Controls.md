Control Reference
=================

GovReady Q includes references to exposed control libraries as of v0.9.1.4. (Previously versions embedded controls within output templates.)

A "Control Catalog" is formal collection of controls, such as the NIST Risk Management Framework's control catalog outline in NIST Special Publication 800-53.

Control catalogs are treated and accessed as Python class object in GovReady instead of models. Control catalogs--the description of controls--are distinct from implementation narratives of how controls are implemented for an individual system.

## Control Look Up

Individual controls can be access via the path `/controls/control_catalog/control_id`.

## Controls in Output Templates

Controls can also be included output templates via the `{{ control_catalog }}` substitution parameter.

The `{{ control_catalog }}` substitution parameter contains 

### Technical Details

First implementation only works with NIST 800-53 and uses code from GovReady project 800-53 Server project.

Controls are managed within the code in a  directory `controls` containing a class for
listing a security control catalog. Code uses XSLT transformations to extract controls from XML representation of the control catalog. (This will change to OSCAL in future.)

The class `module_logic.TemplateContext` manages a item called `control_catalog` to expose the control catalog to the output templates.

The control catalog is a dictionary of dictionaries. The ID of the controls is the index which points to a dictionary defined for the control.

```
{
    'AC-2 (3)': {
        'id': 'AC-2 (3)', 'title': 'DISABLE INACTIVE ACCOUNTS', 'family': '',
        'description': 'The information system automatically disables inactive accounts after [Assignment: organization-defined time period].',
        'control_enhancements': 'N/A', 'supplemental_guidance': ''
    },
...
}
```

**Developer changes**

* Add 800-53 control catalog via classes `SecControlsAll` and `SecControl`
* Create a new directory `controls` into which we add a class for listing a security control catalog.
* Add a new item type to module_logic.TemplateContext called `control_catalog` to enable iterable dictionary of control catalog.

## Code discussion

Output templates are Jinja templates within Django template and are rendered within `guidedmodules/module_logic.py`


Better way is back to putting in view

       # special values
        if self.module_answers and self.module_answers.task:
            # Attributes that are only available if there is a task.
            if not self.is_computing_title or not self.root:
                # 'title' isn't available if we're in the process of
                # computing it
                yield "title"
            for attribute in ("task_link", "project", "organization", "control_catalog_t"):
                if attribute not in seen_keys:
                    yield attribute

## Control Parsers

Developers should see `controls/parsers.py` for useful functionality that can be imported our used with `from controls.parsers import *` statement in Python scripts.

The function `oscalize_control_id`outputs an oscal standard control id from various common formats for control ids.


### CliControlImporter

The Class `CliControlImporter` is a command line importer into controls from an `.xlsx` file and loading those files into Common Control or Control models. **Note this class currently needs to be customized for the structure of importing data.**

Below is a snippet of code for Django Shell leveraging `CliControlImporter` to import Common Controls from a spreadsheet of controls

        from controls.parsers import CliControlImporter
        fp = "~/Downloads/Copy of Controls_Implementation_Securit.xlsx"
        cci = CliControlImporter(fp)

        field_map = {'oscal_ctl_id': 'Paragraph/ReqID', 'legacy_imp_smt': 'Private Implementation'}
        r = cci.rows[33]
        cci.build_common_control_from_row(r, field_map)
        x = cci.build_common_control_from_row(r, field_map)
        cci.create_common_control(x)

        r = cci.rows[37]
        x = cci.create_common_control(cci.build_common_control_from_row(r, field_map), field_map)
        cci.create_common_control(x)

        # Loop through rows
        # Rows to be imported from this spreadsheet with CommonControls have long strings in 'Private Implementation' column
        field_map = {'oscal_ctl_id': 'Paragraph/ReqID', 'legacy_imp_smt': 'Private Implementation'}
        for r in cci.rows:
            if len(r['Private Implementation']) < 10:
                continue
            x = cci.build_common_control_from_row(r, field_map)
            x['oscal_ctl_id']
            cci.create_common_control(x)

### StatementParser_TaggedTextWithElementsInBrackets

The `StatementParser_TaggedTextWithElementsInBrackets` class is a utility to parse statements from a text file with serially listed controls where control ids and elements are enclosed in brackets.

* Goal is to save statement of whatever length and list of system elements involved with process
* Ignore multiple intervening lines
* System name must be entered manually
* Script makes one pass to build search dictionary with bracketed strings then uses dictionary to find all instances of strings in statements. This makes it unnecessary to place all instances of elements regardless of brackets.

The source text file to be parsed should be in the following format:

       meta:
          system_name:  My IT System
          system_id:    id_in_my_database_if_importing

       [AU-2]


       The [CloudOps ISSO] has access to the audit logs in [Kibana] however responses are based on artifacts provided
       by the [LMO team].


       (b) The [LMO Team] and the [ISSO] coordinates the security audit function with other organizational entities 
       requiring audit-related information to enhance mutual support and to help guide the selection of auditable events;

Below is a snippet of code for Django Shell leveraging `StatementParser_TaggedTextWithElementsInBrackets` to parse control implementatation statements from a text of controls

       from controls.parsers import StatementParser_TaggedTextWithElementsInBrackets
       fp = "/Users/greg/Downloads/TaggedTextWithElementsInBrackets_example.txt"
       par = StatementParser_TaggedTextWithElementsInBrackets(fp)
       par.statements[0]['sid'], par.statements[0]['elements']


