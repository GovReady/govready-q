def next_question(module, questions_answered):
    # Compute the next question to ask the user, given the user's
    # answers to questions so far.
    #
    # To figure this out, we start by looking for all questions
    # that actually appear in the output template. Then we walk
    # the dependencies backward until we arrive at questions that
    # have no unanswered dependent questions. Such questions can
    # be put forth to the user.

    # What questions are actually used in the template?

    from jinja2 import meta
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    needs_answer = [ ]
    for d in module.spec["output"]:
        ast = env.parse(d['template'])
        needs_answer.extend([
            module.questions.get(key=qid)
            for qid in meta.find_undeclared_variables(ast)
            if module.questions.filter(key=qid).exists()
        ])

    # Process the questions.

    can_answer = []
    already_processed = set()

    def is_answered(q):
        # Is q answered yet? Yes if the user has provided
        # an answer, or if one of its impute conditions is
        # met.
        return q.key in questions_answered.answers \
          or impute_answer(q, questions_answered)

    while len(needs_answer) > 0:
        # Get the next question to look at.

        q = needs_answer.pop(0)

        if is_answered(q) or q.id in already_processed:
            # This question is already answered or we've already
            # processed its dependencies, so we can skip.
            continue
        already_processed.add(q.id)

        # What unanswered dependencies does it have?

        deps = list(filter(
            lambda d : not is_answered(d),
            get_question_dependencies(q)))

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

def render_content(content, answers, output_format, additional_context={}):
    # Renders content (which is a dict with keys "format" and "template")
    # into HTML, using the ModuleAnswers in answers to provide the template
    # context.

    # Ensure imputed answers are computed.
    answers.add_imputed_answers()

    if content["format"] == "html":
        def escapefunc(s):
            # Ensure that variables are substituted with HTML escapes. We do
            # the escaping ourself because Jinja2 can't handle escaping for
            # other formats, and we use the __html__ method on RenderedAnswer
            # to provide pre-escaped content.
            import html
            return html.escape(s)
        def renderer(output):
            if output_format == "html":
                # It's already HTML.
                return output
            raise ValueError("Can't render HTML template as %s." % output_format)

    elif content["format"] == "markdown":
        def escapefunc(s):
            # Punctuation can, and unless we know better, must be backslash-escaped.
            escape_chars = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
            return "".join(("\\" if c in escape_chars else "") + c for c in s)
        def renderer(output):
            if output_format == "html":
                # Convert CommonMark to HTML.
                import CommonMark
                return CommonMark.commonmark(output)
            raise ValueError("Can't render Markdown template as %s." % output_format)

    elif content["format"] == "text":
        def escapefunc(s):
            # Don't perform any escaping.
            return s
        def renderer(output):
            if output_format == "text":
                return output
            if output_format == "html":
                # HTML-escape the final output and wrap it in a <pre> tag.
                import html
                return "<pre>" + html.escape(output) + "</pre>"
            raise ValueError("Can't render text template as %s." % output_format)

    elif content["format"] in ("json", "yaml"):
        # Ok this is totally different. The template content
        # isn't a string -- it's a Python data structure. Replace
        # all of the strings in the Python data structure using
        # render_content.
        from collections import OrderedDict
        def walk(value):
            if isinstance(value, str):
                return render_content(
                    {
                        "format": "text",
                        "template": value
                    },
                    answers,
                    "text",
                    additional_context,
                )
            elif isinstance(value, list):
                return [walk(i) for i in value]
            elif isinstance(value, dict):
                return OrderedDict([ (k, walk(v)) for k, v in value.items() ])
            else:
                # Leave unchanged.
                return value

        # Render strings within the data structure.
        value = walk(content["template"])

        # Render to JSON or YAML.
        if content["format"] == "json":
            import json
            output = json.dumps(value, indent=True)
        elif content["format"] == "yaml":
            import rtyaml
            output = rtyaml.dump(value)

        # Convert to HTML.
        if output_format == "html":
            import html
            output = "<pre>" + html.escape(output) + "</pre>"

        # Return and skip all of the logic below.
        return output

    else:
        raise ValueError(content["format"])

    # Create an intial context dict.
    context = dict(additional_context) # clone

    # Add rendered answers to it.
    context.update(answers.get_template_context(escapefunc))

    # Evaluate the template. Ensure autoescaping is turned on. Even though
    # we handle it ourselves, we do so using the __html__ method on
    # RenderedAnswer, which relies on autoescaping logic. This also lets
    # the template writer disable autoescaping with "|safe".
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment(autoescape=True)
    template = env.from_string(content["template"])
    output = template.render(context)

    # Apply the renderer which turns the template output into HTML.
    output = renderer(output)
    return output

def get_question_dependencies(question):
    return []

def impute_answer(question, answers):
    # Check if any of the impute conditions are met based on
    # the questions that have been answered so far and return
    # the imputed value.
    from jinja2 import meta
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    for rule in question.spec.get("impute", []):
        condition_func = env.compile_expression(rule["condition"])
        if condition_func(answers.answers):
            # The condition is met. Return the imputed value.
            return rule["value"]
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

    def validate_longtext(question, value):
        if value == "":
            raise ValueError("empty")
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

    def validate_module(question, value):
        # handled by view function
        return value

def get_question_choice(question, key):
    for choice in question.spec["choices"]:
        if choice["key"] == key:
            return choice
    raise KeyError(repr(key) + " is not a choice")

class ModuleAnswers:
    def __init__(self, module, answers):
        self.module = module
        self.answers = answers

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
        for q in self.module.questions.order_by('definition_order'):
            v = impute_answer(q, self)
            if v:
                self.answers[q.key] = v

    def get_template_context(self, escapefunc = lambda x : x):
        # Replace values with RenderedAnswer instances which take
        # care of converting raw data values into what we want for
        # rendering in templates.
        ret = { }
        for qid, value in self.answers.items():
            q = self.module.questions.get(key=qid)
            if q.spec["type"] == "module":
                ret[qid] = value.get_template_context(escapefunc)
            else:
                ret[qid] = RenderedAnswer(q, value, escapefunc)
        return ret

    def render_output(self, additional_context):
        # Now that all questions have been answered, generate this
        # module's output. The output is a set of documents.
        return [
            {
                "name": d.get("name", "Document"),
                "html": render_content(d, self, "html", additional_context)
            }
            for d in self.module.spec["output"]
        ]


class RenderedAnswer:
    def __init__(self, question, answer, escapefunc):
        self.question = question
        self.answer = answer
        self.escapefunc = escapefunc
        self.question_type = self.question.spec["type"]

    def __html__(self):
        # How the template renders a question variable.
        return self.escapefunc(str(self))

    def __str__(self):
        if self.question_type == "yesno":
            return "Yes" if self.answer == "yes" else "No"
        if self.question_type == "choice":
            return get_question_choice(self.question, self.answer)["text"]
        if self.question_type == "multiple-choice":
            return ", ".join(get_question_choice(self.question, c)["text"] for c in self.answer)
        return str(self.answer)

    def __bool__(self):
        # How the template converts a question variable to
        # a boolean within an expression (i.e. within an if).
        if self.question_type == "yesno":
            return self.answer == "yes"
        return bool(self.answer)

    def __iter__(self):
        if self.question_type == "multiple-choice":
            # Iterate by creating a RenderedAnswer for each choice key
            # with a made-up Question instance.
            from .models import ModuleQuestion
            return (
                RenderedAnswer(ModuleQuestion(spec={
                    "type": "choice",
                    "choices": self.question.spec["choices"],
                    }),
                ans, self.escapefunc)
                for ans in self.answer)
        raise TypeError("Answer of type %s is not iterable." % self.question_type)

    @property # if not @property, it renders as "bound method" by jinja template
    def key(self):
        if self.question_type in ("yesno", "choice", "multiple-choice"):
            return self.answer
        raise Exception(".key is not a sensible operation for the %s question type." % self.question_type)
