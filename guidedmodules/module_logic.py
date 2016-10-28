def get_jinja2_template_vars(template):
    from jinja2 import meta
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    return set(meta.find_undeclared_variables(env.parse(template)))

def next_question(questions_answered, required=False, unanswered=None):
    # Compute the next question to ask the user, given the user's
    # answers to questions so far.
    #
    # To figure this out, we start by looking for all questions
    # that actually appear in the output template. Then we walk
    # the dependencies backward until we arrive at questions that
    # have no unanswered dependent questions. Such questions can
    # be put forth to the user.

    # What questions are actually used in the template?

    needs_answer = get_questions_used_in_output(questions_answered.module)

    # Add imputed question. Since an imputed answer can lead to the
    # imuputing of another question, they all have to be evaluated
    # up front.
    questions_answered.add_imputed_answers()

    # Process the questions.

    can_answer = []
    already_processed = set()

    def is_answered(q):
        # Is q answered yet? Yes if the user has provided
        # an answer, or if one of its impute conditions is
        # met. In either case, the answer will be set already.
        if q.key in questions_answered.answers:
            # If q is a required question and the required
            # argument is true, then require that it not
            # be skipped.
            if q.spec.get("required") and required and questions_answered.answers[q.key] is None:
                return False
            return True
        return False

    while len(needs_answer) > 0:
        # Get the next question to look at.

        q = needs_answer.pop(0)
        if is_answered(q) or q.id in already_processed:
            # This question is already answered or we've already
            # processed its dependencies, so we can skip.
            continue
        already_processed.add(q.id)

        # Remember that this question is as-yet unanswered.
        if unanswered is not None:
            unanswered.append(q)

        # What unanswered dependencies does it have?

        deps = get_question_dependencies(q)
        deps = list(filter(lambda d : not is_answered(d), deps))

        if len(deps) == 0:
            # All of this question's dependent questions are answered,
            # so this question can be answered.
            can_answer.append(q)

        else:
            # The unanswered dependent questions must be answered first.
            needs_answer.extend(deps)

    # If there is nothing for the user to answer, then this module
    # is finished --- the user answered everything.
    if len(can_answer) == 0:
        return None

    # There may be multiple routes through the tree of questions,
    # so we'll choose the question that is defined first in the spec.
    can_answer.sort(key = lambda q : q.definition_order)
    return can_answer[0]

def get_question_context(answers, question):
    # What is the context of questions around the given question?

    def annotate(q):
        return {
            "class": "this" if q.key == question.key else "other",
            "key": q.key,
            "title": q.spec['title'],
            "answered": q.key in answers.answers and q.key != question.key,
        }

    # What questions still need to be answered?
    future_questions = []
    next_question(answers, unanswered=future_questions)
    future_questions.reverse()

    # Not including this one.
    future_questions = list(filter(lambda q : q.key != question.key, future_questions))

    # Which questions were recently answered that are not future questions
    # according to the dependency tree.
    past_questions = []
    for ans in answers.task.answers.order_by('created'):
        q = ans.question
        if q not in future_questions and q.key != question.key and q.key not in answers.was_imputed:
            past_questions.append(q)

    return list(map(annotate, past_questions + [question] + future_questions))


def render_content(content, answers, output_format, source, additional_context={}, hard_fail=True):
    # Renders content (which is a dict with keys "format" and "template")
    # into the requested output format, using the ModuleAnswers in answers
    # to provide the template context.

    # Ensure imputed answers are computed.
    answers.add_imputed_answers()

    # Get the template.
    template_format = content["format"]
    template_body = content["template"]

    # Markdown cannot be used with Jinja2 because auto-escaping is highly
    # context dependent. For instance, Markdown can have HTML literal blocks
    # and in those blocks the usual backslash-escaping is replaced with
    # HTML's usual &-escaping. Also, when a template value is substituted
    # inside a Markdown block like a blockquote, newlines in the substituted
    # value will break the logical structure of the template without some
    # very complex handling of adding line-initial whitespace and block
    # markers ("*", ">").
    #
    # So we must convert Markdown to another format prior to running templates.
    #
    # If the output format is HTML, convert the Markdown to HTML.
    #
    # If the output format is plain-text, treat the Markdown as if it is plain text.
    #
    # No other output formats are supported.
    if template_format == "markdown":
        if output_format == "html":
            # Convert the template first to HTML using CommonMark.
            
            # But we don't want CommonMark to process template tags because if
            # there are HTML symbols like ", <, and > within the tag --- which
            # have meaning to Jinaj2, then they may get ruined by CommonMark
            # because they may be escaped.
            #
            # Do a simple lexical pass over the template and replace template
            # tags with a special code that CommonMark will ignore. We'll put
            # back the strings after.
            if not isinstance(template_body, str): raise ValueError("Template %s has incorrect type: %s" % (source, type(template_body)))
            substitutions = []
            import re
            def replace(m):
                # Record the substitution.
                index = len(substitutions)
                substitutions.append(m.group(0))
                return "\uE000%d\uE001" % index # use Unicode private use area code points
            template_body = re.sub("{%.*?%}|{{.*?}}", replace, template_body)

            # Render with a custom renderer to control output.
            import CommonMark
            class q_renderer(CommonMark.HtmlRenderer):
                def heading(self, node, entering):
                    # Generate <h#> tags with one level down from
                    # what would be normal since they should not
                    # conflict with the page <h1>.
                    if entering:
                        node.level += 1
                    super().heading(node, entering)
                def link(self, node, entering):
                    # Rewrite the target URL to be within the app's
                    # static virtual path.
                    if entering:
                        self.rewrite_url(node)
                    super().link(node, entering)
                def image(self, node, entering):
                    # Rewrite the image URL to be within the app's
                    # static virtual path.
                    if entering:
                        self.rewrite_url(node)
                    super().image(node, entering)
                def rewrite_url(self, node):
                    import urllib.parse
                    base_path = "/static/module-assets/"
                    if not node.destination.startswith("/"):
                        # Assets are relative to the module's 'path'.
                        base_path += "/".join(answers.module.key.split("/")[0:-1]) + "/"
                    node.destination = urllib.parse.urljoin(base_path, node.destination)

            template_format = "html"
            template_body = q_renderer().render(CommonMark.Parser().parse(template_body))

            # Put the Jinja2 template tags back that we removed prior to running
            # the CommonMark renderer.
            def replace(m):
                return substitutions[int(m.group(1))]
            template_body = re.sub("\uE000(\d+)\uE001", replace, template_body)

        elif output_format == "text":
            # When rendering a Markdown template for plain-text output, we can just
            # pass the Markdown directly as if it were plain-text. Auto-escaping is
            # turned off in this mode.
            template_format = "text"

        else:
            raise ValueError("Cannot render a markdown template to %s in %s." % (output_format, source))

    # Execute the template.

    if template_format in ("json", "yaml"):
        # The json and yaml template types are not rendered in the usual
        # way. The template itself is a Python data structure (not a string).
        # We will replace all string values in the data structure (except
        # dict keys) with what we get by calling render_content recursively
        # on the string value, assuming it is a template of plain-text type.

        from collections import OrderedDict

        def walk(value, path):
            if isinstance(value, str):
                return render_content(
                    {
                        "format": "text",
                        "template": value
                    },
                    answers,
                    "text",
                    source + " " + "->".join(path),
                    additional_context,
                )
            elif isinstance(value, list):
                return [walk(i, path+[str(i)]) for i in value]
            elif isinstance(value, dict):
                return OrderedDict([ (k, walk(v, path+[k])) for k, v in value.items() ])
            else:
                # Leave unchanged.
                return value

        # Render strings within the data structure.
        value = walk(template_body, [])

        # Render to JSON or YAML depending on what was specified on the
        # template.
        if template_format == "json":
            import json
            output = json.dumps(value, indent=True)
        elif template_format == "yaml":
            import rtyaml
            output = rtyaml.dump(value)

        if output_format == "html":
            # Convert to HTML.
            import html
            return "<pre>" + html.escape(output) + "</pre>"
        elif output_format == "text":
            # Treat as plain text.
            return output
        else:
            raise ValueError("Cannot render %s to %s in %s." % (template_format, output_format, source))

    elif template_format in ("text", "html"):
        # The plain-text and HTML template types are rendered using Jinja2.
        #
        # The only difference is in how escaping of substituted variables works.
        # For plain-text, there is no escaping. For HTML, we render 'longtext'
        # anwers as if the user was typing Markdown. That makes sure that
        # paragraphs aren't collapsed in HTML, and gives us other benefits.
        # For other values we perform standard HTML escaping.

        if template_format == "text":
            def escapefunc(s, is_longtext):
                # Don't perform any escaping.
                return s
    
        elif template_format == "html":
            def escapefunc(s, is_longtext):
                if not is_longtext:
                    import html
                    return html.escape(s)
                else:
                    import CommonMark
                    return CommonMark.HtmlRenderer().render(CommonMark.Parser().parse(s))

        # Execute the template.

        # Create an intial context dict and add rendered answers into it.
        context = dict(additional_context) # clone
        context.update(TemplateContext(answers, escapefunc))

        # Evaluate the template. Ensure autoescaping is turned on. Even though
        # we handle it ourselves, we do so using the __html__ method on
        # RenderedAnswer, which relies on autoescaping logic. This also lets
        # the template writer disable autoescaping with "|safe".
        import jinja2
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment(
            autoescape=True,

            # if hard_fail is True, then raise an error if any variable used
            # in the template is undefined (i.e. answer is not present in
            # dict), otherwise let it pass through silently
            undefined=jinja2.StrictUndefined if hard_fail else jinja2.Undefined,
            )
        try:
            template = env.from_string(template_body)
        except jinja2.TemplateSyntaxError as e:
            raise ValueError("There was an error loading the template %s: %s" % (source, str(e)))
        try:
            output = template.render(context)
        except Exception as e:
            raise ValueError("There was an error executing the template %s: %s" % (source, str(e)))

        # Convert the output to the desired output format.

        if template_format == "text":
            if output_format == "text":
                # text => text (nothing to do)
                return output
            elif output_format == "html":
                # convert text to HTML by ecaping and wrapping in a <pre> tag
                import html
                return "<pre>" + html.escape(output) + "</pre>"
        elif template_format == "html":
            if output_format == "html":
                # html => html (nothing to do)
                return output

        raise ValueError("Cannot render %s to %s." % (template_format, output_format))
         
    else:
        raise ValueError("Invalid template format encountered: %s." % template_format)


def get_questions_used_in_output(module):
    questions = []
    for d in module.spec.get("output", []):
        questions.extend([
            module.questions.get(key=qid)
            for qid in get_jinja2_template_vars(d['template'])
            if module.questions.filter(key=qid).exists()
        ])
    return questions

def get_question_dependencies(question):
    return set(edge[1] for edge in get_question_dependencies_with_type(question))

def get_question_dependencies_with_type(question):
    # Returns a set of ModuleQuestion instances that this question is dependent on.
    ret = []
    
    # All questions mentioned in prompt text become dependencies.
    for qid in get_jinja2_template_vars(question.spec.get("prompt", "")):
        ret.append(("prompt", qid))

    # All questions mentioned in the impute conditions become dependencies.
    # And when impute values are expressions, then similarly for those.
    for rule in question.spec.get("impute", []):
        for qid in get_jinja2_template_vars(
                r"{% if " + rule["condition"] + r" %}...{% endif %}"
                ):
            if rule.get("value") is None:
                ret.append(("skip-condition", qid))
            else:
                ret.append(("impute-condition", qid))

        if rule.get("value-type") == "expression":
            for qid in get_jinja2_template_vars(
                    r"{% if " + rule["value"] + r" %}...{% endif %}"
                    ):
                ret.append(("impute-value", qid))

    # Other dependencies can just be listed.
    for qid in question.spec.get("ask-first", []):
        ret.append(("ask-first", qid))

    # Turn IDs into ModuleQuestion instances.
    return [ (edge_type, question.module.questions.get(key=qid))
         for (edge_type, qid) in ret
         if question.module.questions.filter(key=qid).exists()
       ]

def impute_answer(question, context):
    # Check if any of the impute conditions are met based on
    # the questions that have been answered so far and return
    # the imputed value. Be careful about values like 0 that
    # are false-y --- must check for "is None" to know if
    # something was imputed or not.
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    for rule in question.spec.get("impute", []):
        condition_func = env.compile_expression(rule["condition"])
        if condition_func(context):
            # The condition is met. Compute the imputed value.
            if rule.get("value-mode", "raw") == "raw":
                # Imputed value is the raw YAML value.
                value = rule["value"]
            elif rule.get("value-mode", "raw") == "expression":
                value = env.compile_expression(rule["value"])(context)
                if isinstance(value, RenderedAnswer):
                    # Unwrap.
                    value =  value.answer
                elif hasattr(value, "as_raw_value"):
                    # RenderedProject, RenderedOrganization
                    value = value.as_raw_value()
            else:
                raise ValueError("Invalid impute condition value-mode.")

            # Since the imputed value may be None, return
            # the whole thing in a tuple to distinguish from
            # a None indicating the lack of an imputed value.
            return (value,)
    return None

class validator:
    @staticmethod
    def validate(question, value):
        validate_func = getattr(validator, "validate_" + question.spec["type"].replace("-", "_"))
        return validate_func(question, value)

    def validate_text(question, value):
        if value == "":
            raise ValueError("empty")
        return value

    def validate_password(question, value):
        if value == "":
            raise ValueError("empty")
        return value

    def validate_email_address(question, value):
        import email_validator
        return email_validator.validate_email(value)["email"]

    def validate_url(question, value):
        if value == "":
            raise ValueError("empty")
        from django.core.validators import URLValidator
        validator = URLValidator()
        try:
            validator(value)
        except:
            raise ValueError("That is not a valid web address.")
        return value

    def validate_longtext(question, value):
        if value == "":
            raise ValueError("empty")
        return value

    def validate_date(question, value):
        # Validate that we have a valid date in YYYY-MM-DD format. A client-side
        # tool should be responsible for ensuring that the user entry is translated
        # into this format.
        import re, datetime
        if value == "":
            raise ValueError("empty")
        m = re.match("(\d\d\d\d)-(\d\d)-(\d\d)$", value)
        if not m:
            raise ValueError("Date is not in YYYY-MM-DD format.")
        # Convert to ints, raising ValueError if they are not.
        try:
            year, month, date = [int(x) for x in m.groups()]
        except ValueError:
            raise ValueError("Date is not in YYYY-MM-DD format.")
        # Instantiate a datetime.date object. It will raise a ValueError if the
        # year, month, or day is out of range.
        datetime.date(year, month, date)
        return value

    def validate_choice(question, value):
        if value not in { choice['key'] for choice in question.spec["choices"] }:
            raise ValueError("invalid choice")
        return value

    def validate_yesno(question, value):
        if value not in ("yes", "no"):
            raise ValueError("invalid choice")
        return value

    def validate_multiple_choice(question, value):
        # Comes in from the view function as an array.
        for item in value:
            if item not in { choice['key'] for choice in question.spec["choices"] }:
                raise ValueError("invalid choice: " + item)
        if len(value) < question.spec.get("min", 0):
            raise ValueError("not enough choices")
        if question.spec.get("max") and len(value) > question.spec["max"]:
            raise ValueError("too many choices")
        return value

    def validate_integer(question, value):
        # First validate as a real so we don't have to duplicate those tests.
        # We get back a float.
        value = validator.validate_real(question, value)

        # Then ensure is an integer.
        if value != int(value):
            raise ValueError("Invalid input. Must be a whole number.")

        return int(value)

    def validate_real(question, value):
        if value == "":
            raise ValueError("empty")

        try:
            # Use a locale to parse human input since it may have
            # e.g. thousands-commas.
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 
            value = locale.atof(value)
        except ValueError:
            # make a nicer error message
            raise ValueError("Invalid input. Must be a number.")

        if "min" in question.spec and value < question.spec["min"]:
            raise ValueError("Must be at least %g." % question.spec["min"])
        if "max" in question.spec and value > question.spec["max"]:
            raise ValueError("Must be at most %g." % question.spec["max"])

        return value

    def validate_file(question, value):
        # None is an acceptable value: It means to preserve
        # an existing answer.
        if value is None:
            return value

        # Otherwise, the file must have content.
        if value.size == 0:
            raise ValueError("File is empty.")

        # If the file is expected to be an image, then load it to ensre it is
        # a valid image, and sanitize it by round-tripping it through Pillow.
        # This purposefully is intended to lose image metadata, to protect
        # the user. (TODO: Test that it actually drops XMP metadata.)
        if question.spec.get("file-type") == "image":
            # Load the image.
            from PIL import Image
            try:
                im = Image.open(value.file)
            except:
                raise ValueError("That's not an image file.")

            imspec = question.spec.get("image", {})
            
            # Apply a size constraint and resize the image in-place.
            if imspec.get("max-size"):
                # TODO: Validate the size width/height fields are integers.
                size = imspec["max-size"]
                im.thumbnail(( size.get("width", im.size[0]), size.get("width", im.size[1])  ))

            # Write the image back to a new Django ContentFile instance.
            from io import BytesIO
            buf = BytesIO()
            im.save(buf, "PNG")

            from django.core.files.base import ContentFile
            value = ContentFile(buf.getvalue())
            value.name = "image.png" # needs a name for the storage backend?


        return value

    def validate_module(question, value):
        # handled by view function
        return value

    def validate_interstitial(question, value):
        # interstitials have no actual answer - we should always
        # get "".
        if value != "":
            raise ValueError("Invalid input.")
        return None # store it as null

    def validate_external_function(question, value):
        # the user doesn't answer these directly
        if value != "":
            raise ValueError("Invalid input.")
        return None # doesn't matter

def get_question_choice(question, key):
    for choice in question.spec["choices"]:
        if choice["key"] == key:
            return choice
    raise KeyError(repr(key) + " is not a choice")

class ModuleAnswers:
    """Represents a set of answers to a Task."""

    def __init__(self, module, task, answers):
        self.module = module
        self.task = task
        self.answers = answers
        self.has_imputed_answers = False

    def add_imputed_answers(self):
        # Set (and override) any answers with inputed answers. Imputed
        # answers take precedence over explicit answers because the
        # explicit answers were probably entered before another answer
        # was changed to allow for the original answer to be imputed.
        # It's in a consistent state only when we take the imputed
        # answers.
        #
        # Proceed in order (?) in case there are dependencies between
        # imputations. TODO: This should follow the dependency chain
        # defined by next_question.
        if self.has_imputed_answers: return # already done
        self.was_imputed = set()
        context = TemplateContext(self, str)
        for q in self.module.questions.order_by('definition_order'):
            import jinja2.exceptions
            try:
                v = impute_answer(q, context)
                if v :
                    self.answers[q.key] = v[0]
                    self.was_imputed.add(q.key)
            except jinja2.exceptions.UndefinedError:
                # If a variable is undefined, then we may be trying to
                # impute the answer to a question that depends on a question
                # that hasn't been answered yet.
                continue
        self.has_imputed_answers = True

    def render_output(self, additional_context, hard_fail=True):
        # Now that all questions have been answered, generate this
        # module's output. The output is a set of documents.
        def render_document(d, i):
            ret = { }
            ret.update(d) # keep all original fields (especially 'name', 'tab')
            ret["html"] = render_content(d, self, "html", "%s output document %d" % (repr(self.module), i), additional_context, hard_fail=hard_fail)
            return ret
        return [ render_document(d, i) for i, d in enumerate(self.module.spec.get("output", [])) ]

from collections.abc import Mapping
class TemplateContext(Mapping):
    """Provides Jinja2 template and expression variables."""

    def __init__(self, module_answers, escapefunc):
        self.module_answers = module_answers
        self.escapefunc = escapefunc
        self._cache = { }

    def __getitem__(self, item):
        if item not in self._cache:
            self._cache[item] = self.getitem(item)
        return self._cache[item]

    def getitem(self, item):
        # If 'item' matches a question ID, wrap the internal Pythonic/JSON-able value
        # with a RenderedAnswer instance which take care of converting raw data values
        # into how they are rendered in templates (escaping, iteration, property accessors)
        # and evaluated in expressions.
        question = self.module_answers.module.questions.filter(key=item).first()
        if question:
            # The question might or might not be answered. If not, its value is None.
            answer = self.module_answers.answers.get(item, None)
            return RenderedAnswer(self.module_answers.task, question, answer, self.escapefunc)

        # The context also provides the project and organization that the Task belongs to,
        # and other task attributes, assuming the keys are not overridden by question IDs.
        if self.module_answers.task:
            if item == "task_link":
                return self.module_answers.task.get_absolute_url()
            if item == "project":
                return RenderedProject(self.module_answers.task.project, self.escapefunc)
            if item == "organization":
                return RenderedOrganization(self.module_answers.task.project.organization, self.escapefunc)
            if item in ("is_started", "is_finished"):
                # These are methods on the Task instance. Don't
                # call the method here because that leads to infinite
                # recursion. Figuring out if a module is finished
                # requires imputing all question answers, which calls
                # into templates, and we can end up back here.
                return getattr(self.module_answers.task, item)
        else:
            # If there is no Task associated with this context, then we're
            # faking the attributes.
            if item in ("is_started", "is_finished"):
                return (lambda : False) # the attribute normally returns a bound function

        # The item is not something found in the context.
        raise AttributeError(item)

    def __iter__(self):
        seen_keys = set()
        for q in self.module_answers.task.module.questions.order_by('definition_order'):
            seen_keys.add(q.key)
            yield q.key
        if self.module_answers.task:
            # Attributes that are only available if there is a task.
            for attribute in ("task_link", "project", "organization"):
                if attribute not in seen_keys:
                    yield attribute
        for attribute in ("is_started", "is_finished"):
            if attribute not in seen_keys:
                yield attribute

    def __len__(self):
        return len([x for x in self])

class RenderedProject(TemplateContext):
    def __init__(self, project, escapefunc):
        self.project = project
        super().__init__(project.root_task.get_answers(), escapefunc)

    def as_raw_value(self):
        return self.project.title
    def __html__(self):
        return self.escapefunc(self.as_raw_value(), False)

class RenderedOrganization(TemplateContext):
    def __init__(self, organization, escapefunc):
        self.organization = organization
        super().__init__(organization.get_organization_project().root_task.get_answers(), escapefunc)

    def as_raw_value(self):
        return self.organization.name
    def __html__(self):
        return self.escapefunc(self.as_raw_value(), False)

class RenderedAnswer:
    def __init__(self, task, question, answer, escapefunc):
        self.task = task
        self.question = question
        self.answer = answer
        self.escapefunc = escapefunc
        self.question_type = self.question.spec["type"]

    def __html__(self):
        # How the template renders a question variable used plainly, i.e. {{q0}}.
        if self.answer is None:
            value = "<%s>" % self.question.spec['title']
        elif self.question_type == "multiple-choice":
            # Render multiple-choice as a comma+space-separated list
            # of the choice keys.
            value = ", ".join(self.answer)
        elif self.question_type == "module":
            return self.text
        else:
            # For all other question types, just call Python str().
            value = str(self.answer)

        # And in all cases, escape the result.
        return self.escapefunc(value, self.question_type == "longtext")

    @property
    def text(self):
        # How the template renders {{q0.text}} to get a nice display form of the answer.
        if self.answer is None:
            value = "<not answered>"
        elif self.question_type == "yesno":
            value = ("Yes" if self.answer == "yes" else "No")
        elif self.question_type == "choice":
            value = get_question_choice(self.question, self.answer)["text"]
        elif self.question_type == "multiple-choice":
            value = ", ".join(get_question_choice(self.question, c)["text"] for c in self.answer)
        elif self.question_type in ("integer", "real"):
            # Use a locale to generate nice human-readable numbers.
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            value = locale.format(
                "%d" if self.question_type == "integer" else "%g",
                self.answer,
                grouping=True)
        elif self.question_type == "module":
            return self.answer.task.render_title()
        else:
            # For all other question types, just call Python str().
            value = str(self.answer)

        # Wrap the value in something that provides a __html__
        # method to override Jinja2 escaping so we can use our
        # own function.
        class SafeString:
            def __init__(self, value, escapefunc):
                self.value = value
                self.escapefunc = escapefunc
            def __html__(self):
                return self.escapefunc(value)
        return SafeString(value, lambda value : self.escapefunc(value, self.question_type == "longtext"))

    @property
    def edit_link(self):
        # Return a link to edit this question.
        return self.task.get_absolute_url_to_question(self.question)

    def rendered_outputs(self):
        if self.question_type == "module":
            try:
                return self.answer.task.render_output_documents(hard_fail=False)
            except:
                return []
        raise AttributeError()

    def __bool__(self):
        # How the template converts a question variable to
        # a boolean within an expression (i.e. within an if).
        # true.
        if self.question_type == "yesno":
            # yesno questions are true if they are answered as yes.
            return self.answer == "yes"
        else:
            # Other question types are true if they are answered.
            # (It would be bad to use Python bool() because it might
            # give unexpected results for e.g. integer/real zero.)
            return self.answer is not None

    def __iter__(self):
        if self.answer is None:
            # If the question was skipped, return a generator that
            # yields nothing --- there is nothing to iterate over.
            return (None for _ in [])

        if self.question_type == "multiple-choice":
            # Iterate by creating a RenderedAnswer for each choice key
            # with a made-up Question instance.
            from .models import ModuleQuestion
            return (
                RenderedAnswer(None, ModuleQuestion(spec={
                    "type": "choice",
                    "choices": self.question.spec["choices"],
                    }),
                ans, self.escapefunc)
                for ans in self.answer)
        
        elif self.question_type == "module-set":
            # Iterate over the sub-tasks' answers.
            def get_module(m):
                m.add_imputed_answers()
                return TemplateContext(m, self.escapefunc)
            return (get_module(v) for v in self.answer)

        elif self.question_type == "external-function":
            return iter(self.answer)

        raise TypeError("Answer of type %s is not iterable." % self.question_type)

    def __getattr__(self, item):
        # For module-type questions, provide the answers of the
        # sub-task as properties of this context variable.
        if self.question_type == "module":
            # Pass through via a temporary TemplateContext.
            if self.answer is not None:
                # If the question was not skipped, then we have the ModuleAnswers for it.
                self.answer.add_imputed_answers()
                tc = TemplateContext(self.answer, self.escapefunc)
            else:
                # The question was skipped -- i.e. we have no ModuleAnswers for
                # the question that this RenderedAnswer represents. But we want
                # to gracefully represent the item attribute as skipped too.
                tc = TemplateContext(ModuleAnswers(self.question.answer_type_module, None, {}), self.escapefunc)
            return tc[item]

        # For external-function and "raw" question types, the answer value is any
        # JSONable Python data structure. Forward the getattr request onto the value.
        # Similarly for file questions.
        elif self.question_type in ("external-function", "raw", "file"):
            if self.answer is not None:
                return self.answer[item]
            else:
                # Avoid attribute errors.
                return None

        # For other types of questions, or items that are not question
        # IDs of the subtask, just do normal Python behavior.
        return super().__getattr__(self, item)

    def __eq__(self, other):
        if isinstance(other, RenderedAnswer):
            other = other.answer
        return self.answer == other

def run_external_function(question, existing_answers):
    # Split the function name into the module path and function name.
    function_name = question.get("function", "").rsplit(".", 1)
    if len(function_name) != 2:
        raise Exception("Invalid function name.") # not trapped / not user-visible error

    # Import the module and get the method.
    import importlib
    module = importlib.import_module(function_name[0])
    method = getattr(module, function_name[1])

    # Run the method.
    return method(question, existing_answers)
