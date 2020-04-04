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

