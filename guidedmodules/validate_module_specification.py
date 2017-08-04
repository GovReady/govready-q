# This module provides a single function that validates a module YAML file
# and normalizes some fields like setting a missing 'min' on a multiple-choice
# question to 0.

import re

from guidedmodules.module_logic import render_content

class ValidationError(ValueError):
    def __init__(self, context, message):
        self.context = context
        self.message = message
    def __str__(self):
        return self.context + ": " + self.message

def validate_module(spec):
    # Validate that the introduction and output documents are renderable.
    if "introduction" in spec:
        if not isinstance(spec["introduction"], dict):
            raise ValidationError("module introduction", "Must be a dictionary, not a %s." % str(type(spec["introduction"])))
        try:
            render_content(spec["introduction"], None, "PARSE_ONLY", "(introduction)")
        except ValueError as e:
            raise ValidationError("module introduction", "Invalid Jinja2 template: " + str(e))

    if not isinstance(spec.get("output", []), list):
        raise ValidationError("module output", "Must be a list, not a %s." % str(type(spec.get("output"))))
    for i, doc in enumerate(spec.get("output", [])):
        try:
            render_content(doc, None, "PARSE_ONLY", "(output document)")
        except ValueError as e:
            raise ValidationError("output document #%d" % (i+1), "Invalid Jinja2 template: %s" % str(e))

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

    # Validate the questions.
    if not isinstance(spec.get("questions"), list):
        raise ValidationError("module questions", "Invalid value for 'questions'.")
    for i, q in enumerate(spec.get("questions", [])):
    	spec["questions"][i] = validate_question(spec, spec["questions"][i])


    return spec

def validate_question(mspec, spec):
    if not spec.get("id"):
        raise ValidationError("module questions", "A question is missing an id.")

    def invalid(msg):
        raise ValidationError("question %s" % spec['id'], msg)

    # clone dict before updating
    spec = dict(spec)

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
    
    elif spec.get("type") in ("module", "module-set"):
        if "module-id" in spec:
            # Resolve the relative module ID to an absolute path relative
            # to the root of this app. It's optional because a protocol
            # can be specified instead.
            spec["module-id"] = resolve_relative_module_id(mspec, spec.get("module-id"))
        elif "protocol" in spec:
            pass
        else:
            invalid("Question must have a module-id or protocol field.")

    elif spec.get("type") == None:
        invalid("Question is missing a type.")

    # Check that required fields are present.
    if spec.get("prompt") is None:
        # Prompts are optional in project and system modules but required elsewhere.
        if mspec.get("type") not in ("project", "system-project"):
            invalid("Question prompt is missing.")

    # Check that the prompt, placeholder, and default are valid Jinja2 templates.
    for field in ("prompt", "placeholder", "default"):
        if field not in spec: continue
        if not isinstance(spec.get(field), str):
            invalid("Question %s must be a string, not a %s." % (field, str(type(spec.get(field)))))
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
            raise ValidationError(mspec['id'], "question %s, impute condition %d" % (spec['id'], i+1), msg)

        # Check that the condition is a string, and that it's a valid Jinja2 expression.
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment()
        if "condition" in rule:
            if not isinstance(rule.get("condition"), str):
                invalid_rule("Impute condition must be a string, not a %s." % str(type(rule["condition"])))
            try:
                env.compile_expression(rule["condition"])
            except Exception as e:
                invalid_rule("Impute condition %s is an invalid Jinja2 expression: %s." % (repr(rule["condition"]), str(e)))

        # Check that the value is valid. If the value-mode is raw, which
        # is the default, then any Python/YAML value is valid. We only
        # check expression values.
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
    if module_id.startswith("/"):
        return module_id[1:]
    return "/".join(within_module["id"].split("/")[:-1] + [module_id])


