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

        # Load the output template.
        self.output = {
            "format": spec["output"].get("format", "text"),
            "template": spec["output"]["template"]
        }

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

        from jinja2 import Environment, meta
        env = Environment()
        ast = env.parse(self.output['template'])
        needs_answer = [
            self.questions_by_id[qid]
            for qid in meta.find_undeclared_variables(ast)
            if qid in self.questions_by_id
            ]

        # Process the questions.

        can_answer = []
        already_processed = set()

        def is_answered(q):
            # Is q answered yet? Yes if the user has provided
            # an answer, or if one of its skip conditions is
            # met.
            return q.id in questions_answered \
              or q.should_skip(questions_answered)

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

    def render_output(self, answers):
        # Now that all questions have been answered, generate this
        # module's output.

        # Some questions may currently be in a skip state even though
        # the user may have previously entered an answer for it. Clear
        # out those questions. Go in forward order in case there are
        # dependencies between skip states.
        answers = dict(answers) # clone
        for q in self.questions:
            if q.id in answers and q.should_skip(answers):
                del answers[q.id]

        # Render.
        from jinja2 import Template
        template = Template(self.output["template"])
        output = template.render(answers)
        if self.output["format"] == "markdown":
            import CommonMark
            output = CommonMark.commonmark(output)
        return output

class Question(object):
    def __init__(self, spec):
        # Load from a YAML specification.
        self.id = spec["id"]
        self.title = spec["title"]
        self.prompt = spec["prompt"]
        self.type = spec["type"]
        self.skip_if = [spec["skip_if"]] if spec.get("skip_if") else []
        self.choices = spec.get("choices", [])

    def __repr__(self):
        return "<Question %s '%s'>" % (self.id, self.title)

    def render_prompt(self, answers):
        from jinja2 import Template
        import CommonMark
        output = Template(self.prompt).render(answers)
        output = CommonMark.commonmark(output)
        return output

    def should_skip(self, answers):
        # Check if any of the skip_if conditions are met based on
        # the questions that have been answered so far.
        from jinja2 import Environment, meta
        env = Environment()
        for condition in self.skip_if:
            condition_func = env.compile_expression(condition)
            if condition_func(answers):
                # The condition is met.
                return True
        return None

