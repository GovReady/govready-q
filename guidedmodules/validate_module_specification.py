# This module provides a single function that validates a module YAML file
# and normalizes some fields like setting a missing 'min' on a multiple-choice
# question to 0.

from collections import OrderedDict
import re

import json
import rtyaml

from guidedmodules.module_logic import render_content

class ValidationError(ValueError):
    def __init__(self, context, message):
        self.context = context
        self.message = message
    def __str__(self):
        return self.context + ": " + self.message

def validate_module(spec, app, is_authoring_tool=False):
    # The module must have a title.
    for field in ("title",):
        if field not in spec:
            raise ValidationError("module specification", "Missing '%s' field." % field)

    # Validate that the introduction and output documents are renderable.
    # If they refer to external files, slurp in the content of those files.
    if "introduction" in spec:
        spec["introduction"] = validate_document(spec["introduction"], "module introduction", app)
    if not isinstance(spec.get("output", []), list):
        raise ValidationError("module output", "Must be a list, not a %s." % type(spec.get("output")).__name__)
    for i, doc in enumerate(spec.get("output", [])):
        spec["output"][i] = validate_document(spec["output"][i], "output document #{}".format(i+1), app)

    # 'introduction' fields are an alias for an interstitial
    # question that comes before all other questions, and since
    # it is first it will be asked first. Except in projects,
    # where it's just a renderable field.
    if "introduction" in spec and spec.get("type") != "project":
        q = {
            "id": "_introduction",
            "title": "Introduction",
            "type": "interstitial",
            "prompt": spec["introduction"]["template"],
        }
        spec.setdefault("questions", []).insert(0, q)

    # Validate an app protocol.
    if "protocol" in spec:
        if spec.get("type") != "project":
            raise ValidationError("module specification", "A protocol cannot be specified in this type of module.")
        if isinstance(spec["protocol"], str):
            # If a single protocol is given, turn it into a list of one.
            spec["protocol"] = [spec["protocol"]]
        elif isinstance(spec["protocol"], list):
            # If it's a list, the values must be strings.
            for x in spec["protocol"]:
                if not isinstance(x, str):
                    raise ValidationError("protocols", "Protocols must be strings (not %s)." % repr(x))
        else:
            raise ValidationError("module specification", "protocol must be a string or a list of strings (not %s)." % repr(spec["protocol"]))

    # Validate the questions.
    if not isinstance(spec.get("questions"), (type(None), list)):
        raise ValidationError("module questions", "Invalid data type of value for 'questions'.")
    for i, q in enumerate(spec.get("questions", [])):
        spec["questions"][i] = validate_question(spec, spec["questions"][i])

    return spec


def validate_document(doc, error_message_name, app):
    # The document must be either a string which points to another
    # file holding the document, or a dictionary. But the string
    # form isn't available if we're validating a new spec submitted
    # by the authoring tool since we don't have the app virtual
    # filesystem at that point.
    if app:
        if not isinstance(doc, (str, dict)):
            raise ValidationError(error_message_name, "Must be a file name or dictionary, not a %s." % type(doc).__name__)
    else:
        if not isinstance(doc, dict):
            raise ValidationError(error_message_name, "Must be a dictionary, not a %s." % type(doc).__name__)

    # If it's a string, slurp in the document from an external file.
    # The document begins with YAML dictionary terminated by a line
    # containing three dots. The subsequent content is stored in
    # the dictionary's 'template' field. The file name is stored
    # in the 'filename' field so that we can re-generate the original
    # filesystem layout in Module::serialize_to_disk.
    if isinstance(doc, str):
        error_message_name += " ({})".format(doc)

        # Read the external file.
        blob = app.read_file(doc)

        # Split the file on the first ocurrence of three dots. This
        # is YAML's standard end-of-stream marker. But PyYAML doesn't
        # have a way to read just up to the "...", so we handle that
        # ourselves.
        sep = "\n...\n"
        if sep not in blob:
            raise ValidationError(error_message_name, "File does not contain a line with just '...'.")
        data, template = blob.split(sep, 1)

        # Parse the YAML above the "...".
        data = rtyaml.load(data)

        # Trim the template so that it looks good if the revised
        # module spec is serialized to YAML.
        template = template.rstrip() + "\n"

        # If the template format is json or yaml, then parse that format.
        # Other template formats are loaded as strings.
        try:
            if data.get("format") == "json":
                template = json.loads(template)
            if data.get("format") == "yaml":
                template = rtyaml.load(template)
        except Exception as e:
            raise ValidationError(error_message_name, "Invalid %s template syntax: %s" % (data["format"], str(e)))

        # Store the filename and template in it.
        data['filename'] = doc
        data['template'] = template
        doc = data

    # Check that the template is valid.
    try:
        render_content(doc, None, "PARSE_ONLY", "(document template)")
    except KeyError as e:
        raise ValidationError(error_message_name, "Missing field: %s" % str(e))
    except ValueError as e:
        raise ValidationError(error_message_name, "Invalid template: %s" % str(e))

    return doc


def validate_question(mspec, spec):
    if not spec.get("id"):
        raise ValidationError("module questions", "A question is missing an id.")

    def invalid(msg):
        raise ValidationError("question %s" % spec['id'], msg)

    # clone dict before updating
    spec = OrderedDict(spec)

    # Since question IDs become Jinja2 identifiers, they must be valid
    # Jinaj2 identifiers. http://jinja.pocoo.org/docs/2.9/api/#notes-on-identifiers
    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", spec["id"]):
        invalid("The question ID may only contain ASCII letters, numbers, and underscores, and the first character must be a letter or underscore.")
        
    # Perform type conversions, validation, and fill in some defaults in the YAML
    # schema so that the values are ready to use in the database.
    if spec.get("type") == "multiple-choice":
        # validate and type-convert min and max

        spec["min"] = spec.get("min", 0)
        if not isinstance(spec["min"], int) or spec["min"] < 0:
            invalid("min must be a positive integer")

        spec["max"] = None if ("max" not in spec) else spec["max"]
        if spec["max"] is not None:
            if not isinstance(spec["max"], int) or spec["max"] < 0:
                invalid("max must be a positive integer")
            if not isinstance(spec["max"], int) or spec["max"] < spec["min"]:
                invalid("max must be an integer greater than or equal to min")

    elif spec.get("type") == "datagrid":
        # validate and type-convert min and max

        spec["min"] = spec.get("min", 0)
        if not isinstance(spec["min"], int) or spec["min"] < 0:
            invalid("min must be a positive integer")

        spec["max"] = None if ("max" not in spec) else spec["max"]
        if spec["max"] is not None:
            if not isinstance(spec["max"], int) or spec["max"] < 0:
                invalid("max must be a positive integer")
            if not isinstance(spec["max"], int) or spec["max"] < spec["min"]:
                invalid("max must be an integer greater than or equal to min")

    elif spec.get("type") in ("module", "module-set"):
        if "module-id" in spec:
            # Resolve the relative module ID to an absolute path relative
            # to the root of this app. It's optional because a protocol
            # can be specified instead.
            spec["module-id"] = resolve_relative_module_id(mspec, spec.get("module-id"))
        if "protocol" in spec:
            if isinstance(spec["protocol"], str):
                # If a single protocol is given, turn it into a list of one.
                spec["protocol"] = [spec["protocol"]]
            elif isinstance(spec["protocol"], list):
                # If it's a list, the values must be strings.
                for x in spec["protocol"]:
                    if not isinstance(x, str):
                        invalid("Protocol value must be a string (not %s)." % repr(x))
            else:
                invalid("Protocol must be either a string or a list of strings.")
        if ("module-id" not in spec and "protocol" not in spec) or ("module-id" in spec and "protocol" in spec):
            invalid("Question must have either a module-id or protocol field.")

    elif spec.get("type") == None:
        invalid("Question is missing a type.")

    # Check that required fields are present.

    if not isinstance(spec.get("title"), str):
        invalid("Question title is missing or has an invalid data type (must be a string).")
    
    if spec.get("prompt") is None:
        # Prompts are optional in project and system modules but required elsewhere.
        if mspec.get("type") not in ("project", "system-project"):
            invalid("Question prompt is missing.")

    # Check that the prompt, placeholder, and default are valid Jinja2 templates.
    for field in ("prompt", "placeholder", "default"):
        if field not in spec: continue
        if not isinstance(spec.get(field), str):
            invalid("Question %s must be a string, not a %s." % (field, type(spec.get(field)).__name__))
        try:
            render_content({
                    "format": "markdown",
                    "template": spec[field],
                },
                None, "PARSE_ONLY", "(question %s)" % field)
        except ValueError as e:
            invalid("Question %s is an invalid Jinja2 template: %s" % (field, e))

    # Validate impute conditions.
    imputes = spec.get("impute", [])
    if not isinstance(imputes, list):
        invalid("Impute's value must be a list.")
    for i, rule in enumerate(imputes):
        def invalid_rule(msg):
            raise ValidationError(mspec['id'] + " question %s, impute condition %d" % (spec['id'], i+1), msg)

        # Check that the condition is a string, and that it's a valid Jinja2 expression.
        # The condition can be omitted (it means "always true").
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment()
        if "condition" in rule:
            if not isinstance(rule.get("condition"), str):
                invalid_rule("Impute condition must be a string, not a %s." % type(rule["condition"]).__name__)
            try:
                env.compile_expression(rule["condition"])
            except Exception as e:
                invalid_rule("Impute condition %s is an invalid Jinja2 expression: %s." % (repr(rule["condition"]), str(e)))

        # Check that the value is valid. If the value-mode is raw, which
        # is the default, then any Python/YAML value is valid --- but it
        # most be present. The "expression" mode requires a valid Jinja2
        # expression, which we can check. The "template" mode requires
        # a valid Jinaja2 template.
        if "value" not in rule:
            invalid_rule("Impute condition value is missing.")
        if rule.get("value-mode") == "expression":
            try:
                env.compile_expression(rule["value"])
            except Exception as e:
                invalid_rule("Impute condition value %s is an invalid Jinja2 expression: %s." % (repr(rule["value"]), str(e)))
        if rule.get("value-mode") == "template":
            try:
                env.from_string(rule["value"])
            except Exception as e:
                invalid_rule("Impute condition value %s is an invalid Jinja2 template: %s." % (repr(rule["value"]), str(e)))
    
    return spec


def resolve_relative_module_id(within_module, module_id):
    # Module IDs specified in the YAML are relative to the directory in which
    # they are found. Unless they start with '/'.
    # See modules.Module.getReferenceTo for the inverse function.
    if module_id.startswith("/"):
        return module_id[1:]
    return "/".join(within_module["id"].split("/")[:-1] + [module_id])


