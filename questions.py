class Module(object):
    def __init__(self, spec):
        # Load from a YAML specification.
        self.id = spec["id"]
        self.title = spec["title"]
        self.answerable_in_project = spec.get("type") != "account"

        # The question definitions.
        self.questions = []
        self.questions_by_id = { }
        for qspec in spec["questions"]:
            # Parse the question spec.
            q = Question(qspec)
            q.def_index = len(self.questions)

            # What does it depend on?
            if "depends_on" not in qspec:
                # If "depends_on" is not specified, the question
                # depends on the previous one in the module, unless
                # this is the first question, which then has no
                # dependencies.
                if len(self.questions) == 0:
                    q.depends_on = []
                else:
                    q.depends_on = [self.questions[-1]]
            else:
                # depends_on is a list of question IDs that must be
                # answered first before question q.
                q.depends_on = []
                for qid in qspec["depends_on"]:
                    try:
                        q.depends_on.append(self.questions_by_id[qid])
                    except KeyError:
                        raise "depends_on references question %s which is not defined" % qid

            # Add to the module.
            self.questions.append(q)
            self.questions_by_id[q.id] = q

        # Load the introduction template.
        self.introduction = {
            "format": spec["introduction"].get("format", "text"),
            "template": spec["introduction"]["template"]
        }

        # Load the output templates.
        self.output = [
            {
                "name": d.get("name", "Document"),
                "format": d.get("format", "text"),
                "template": d["template"]
            } for d in spec.get("output", [])
        ]

    def __repr__(self):
        return "<Module '%s'>" % (self.title,)

    @staticmethod
    def get_anserable_modules():
        import glob, os.path, rtyaml
        for fn in glob.glob("modules/*.yaml"):
            m = Module(rtyaml.load(open(fn)))
            if m.answerable_in_project:
                yield m

    @staticmethod
    def load(id):
        # Sanity check id, since we're going to the filesystem.
        import re
        if re.search(r"[^a-z0-9\-_]", id):
            raise ValueError(id)

        import rtyaml
        return Module(rtyaml.load(open("modules/%s.yaml" % id)))

    def next_question(self, questions_answered):
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
        for d in self.output:
            ast = env.parse(d['template'])
            needs_answer.extend([
                self.questions_by_id[qid]
                for qid in meta.find_undeclared_variables(ast)
                if qid in self.questions_by_id
            ])

        # Process the questions.

        can_answer = []
        already_processed = set()

        def is_answered(q):
            # Is q answered yet? Yes if the user has provided
            # an answer, or if one of its skip conditions is
            # met.
            return q.id in questions_answered.answers \
              or q.impute_answer(questions_answered)

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
                q.depends_on))

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
        can_answer.sort(key = lambda q : q.def_index)
        return can_answer[0]

    def add_imputed_answers(self, answers):
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
        for q in self.questions:
            v = q.impute_answer(answers)
            if v:
                answers.answers[q.id] = v

    @staticmethod
    def render_content(content, context):
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment(autoescape=True)
        template = env.from_string(content['template'])
        output = template.render(context)
        if content["format"] == "markdown":
            import CommonMark
            output = CommonMark.commonmark(output)
        return output

    def render_introduction(self):
        return self.render_content(self.introduction, {})

    def render_output(self, answers):
        # Now that all questions have been answered, generate this
        # module's output. The output is a set of documents.
        return [
            {
                "name": d["name"],
                "html": self.render_content(d, answers)
            }
            for d in self.output
        ]

class Question(object):
    def __init__(self, spec):
        # Load from a YAML specification.
        self.id = spec["id"]
        self.title = spec["title"]
        self.prompt = spec["prompt"]
        self.type = spec["type"]
        self.impute = [(s["condition"], s["value"]) for s in spec.get("impute", [])]
        self.choices = spec.get("choices", [])
        if self.type in ("multiple-choice",):
            self.choice_selection_min = int(spec.get("min", "0"))
            self.choice_selection_max = int(spec["max"]) if spec.get("max") else None
        self.module_id = spec.get("module-id")

    def __repr__(self):
        return "<Question %s '%s'>" % (self.id, self.title)

    def render_prompt(self, answers):
        return Module.render_content(
            {
                "template": self.prompt,
                "format": "markdown",
            },
            answers.answers
        )

    def impute_answer(self, answers):
        # Check if any of the impute conditions are met based on
        # the questions that have been answered so far and return
        # the imputed value.
        from jinja2 import meta
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment()
        for condition, value in self.impute:
            condition_func = env.compile_expression(condition)
            if condition_func(answers.answers):
                # The condition is met. Return the imputed value.
                return value
        return None

    def validate(self, value):
        validate_func = getattr(self, "validate_" + self.type.replace("-", "_"))
        return validate_func(value)

    def validate_text(self, value):
        if value == "":
            raise ValueError("empty")
        return value

    def validate_password(self, value):
        if value == "":
            raise ValueError("empty")
        return value

    def validate_email(self, value):
        import email_validator
        email_validator.validate_email(value)
        return value

    def validate_longtext(self, value):
        if value == "":
            raise ValueError("empty")
        return value

    def validate_choice(self, value):
        if value not in [choice['key'] for choice in self.choices]:
            raise ValueError("invalid choice")
        return value

    def validate_yesno(self, value):
        if value not in ("yes", "no"):
            raise ValueError("invalid choice")
        return value

    def validate_multiple_choice(self, value):
        # Comes in from the view function as an array.
        for item in value:
            if item not in [choice['key'] for choice in self.choices]:
                raise ValueError("invalid choice: " + item)
        if len(value) < self.choice_selection_min:
            raise ValueError("not enough choices")
        if self.choice_selection_max and len(value) > self.choice_selection_max:
            raise ValueError("too many choices")
        return value

    def validate_module(self, value):
        # handled by view function
        return value

    def get_choice(self, key):
        for choice in self.choices:
            if choice["key"] == key:
                return choice
        raise KeyError(repr(key) + " is not a choice")

class ModuleAnswers:
    def __init__(self, module, answers):
        self.module = module
        self.answers = answers

    def add_imputed_answers(self):
        self.module.add_imputed_answers(self)

    def prerender(self):
        ret = { }
        for qid, value in self.answers.items():
            if qid not in self.module.questions_by_id: continue
            q = self.module.questions_by_id[qid]
            if q.type == "module":
                ret[q.id] = value.prerender()
            else:
                ret[q.id] = RenderedAnswer(q, value)
        return ret


class RenderedAnswer:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __str__(self):
        # How the template renders a question variable.
        if self.question.type == "yesno":
            return "Yes" if self.answer else "No"
        if self.question.type == "choice":
            return self.question.get_choice(self.answer)["text"]
        if self.question.type == "multiple-choice":
            return ", ".join(self.question.get_choice(c)["text"] for c in self.answer)
        return str(self.answer)

    def __bool__(self):
        # How the template converts a question variable to
        # a boolean within an expression (i.e. within an if).
        if self.question.type == "yesno":
            return self.answer == "yes"
        return bool(self.answer)

    @property # if not @property, it renders as "bound method" by jinja template
    def key(self):
        if self.question.type in ("yesno", "choice", "multiple-choice"):
            return self.answer
        raise Exception(".key is not a sensible operation for the %s question type." % self.question.type)
