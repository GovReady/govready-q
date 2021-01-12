from django.conf import settings
from jinja2.sandbox import SandboxedEnvironment

def get_jinja2_template_vars(template):
    from jinja2 import meta, TemplateSyntaxError
    env = SandboxedEnvironment()
    try:
        expr = env.parse(template)
    except TemplateSyntaxError as e:
        raise Exception("expression {} is invalid: {}".format(template, e))
    return set(meta.find_undeclared_variables(expr))


class Jinja2Environment(SandboxedEnvironment):
    # A Jinja2 Environment for template and expression execution.

    intercepted_binops = frozenset(['+'])

    def call_binop(self, context, operator, left, right):
        # If the operands are RenderedAnswer instances, then unwrap them
        # to the raw Python value before executing the operator.
        def unwrap(operand):
            if isinstance(operand, RenderedAnswer):
                operand = operand.answer
            return operand
        left = unwrap(left)
        right = unwrap(right)

        # Example from Jinja2 docs about overriding an operator.
        #if operator == '+':
        #    return self.undefined('the power operator is unavailable')

        # Call default operator logic.
        return SandboxedEnvironment.call_binop(self, context, operator, left, right)

def walk_module_questions(module, callback):
    # Walks the questions in depth-first order following the dependency
    # tree connecting questions. If a question is a dependency of multiple
    # questions, it is walked only once.
    #
    # callback is called for each question in the module with these arguments:
    #
    # 1) A ModuleQuestion, after the callback has been called for all
    #    ModuleQuestions that the question depends on.
    # 2) A dictionary that has been merged from the return value of all
    #    of the callback calls on its dependencies.
    # 3) A set of ModuleQuestion instances that this question depends on,
    #    so that the callback doesn't have to compute it (again) itself.

    # Remember each question that is processed so we only process each
    # question at most once. Cache the state that it gives.
    processed_questions = { }

    # Pre-load all of the dependencies between questions in this module
    # and get the questions that are not depended on by any question,
    # which is where the dependency chains start.
    dependencies, root_questions = get_all_question_dependencies(module)

    # Local function that processes a single question.
    def walk_question(q, stack):
        # If we've seen this question already as a dependency of another
        # question, then return its state dict from last time.
        if q.key in processed_questions:
            return processed_questions[q.key]
        
        # Prevent infinite recursion.
        if q.key in stack:
            raise ValueError("Cyclical dependency in questions: " + "->".join(stack + [q.key]))

        # Execute recursively on the questions it depends on,
        # in module definition order rather than in a random
        # order.
        state = { }
        deps = list(dependencies[q])
        deps.sort(key = lambda q : q.definition_order)
        for qq in deps:
            state.update(walk_question(qq, stack+[q.key]))

        # Run the callback and get its state.
        state = callback(q, state, dependencies[q])

        # Remember the state in case we encounter it later.
        processed_questions[q.key] = dict(state) # clone

        # Return the state to the caller.
        return state

    # Walk the dependency root questions in document order.
    root_questions = list(root_questions)
    root_questions.sort(key = lambda q : q.definition_order)
    for q in root_questions:
        walk_question(q, [])


def evaluate_module_state(current_answers, parent_context=None):
    # Compute the next question to ask the user, given the user's
    # answers to questions so far, and all imputed answers up to
    # that point.
    #
    # To figure this out, we walk the dependency tree of questions
    # until we arrive at questions that have no unanswered dependencies.
    # Such questions can be put forth to the user.

    # Build a list of ModuleQuestion that the are not unanswerable
    # because they are imputed or unavailable to the user. These
    # questions may have no answer or can be updatd with a new answer.
    answerable = set()

    # Build a list of ModuleQuestions that the user may answer now
    # excluding questions that the have already been answered.
    can_answer = set()

    # Build a list of ModuleQuestions that still need an answer,
    # including can_answer and unanswered ModuleQuestions that
    # have dependencies that are unanswered and need to be answered
    # first before the questions in this list can be answered.
    unanswered = set()

    # Build a new array of answer values.
    from collections import OrderedDict
    answertuples = OrderedDict()

    # Build a list of questions whose answers were imputed.
    was_imputed = set()

    # Create some reusable context for evaluating impute conditions --- really only
    # so that we can pass down project and organization values. Everything else is
    # cleared from the context's cache for each question because each question sees
    # a different set of dependencies.
    impute_context_parent = TemplateContext(
        ModuleAnswers(current_answers.module, current_answers.task, {}), lambda _0, _1, _2, _3, value : str(value), # escapefunc
        parent_context=parent_context)

    # Visitor function.
    def walker(q, state, deps):
        # If any of the dependencies don't have answers yet, then this question
        # cannot be processed yet.
        for qq in deps:
            if qq.key not in state:
                unanswered.add(q)
                answertuples[q.key] = (q, False, None, None)
                return { }

        # Can this question's answer be imputed from answers that
        # it depends on? If the user answered this question (during
        # a state in which it wasn't imputed, but now it is), the
        # user's answer is overridden with the imputed value for
        # consistency with the Module's logic.

        # Before running impute conditions below, we need a TemplateContext
        # which provides the functionality of resolving variables mentioned
        # in the impute condition. The TemplateContext that we use here is 
        # different from the one we normally use to render output documents
        # because an impute condition in a question should not be able to see
        # the answers to questions that come later in the module. The purpose
        # of evaluate_module_state is, in part, to get the answers to questions,
        # included imputed answers, and so the answers to later questions are not
        # yet know. Therefore, we construct a TemplateContext that only includes
        # the answers to questions that we've computed so far.

        impute_context = TemplateContext(
            ModuleAnswers(current_answers.module, current_answers.task, state),
            impute_context_parent.escapefunc, parent_context=impute_context_parent, root=True)

        v = run_impute_conditions(q.spec.get("impute", []), impute_context)
        if v:
            # An impute condition matched. Unwrap to get the value.
            answerobj = None
            v = v[0]
            was_imputed.add(q.key)

        elif q.key in current_answers.as_dict():
            # The user has provided an answer to this question. Question can be updated.
            answerobj = current_answers.get(q.key)
            v = current_answers.as_dict()[q.key]
            answerable.add(q)

        elif current_answers.module.spec.get("type") == "project" and q.key == "_introduction":
            # Projects have an introduction but it isn't displayed as a question.
            # It's not explicitly answered, but treat it as answered so that questions
            # that implicitly depend on it can be evaluated.
            # TODO: Is this still necessary?
            answerobj = None
            v = None

        else:
            # This question does not have an answer yet. We don't set
            # anything in the state that we return, which flags that
            # the question is not answered.
            #
            # But we can remember that this question *can* be answered
            # by the user, and that it's not answered yet.
            answerable.add(q)
            can_answer.add(q)
            unanswered.add(q)
            answertuples[q.key] = (q, False, None, None)
            return state

        # Update the state that's passed to questions that depend on this
        # and also the global state of all answered questions.
        state[q.key] = (q, True, answerobj, v)
        answertuples[q.key] = (q, True, answerobj, v)
        return state

    # Walk the dependency tree.
    walk_module_questions(current_answers.module, walker)

    # There may be multiple routes through the tree of questions,
    # so we'll prefer the question that is defined first in the spec.
    can_answer = sorted(can_answer, key = lambda q : q.definition_order)

    # The list of unanswered questions should be in the same order as
    # can_answer so that as the user goes through the questions they
    # are following the same order as the list of upcoming questions.
    # Ideally we'd form both can_answer and unanswered in the same way
    # in the right order without needing to sort later, but until then
    # we'll just sort both.
    unanswered = sorted(unanswered, key = lambda q : q.definition_order)

    # Create a new ModuleAnswers object that holds the user answers,
    # imputed answers (which override user answers), and next-question
    # information.
    ret = ModuleAnswers(current_answers.module, current_answers.task, answertuples)
    ret.was_imputed = was_imputed
    ret.unanswered = unanswered
    ret.can_answer = can_answer
    ret.answerable = answerable
    return ret


def get_question_context(answers, question):
    # What is the context of questions around the given question so show
    # the user their progress through the questions?

    # Create an object to lazy-render values, since we only use it on
    # the module-finished page and not to display context on question
    # pages.
    from guidedmodules.module_logic import TemplateContext, RenderedAnswer, HtmlAnswerRenderer
    class LazyRenderedAnswer:
        def __init__(self, q, is_answered, answer_obj, answer_value):
            self.q = q
            self.is_answered = is_answered
            self.answer_obj = answer_obj
            self.answer_value = answer_value
        def __call__(self):
            if not self.is_answered:
                return "<i>not answered</i>"
            if self.q.spec["type"] == "interstitial":
                return "<i>seen</i>"
            if self.answer_value is None:
                return "<i>skipped</i>"
            if not hasattr(LazyRenderedAnswer, 'tc'):
                LazyRenderedAnswer.tc = TemplateContext(answers, HtmlAnswerRenderer(show_metadata=False))
            return RenderedAnswer(answers.task, self.q, self.is_answered, self.answer_obj, self.answer_value, LazyRenderedAnswer.tc).__html__()

    answers.as_dict() # force lazy-load
    context = []
    for q, is_answered, answer_obj, answer_value in answers.answertuples.values():
        # Sometimes we want to skip imputed questions, but for the sake
        # of the authoring tool we need to keep imputed questions so
        # the user can navigate to them.
        context.append({
            "key": q.key,
            "title": q.spec['title'],
            "link": answers.task.get_absolute_url_to_question(q),

            # Any question that has been answered or can be answered next can be linked to,
            "can_link": (answer_obj or q in answers.can_answer),

            "imputed": is_answered and answer_obj is None,
            "skipped": (answer_obj is not None and answer_value is None) and (q.spec["type"] != "interstitial"),
            "answered": answer_obj is not None,
            "reviewed": answer_obj.reviewed if answer_obj is not None else None,
            "is_this_question": (question is not None) and (q.key == question.key),
            "value": LazyRenderedAnswer(q, is_answered, answer_obj, answer_value),
            "definition_order": q.definition_order
        })

    # Sort list of questions by definition_order
    from operator import itemgetter
    context_sorted = sorted(context, key=itemgetter('definition_order'))

    return context_sorted


def render_content(content, answers, output_format, source,
                   additional_context={}, demote_headings=True,
                   show_answer_metadata=False, use_data_urls=False,
                   is_computing_title=False):

    # Renders content (which is a dict with keys "format" and "template")
    # into the requested output format, using the ModuleAnswers in answers
    # to provide the template context.

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
        if output_format == "html" or output_format == "PARSE_ONLY":
            # Convert the template first to HTML using CommonMark.

            if not isinstance(template_body, str): raise ValueError("Template %s has incorrect type: %s" % (source, type(template_body)))
            
            # We don't want CommonMark to mess up template tags, however. If
            # there are symbols which have meaning both to Jinaj2 and CommonMark,
            # then they may get ruined by CommonMark because they may be escaped.
            # For instance:
            #
            #    {% hello "*my friend*" %}
            #
            # would become
            #
            #    {% hello "<em>my friend</em>" %}
            #
            # and
            #
            #    [my link]({{variable_holding_url}})
            #
            # would become a link whose target is
            #
            #    %7B%7Bvariable_holding_url%7D%7D
            #
            # And that's not good!
            #
            # Do a simple lexical pass over the template and replace template
            # tags with special codes that CommonMark will ignore. Then we'll
            # put back the strings after the CommonMark has been rendered into
            # HTML, so that the template tags end up in their appropriate place.
            #
            # Since CommonMark will clean up Unicode in URLs, e.g. in link and
            # image URLs, by %-encoding non-URL-safe characters, we have to
            # also override CommonMark's URL escaping function at
            # https://github.com/rtfd/CommonMark-py/blob/master/CommonMark/common.py#L71
            # to not %-encode our special codes. Unfortunately urllib.parse.quote's
            # "safe" argument does not handle non-ASCII characters.
            from commonmark import inlines
            def urlencode_special(uri):
                import urllib.parse
                return "".join(
                    urllib.parse.quote(c, safe="/@:+?=&()%#*,") # this is what CommonMark does
                    if c not in "\uE000\uE001" else c # but keep our special codes
                    for c in uri)
            inlines.normalize_uri = urlencode_special

            substitutions = []
            import re
            def replace(m):
                # Record the substitution.
                index = len(substitutions)
                substitutions.append(m.group(0))
                return "\uE000%d\uE001" % index # use Unicode private use area code points
            template_body = re.sub(r"{%[\w\W]*?%}|{{.*?}}", replace, template_body)

            # Use our CommonMark Tables parser & renderer.
            from commonmark_extensions.tables import \
                ParserWithTables as CommonMarkParser, \
                RendererWithTables as CommonMarkHtmlRenderer

            # Subclass the renderer to control the output a bit.
            class q_renderer(CommonMarkHtmlRenderer):
                def __init__(self):
                    # Our module templates are currently trusted, so we can keep
                    # safe mode off, and we're making use of that. Safe mode is
                    # off by default, but I'm making it explicit. If we ever
                    # have untrusted template content, we will need to turn
                    # safe mode on.
                    super().__init__(options={ "safe": False })

                def heading(self, node, entering):
                    # Generate <h#> tags with one level down from
                    # what would be normal since they should not
                    # conflict with the page <h1>.
                    if entering and demote_headings:
                        node.level += 1
                    super().heading(node, entering)

                def code_block(self, node, entering):
                    # Suppress info strings because with variable substitution
                    # untrusted content could land in the <code> class attribute
                    # without a language- prefix.
                    node.info = None
                    super().code_block(node, entering)

                def make_table_node(self, node):
                    return "<table class='table'>"

            template_format = "html"
            template_body = q_renderer().render(CommonMarkParser().parse(template_body))
            # Put the Jinja2 template tags back that we removed prior to running
            # the CommonMark renderer.
            def replace(m):
                return substitutions[int(m.group(1))]
            template_body = re.sub("\uE000(\d+)\uE001", replace, template_body)

        elif output_format in ("text", "markdown"):
            # Pass through the markdown markup unchanged.
            pass

        else:
            raise ValueError("Cannot render a markdown template to %s in %s." % (output_format, source))

    # Execute the template.

    if template_format in ("json", "yaml"):
        # The json and yaml template types are not rendered in the usual
        # way. The template itself is a Python data structure (not a string).
        # We will replace all string values in the data structure (except
        # dict keys) with what we get by calling render_content recursively
        # on the string value, assuming it is a template of plain-text type.

        import re
        from collections import OrderedDict

        import jinja2
        env = Jinja2Environment(
            autoescape=True,
            undefined=jinja2.StrictUndefined) # see below - we defined any undefined variables
        context = dict(additional_context) # clone
        if answers:
            def escapefunc(question, task, has_answer, answerobj, value):
                # Don't perform any escaping. The caller will wrap the
                # result in jinja2.Markup().
                return str(value)
            def errorfunc(message, short_message, long_message, **format_vars):
                # Wrap in jinja2.Markup to prevent auto-escaping.
                return jinja2.Markup("<" + message.format(**format_vars) + ">")
            tc = TemplateContext(answers, escapefunc,
                root=True,
                errorfunc=errorfunc,
                source=source,
                show_answer_metadata=show_answer_metadata,
                is_computing_title=is_computing_title)
            context.update(tc)

        def walk(value, path, additional_context_2 = {}):
            # Render string values through the templating logic.
            if isinstance(value, str):
                return render_content(
                    {
                        "format": "text",
                        "template": value
                    },
                    answers,
                    "text",
                    source + " " + "->".join(path),
                    { **additional_context, **additional_context_2 }
                )

            # Process objects with a special "%___" key specially.
            # If it has a %for key with a string value, then interpret the string value as
            # an expression in Jinja2 which we assume evaluates to a sequence-like object
            # and loop over the items in the sequence. For each item, the "%body" key
            # of this object is rendered with the context amended with variable name
            # assigned the sequence item.
            elif isinstance(value, dict) and isinstance(value.get("%for"), str):
                # The value of the "%for" key is "variable in expression". Parse that
                # first.
                m = re.match(r"^(\w+) in (.*)", value.get("%for"), re.I)
                if not m:
                    raise ValueError("%for directive needs 'variable in expression' value")
                varname = m.group(1)
                expr = m.group(2)

                condition_func = compile_jinja2_expression(expr)
                if output_format == "PARSE_ONLY":
                    return value

                # Evaluate the expression.
                context.update(additional_context_2)
                seq = condition_func(context)

                # Render the %body key for each item in sequence.
                return [
                    walk(
                        value.get("%loop"),
                        path+[str(i)],
                        { **additional_context_2, **{ varname: item } })
                    for i, item in enumerate(seq)
                ]

            elif isinstance(value, dict) and isinstance(value.get("%if"), str):
                # The value of the "%if" key is an expression.
                condition_func = compile_jinja2_expression(value["%if"])
                if output_format == "PARSE_ONLY":
                    return value

                # Evaluate the expression.
                context.update(additional_context_2)
                test = condition_func(context)

                # If the expression is true, then we render the "%then" key.
                if test:
                    return walk(
                            value.get("%then"),
                            path+["%then"],
                            additional_context_2)
                else:
                    return None

            # All other JSON data passes through unchanged.
            elif isinstance(value, list):
                # Recursively enter each value in the list and re-assemble a new list with
                # the return value of this function on each item in the list.
                return [
                    walk(i, path+[str(i)], additional_context_2)
                    for i in value]
            elif isinstance(value, dict):
                # Recursively enter each value in each key-value pair in the JSON object.
                # Return a new JSON object with the same keys but with the return value
                # of this function applied to the value.
                return OrderedDict([
                    ( k,
                      walk(v, path+[k], additional_context_2)
                    )
                    for k, v in value.items()
                    ])
            else:
                # Leave unchanged.
                return value

        # Render the template. Recursively walk the JSON data structure and apply the walk()
        # function to each value in it.
        value = walk(template_body, [])

        # If we're just testing parsing the template, return
        # any output now. Since the inner templates may have
        # returned a value of any type, we can't serialize back to
        # JSON --- pyyaml's safe dumper will raise an error if
        # it gets a non-safe value type.
        if output_format == "PARSE_ONLY":
            return value

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
        elif output_format == "PARSE_ONLY":
            # For tests, callers can use the "PARSE_ONLY" output format to
            # stop after the template is prepared.
            return output
        else:
            raise ValueError("Cannot render %s to %s in %s." % (template_format, output_format, source))

    elif template_format in ("text", "markdown", "html", "xml"):
        # The plain-text and HTML template types are rendered using Jinja2.
        #
        # The only difference is in how escaping of substituted variables works.
        # For plain-text, there is no escaping. For HTML, we render 'longtext'
        # anwers as if the user was typing Markdown. That makes sure that
        # paragraphs aren't collapsed in HTML, and gives us other benefits.
        # For other values we perform standard HTML escaping.
        import jinja2

        if template_format in ("text", "markdown", "xml"):
            def escapefunc(question, task, has_answer, answerobj, value):
                # Don't perform any escaping. The caller will wrap the
                # result in jinja2.Markup().
                return str(value)
            def errorfunc(message, short_message, long_message, **format_vars):
                # Wrap in jinja2.Markup to prevent auto-escaping.
                return jinja2.Markup("<" + message.format(**format_vars) + ">")

        elif template_format == "html":
            escapefunc = HtmlAnswerRenderer(show_metadata=show_answer_metadata, use_data_urls=use_data_urls)
            def errorfunc(message, short_message, long_message, **format_vars):
                if output_format == "html" and show_answer_metadata:
                    # In HTML outputs with popovers for answer metadata, use a popover
                    # TODO: Display detailed error info in task-finished.html more explicitly
                    # renders popovers in templates.
                    return jinja2.Markup("""
                    <span class="text-danger"
                     data-toggle="popover" data-content="{}">
                        &lt;{}&gt;
                    </span>
                    """.format(jinja2.escape(long_message.format(**format_vars)),
                               jinja2.escape(short_message.format(**format_vars))))
                else:
                    # Simple error message for HTML output when popovers are not
                    # being used. Auto-escaping will take care of escaping.
                    return "<{}>".format(message.format(**format_vars))

        # Execute the template.

        # Evaluate the template. Ensure autoescaping is turned on. Even though
        # we handle it ourselves, we do so using the __html__ method on
        # RenderedAnswer, which relies on autoescaping logic. This also lets
        # the template writer disable autoescaping with "|safe".
        env = Jinja2Environment(
            autoescape=True,
            undefined=jinja2.StrictUndefined) # see below - we defined any undefined variables
        try:
            template = env.from_string(template_body)
        except jinja2.TemplateSyntaxError as e:
            raise ValueError("There was an error loading the Jinja2 template %s: %s, line %d" % (source, str(e), e.lineno))

        # For tests, callers can use the "PARSE_ONLY" output format to
        # stop after the template is compiled.
        if output_format == "PARSE_ONLY":
            return template

        # Create an intial context dict with the additional_context provided
        # by the caller, add additional context variables and functions, and
        # add rendered answers into it.
        context = dict(additional_context) # clone
        if answers and answers.task:
            context['static_asset_path_for'] = answers.task.get_static_asset_url

        # Render.
        try:
            # context.update will immediately load all top-level values, which
            # unfortuntately might throw an error if something goes wrong
            if answers:
                tc = TemplateContext(answers, escapefunc,
                    root=True,
                    errorfunc=errorfunc,
                    source=source,
                    show_answer_metadata=show_answer_metadata,
                    is_computing_title=is_computing_title)
                context.update(tc)

            # Define undefined variables. Jinja2 will normally raise an exception
            # when an undefined variable is accessed. It can also be set to not
            # raise an exception and treat the variables as nulls. As a middle
            # ground, we'll render these variables as error messages. This isn't
            # great because an undefined variable indicates an incorrectly authored
            # template, and rendering the variable might mean no one will notice
            # the template is incorrect. But it's probably better UX than having
            # a big error message for the output as a whole or silently ignoring it.
            for varname in get_jinja2_template_vars(template_body):
                context.setdefault(varname, UndefinedReference(varname, errorfunc, [source]))
            # Now really render.
            output = template.render(context)
        except Exception as e:
            raise ValueError("There was an error executing the template %s: %s" % (source, str(e)))

        # Convert the output to the desired output format.
        if template_format == "text":
            if output_format == "text":
                # text => text (nothing to do)
                return output
            # TODO: text => markdown
            elif output_format == "html":
                # convert text to HTML by ecaping and wrapping in a <pre> tag
                import html
                return "<pre>" + html.escape(output) + "</pre>"
        elif template_format == "markdown":
            if output_format == "text":
                # TODO: markdown => text, for now just return the Markdown markup
                return output
            elif output_format == "markdown":
                # markdown => markdown -- nothing to do
                return output
        elif template_format == "xml":
            if output_format == "text":
                # TODO: markdown => text, for now just return the Markdown markup
                return output
            elif output_format == "markdown":
                # markdown => markdown -- nothing to do
                return output
            # markdown => html never occurs because we convert the Markdown to
            # HTML earlier and then we see it as html => html.
        elif template_format == "html":
            if output_format == "html":
                # html => html
                #
                # There is no data transformation, but we must check that no
                # unsafe content was inserted by variable substitution ---
                # in particular, unsafe URLs like javascript: and data: URLs.
                # When the content comes from a Markdown template, unsafe content
                # can only end up in <a> href's and <img> src's. If the template
                # has unsafe content like raw HTML, then it is up to the template
                # writer to ensure that variable substitution does not create
                # a vulnerability.
                #
                # We also rewrite non-absolute URLs in <a> href's and <img> src
                # to allow for linking to module-defined static content.
                #
                # This also fixes the nested <p>'s within <p>'s when a longtext
                # field is rendered.

                def rewrite_url(url, allow_dataurl=False):
                    # Rewrite for static assets.
                    if answers and answers.task:
                        url = answers.task.get_static_asset_url(url, use_data_urls=use_data_urls)

                    # Check final URL.
                    import urllib.parse
                    u = urllib.parse.urlparse(url)
                    
                    # Allow data URLs in some cases.
                    if use_data_urls and allow_dataurl and u.scheme == "data":
                        return url

                    if u.scheme not in ("", "http", "https", "mailto"):
                        return "javascript:alert('Invalid link.');"
                    return url

                import html5lib, xml.etree
                dom = html5lib.HTMLParser().parseFragment(output)
                for node in dom.iter():
                    if node.get("href"):
                        node.set("href", rewrite_url(node.get("href")))
                    if node.get("src"):
                        node.set("src", rewrite_url(node.get("src"), allow_dataurl=(node.tag == "{http://www.w3.org/1999/xhtml}img")))
                output = html5lib.serialize(dom, quote_attr_values="always", omit_optional_tags=False, alphabetical_attributes=True)

                # But the p's within p's fix gives us a lot of empty p's.
                output = output.replace("<p></p>", "")

                return output

        raise ValueError("Cannot render %s to %s." % (template_format, output_format))

    else:
        raise ValueError("Invalid template format encountered: %s." % template_format)


class HtmlAnswerRenderer:
    def __init__(self, show_metadata, use_data_urls=False):
        self.show_metadata = show_metadata
        self.use_data_urls = use_data_urls
    def __call__(self, question, task, has_answer, answerobj, value):
        import html

        if question is not None and question.spec["type"] == "longtext":
            # longtext fields are rendered into the output
            # using CommonMark. Escape initial <'s so they
            # are not treated as the start of HTML tags,
            # which are not permitted in safe mode, but
            # <'s appear tag-like in certain cases like
            # when we say <not answerd>.
            if value.startswith("<"): value = "\\" + value

            from commonmark_extensions.tables import \
                ParserWithTables as CommonMarkParser, \
                RendererWithTables as CommonMarkHtmlRenderer
            parsed = CommonMarkParser().parse(value)
            value = CommonMarkHtmlRenderer({ "safe": True }).render(parsed)

            wrappertag = "div"

        elif question is not None and question.spec["type"] == "file" \
            and hasattr(value, "file_data"):
            # Files turn into link tags, possibly containing a thumbnail
            # or the uploaded image itself.

            img_url = None
            if self.use_data_urls and value.file_data.get("thumbnail_dataurl"):
                img_url = value.file_data["thumbnail_dataurl"]
            elif self.use_data_urls and value.file_data.get("content_dataurl"):
                img_url = value.file_data["content_dataurl"]
            elif self.use_data_urls:
                img_url = "data:"
            elif value.file_data.get("thumbnail_url"):
                img_url = value.file_data["thumbnail_url"]
            elif question.spec.get("file-type") == "image":
                img_url = value.file_data['url']

            from jinja2.filters import do_filesizeformat
            label = "Download attachment ({format}; {size}; {date})".format(
                format=value.file_data["type_display"],
                size=do_filesizeformat(value.file_data['size']),
                date=answerobj.created.strftime("%x") if answerobj else "",
            )

            if not img_url:
                # no thumbnail
                value = """<p><a href="%s">%s</a></p>""" % (
                    html.escape(value.file_data['url']),
                    label,
                )
            else:
                # has a thumbnail
                # used to have max-height: 100vh; here but wkhtmltopdf understands it as 0px
                value = """
                <p>
                  <a href="%s" class="user-media">
                    <img src="%s" class="img-responsive" style=" border: 1px solid #333; margin-bottom: .25em;">
                    <div style='font-size: 90%%;'>%s</a></div>
                  </a>
                </p>""" % (
                    html.escape(value.file_data['url']),
                    html.escape(img_url or ""),
                    label,
                )

            wrappertag = "div"

        elif question is not None and question.spec["type"] == "datagrid":
            # Assuming that RenderedAnswer gives us string version of the stored datagrid object
            # that is an Array of Dictionaries
            import ast
            try:
                # Get datagrid data if datagrid question has been answered with information
                datagrid_rows = ast.literal_eval(value)
            except:
                if value == "<nothing chosen>":
                    # Datagrid question has been visited and instantiated but no answer given
                    # No data was entered into data grid
                    datagrid_rows = []
                else:
                    # Datagrid question has not been visited and not yet instantiated
                    # `value` is set to "<Software Inventory (datagrid)>"
                    datagrid_rows = []

            if "render" in question.spec and question.spec["render"] == "vertical":
                # Build a vertical table to display datagrid information
                value = ""
                for item in datagrid_rows:
                    # Start a new table
                    value += "<table class=\"table\">\n"
                    # Create a row for each field
                    for field in question.spec["fields"]:
                        value += "<tr><td class=\"td_datagrid_vertical\">{}</td><td>{}</td></tr>".format(html.escape(str(field["text"])), html.escape(str(item[field["key"]])))
                    value += "\n</table>"
            else:
                # Build a standard table to display datagrid information
                value = "<table class=\"table\">\n"
                value += "<thead>\n<tr>"
                # To get the correct order, get keys from question specification fields
                for field in question.spec["fields"]:
                    value += "<th>{}</th>".format(html.escape(str(field["text"])))
                value += "</tr>\n"
                for item in datagrid_rows:
                    value += "<tr>"
                    # To get the correct order, get keys from question specification fields
                    for field in question.spec["fields"]:
                        value += "<td>{}</td>".format(html.escape(str(item[field["key"]])))
                    value += "</tr>\n</thead>"
                # value = html.escape(str(datagrid_rows))
                value += "\n</table>"
            wrappertag = "div"

        else:
            # Regular text fields just get escaped.
            value = html.escape(str(value))
            wrappertag = "span"

        if (not self.show_metadata) or (question is None):
            return value

        # Wrap the output in a tag that holds metadata.

        # If the question is imputed...
        if has_answer and not answerobj:
            return """<{tag} class='question-answer'
              data-module='{module}'
              data-question='{question}'
              data-answer-type='{answer_type}'
              {edit_link}
              >{value}</{tag}>""".format(
                tag=wrappertag,
                module=html.escape(question.module.spec['title']),
                question=html.escape(question.spec["title"]),
                answer_type="skipped" if not has_answer else "imputed",
                edit_link="",
                value=value,
            )

        # If the question is unanswered...
        if not answerobj:
            return """<{tag} class='question-answer'
              data-module='{module}'
              data-question='{question}'
              data-answer-type='{answer_type}'
              {edit_link}
              >{value}</{tag}>""".format(
                tag=wrappertag,
                module=html.escape(question.module.spec['title']),
                question=html.escape(question.spec["title"]),
                answer_type="skipped" if not has_answer else "imputed",
                edit_link=("data-edit-link='" + task.get_absolute_url_to_question(question) + "'") if task else "",
                value=value,
            )

        # If the question is answered (by a user).
        return """<{tag} class='question-answer'
          data-module='{module}'
          data-question='{question}'
          data-answer-type='user-answer'
          data-edit-link='{edit_link}'
          data-answered-by='{answered_by}'
          data-answered-on='{answered_on}'
          data-reviewed='{reviewed}'
          >{value}</{tag}>""".format(
            tag=wrappertag,
            module=html.escape(question.module.spec['title']),
            question=html.escape(question.spec["title"]),
            edit_link=answerobj.taskanswer.get_absolute_url(),
            answered_by=html.escape(str(answerobj.answered_by)),
            answered_on=html.escape(answerobj.created.strftime("%c")),
            reviewed=str(answerobj.reviewed),
            value=value,
        )


def clear_module_question_cache():
    if hasattr(get_all_question_dependencies, 'cache'):
        del get_all_question_dependencies.cache


def get_all_question_dependencies(module):
    # Initialize cache, query cache.
    if not hasattr(get_all_question_dependencies, 'cache'):
        get_all_question_dependencies.cache = { }
    if module.id in get_all_question_dependencies.cache:
        return get_all_question_dependencies.cache[module.id]

    # Pre-load all of the questions by their key so that the dependency
    # evaluation is fast.
    all_questions = { }
    for q in module.questions.all():
        all_questions[q.key] = q

    # Compute all of the dependencies of all of the questions.
    dependencies = {
        q: get_question_dependencies(q, get_from_question_id=all_questions)
        for q in all_questions.values()
    }

    # Find the questions that are at the root of the dependency tree.
    is_dependency_of_something = set()
    for deps in dependencies.values():
        is_dependency_of_something |= deps
    root_questions = { q for q in dependencies if q not in is_dependency_of_something }

    ret = (dependencies, root_questions)

    # Save to in-memory (in-process) cache. Never in debugging.
    if not settings.DEBUG:
        get_all_question_dependencies.cache[module.id] = ret

    return ret

def get_question_dependencies(question, get_from_question_id=None):
    return set(edge[1] for edge in get_question_dependencies_with_type(question, get_from_question_id))

def get_question_dependencies_with_type(question, get_from_question_id=None):
    if get_from_question_id is None:
        # dict-like interface
        class GetFromQuestionId:
            def __getitem__(self, qid):
                return question.module.questions.filter(key=qid).get()
            def __contains__(self, qid):
                return question.module.questions.filter(key=qid).exists()
        get_from_question_id = GetFromQuestionId()

    # Returns a set of ModuleQuestion instances that this question is dependent on
    # as a list of edges that are tuples of (edge_type, question obj).
    ret = []
    
    # All questions mentioned in prompt text become dependencies.
    for qid in get_jinja2_template_vars(question.spec.get("prompt", "")):
        ret.append(("prompt", qid))

    # All questions mentioned in the impute conditions become dependencies.
    # And when impute values are expressions, then similarly for those.
    for rule in question.spec.get("impute", []):
        if "condition" in rule:
            for qid in get_jinja2_template_vars(
                    r"{% if (" + rule["condition"] + r") %}...{% endif %}"
                    ):
                ret.append(("impute-condition", qid))

        if rule.get("value-mode") == "expression":
            for qid in get_jinja2_template_vars(
                    r"{% if (" + rule["value"] + r") %}...{% endif %}"
                    ):
                ret.append(("impute-value", qid))

        if rule.get("value-mode") == "template":
            for qid in get_jinja2_template_vars(rule["value"]):
                ret.append(("impute-value", qid))

    # Other dependencies can just be listed.
    for qid in question.spec.get("ask-first", []):
        ret.append(("ask-first", qid))

    # Turn IDs into ModuleQuestion instances.
    return [ (edge_type, get_from_question_id[qid])
         for (edge_type, qid) in ret
         if qid in get_from_question_id
       ]

jinja2_expression_compile_cache = { }

def compile_jinja2_expression(expr):
    # If the expression has already been compiled and is in the cache,
    # return the compiled expression.
    if expr in jinja2_expression_compile_cache:
        return jinja2_expression_compile_cache[expr]

    # The expression is not in the cache. Compile it.
    env = Jinja2Environment()
    compiled = env.compile_expression(expr)

    # Save it to the cache.
    jinja2_expression_compile_cache[expr] = compiled

    # Return it.
    return compiled

def run_impute_conditions(conditions, context):
    # Check if any of the impute conditions are met based on
    # the questions that have been answered so far and return
    # the imputed value. Be careful about values like 0 that
    # are false-y --- must check for "is None" to know if
    # something was imputed or not.
    env = Jinja2Environment()
    for rule in conditions:
        if "condition" in rule:
            condition_func = compile_jinja2_expression(rule["condition"])
            try:
                value = condition_func(context)
            except:
                value = None
        else:
            value = True

        if value:
            # The condition is met. Compute the imputed value.
            if rule.get("value-mode", "raw") == "raw":
                # Imputed value is the raw YAML value.
                value = rule["value"]
            elif rule.get("value-mode", "raw") == "expression":
                value = compile_jinja2_expression(rule["value"])(context)
                if isinstance(value, RenderedAnswer):
                    # Unwrap.
                    value =  value.answer
                elif hasattr(value, "__html__"):
                    # some things might return something that safely wraps a string,
                    # like our SafeString instance
                    value = value.__html__()
                elif hasattr(value, "as_raw_value"):
                    # RenderedProject, RenderedOrganization
                    value = value.as_raw_value()
            elif rule.get("value-mode", "raw") == "template":
                env = Jinja2Environment(autoescape=True)
                try:
                    template = env.from_string(rule["value"])
                except jinja2.TemplateSyntaxError as e:
                    raise ValueError("There was an error loading the template %s: %s" % (rule["value"], str(e)))
                value = template.render(context)
            else:
                raise ValueError("Invalid impute condition value-mode.")

            # Since the imputed value may be None, return
            # the whole thing in a tuple to distinguish from
            # a None indicating the lack of an imputed value.
            return (value,)
    return None


def get_question_choice(question, key):
    for choice in question.spec["choices"]:
        if choice["key"] == key:
            return choice
    raise KeyError(repr(key) + " is not a choice")

class ModuleAnswers(object):
    """Represents a set of answers to a Task."""

    def __init__(self, module, task, answertuples):
        self.module = module
        self.task = task
        self.answertuples = answertuples
        self.answers_dict = None

    def __str__(self):
        return "<ModuleAnswers for %s - %s>" % (self.module, self.task)

    def as_dict(self):
        if self.answertuples is None:
            # Lazy-load by calling the task's get_answers function
            # and copying its answers dictionary.
            if self.task is None:
                self.answertuples = { q.key: (q, False, None, None) for q in sorted(self.module.questions.all(), key = lambda q : q.definition_order) }
            else:
                self.answertuples = self.task.get_answers().answertuples
        if self.answers_dict is None:
            self.answers_dict = { q.key: value for q, is_ans, ansobj, value in self.answertuples.values() if is_ans }
        return self.answers_dict

    def with_extended_info(self, parent_context=None):
        # Return a new ModuleAnswers instance that has imputed values added
        # and information about the next question(s) and unanswered questions.
        return evaluate_module_state(self, parent_context=parent_context)

    def get(self, question_key):
        return self.answertuples[question_key][2]

    def get_questions(self):
        self.as_dict() # lazy load if necessary
        return [v[0] for v in self.answertuples.values()]

    def render_answers(self, show_unanswered=True, show_imputed=True, show_imputed_nulls=True, show_metadata=False):
        # Return a generator that provides tuples of
        # (question, answerobj, answerhtml) where
        #   * question is a ModuleQuestion instance
        #   * answerobj is a TaskAnswerHistory instance (e.g. holding user and review state), or None if the answer was skipped or imputed
        #   * answerhtml is a str of rendered HTML
        tc = TemplateContext(self, HtmlAnswerRenderer(show_metadata=show_metadata))
        for q, is_answered, a, value in self.answertuples.values():
            if not is_answered and not show_unanswered: continue # skip questions that have no answers
            if not a and not show_imputed: continue # skip imputed answers
            if not a and value is None and not show_imputed_nulls: continue # skip questions whose imputed value is null
            if q.spec["type"] == "interstitial": continue # skip question types that display awkwardly
            if value is None:
                # Question is skipped.
                if a.skipped_reason:
                    value_display = "<i>{}</i>".format( a.get_skipped_reason_display() )
                else:
                    value_display = "<i>skipped</i>"
            else:
                # Use the template rendering system to produce a human-readable
                # HTML rendering of the value.
                value_display = RenderedAnswer(self.task, q, is_answered, a, value, tc)
                
                # For question types whose primary value is machine-readable,
                # show a nice display form if possible using the .text attribute,
                # if possible. It probably returns a SafeString which needs __html__()
                # to be called on it. "file" questions render nicer without .text.
                if q.spec["type"] not in ("file",):
                    try:
                        value_display = value_display.text
                    except AttributeError:
                        pass

                # Whether or not we called .text, call __html__() to get
                # a rendered form.
                if hasattr(value_display, "__html__"):
                    value_display = value_display.__html__()

            yield (q, a, value_display)

    def render_output(self, use_data_urls=False):
        # Now that all questions have been answered, generate this
        # module's output. The output is a set of documents. The
        # documents are lazy-rendered because not all of them may
        # be used by the caller.

        class LazyRenderedDocument(object):
            output_formats = ("html", "text", "markdown")

            def __init__(self, module_answers, document, index, use_data_urls):
                self.module_answers = module_answers
                self.document = document
                self.index = index
                self.rendered_content = { }
                self.use_data_urls = use_data_urls

            def __iter__(self):
                # Yield all of the keys (entry) that are in the output document
                # specification, plus all of the output formats which are
                # keys (entry) in our returned dict that lazily render the document.
                for entry, value in self.document.items():
                    if entry not in self.output_formats:
                        yield entry
                for entry in self.output_formats:
                    yield entry
            def __getitem__(self, entry):
                if entry in self.output_formats:
                    # entry is an output format -> lazy render.

                    if entry not in self.rendered_content:
                        # Cache miss.

                        # For errors, what is the name of this document?
                        if "id" in self.document:
                            doc_name = self.document["id"]
                        else:
                            doc_name = "at index " + str(self.index)
                            if "title" in self.document:
                                doc_name = repr(self.document["title"]) + " (" + doc_name + ")"
                        doc_name = "'%s' output document '%s'" % (self.module_answers.module.module_name, doc_name)

                        # Try to render it.
                        task_cache_entry = "output_r1_{}_{}_{}".format(
                            self.index,
                            entry,
                            1 if self.use_data_urls else 0,
                        )
                        def do_render():
                            try:
                                return render_content(self.document, self.module_answers, entry, doc_name, show_answer_metadata=True, use_data_urls=self.use_data_urls)
                            except Exception as e:
                                # Put errors into the output. Errors should not occur if the
                                # template is designed correctly.
                                ret = str(e)
                                if entry == "html":
                                    import html
                                    ret = "<p class=text-danger>" + html.escape(ret) + "</p>"
                                return ret
                        self.rendered_content[entry] = self.module_answers.task._get_cached_state(task_cache_entry, do_render)

                    return self.rendered_content[entry]

                elif entry in self.document:
                    # entry is a entry in the specification for the document.
                    # Return it unchanged.
                    return self.document[entry]

                raise KeyError(entry)
                
            def get(self, entry, default=None):
                if entry in self.output_formats or entry in self.document:
                    return self[entry]

        return [ LazyRenderedDocument(self, d, i, use_data_urls) for i, d in enumerate(self.module.spec.get("output", [])) ]


class UndefinedReference:
    def __init__(self, varname, errorfunc, path=[]):
        self.varname = varname
        self.errorfunc = errorfunc
        self.path = path
    def __html__(self):
        return self.errorfunc(
            "invalid reference to '{varname}' in {source}",
            "invalid reference",
            "Invalid reference to variable '{varname}' in {source}.",
            varname=self.varname,
            source=" -> ".join(self.path),
        )
    def __getitem__(self, item):
        return UndefinedReference(item, self.errorfunc, self.path+[self.varname])

from collections.abc import Mapping
class TemplateContext(Mapping):
    """A Jinja2 execution context that wraps the Pythonic answers to questions
       of a ModuleAnswers instance in RenderedAnswer instances that provide
       template and expression functionality like the '.' accessor to get to
       the answers of a sub-task."""

    def __init__(self, module_answers, escapefunc, parent_context=None, root=False, errorfunc=None, source=None, show_answer_metadata=None, is_computing_title=False):
        self.module_answers = module_answers
        self.escapefunc = escapefunc
        self.root = root
        self.errorfunc = parent_context.errorfunc if parent_context else errorfunc
        self.source = (parent_context.source if parent_context else []) + ([source] if source else [])
        self.show_answer_metadata = parent_context.show_answer_metadata if parent_context else (show_answer_metadata or False)
        self.is_computing_title = parent_context.is_computing_title if parent_context else is_computing_title
        self._cache = { }
        self.parent_context = parent_context

    def __str__(self):
        return "<TemplateContext for %s>" % (self.module_answers)

    def __getitem__(self, item):
        # Cache every context variable's value, since some items are expensive.
        if item not in self._cache:
            self._cache[item] = self.getitem(item)
        return self._cache[item]

    def _execute_lazy_module_answers(self):
        if self.module_answers is None:
            # This is a TemplateContext for an unanswered question with an unknown
            # module type. We treat this as if it were a Task that had no questions but
            # also is not finished.
            self._module_questions = { }
            return
        if callable(self.module_answers):
            self.module_answers = self.module_answers()
        self._module_questions = { q.key: q for q in self.module_answers.get_questions() }

    def getitem(self, item):
        self._execute_lazy_module_answers()
        
        # If 'item' matches a question ID, wrap the internal Pythonic/JSON-able value
        # with a RenderedAnswer instance which take care of converting raw data values
        # into how they are rendered in templates (escaping, iteration, property accessors)
        # and evaluated in expressions.
        question = self._module_questions.get(item)
        if question:
            # The question might or might not be answered. If not, its value is None.
            self.module_answers.as_dict() # trigger lazy-loading
            _, is_answered, answerobj, answervalue = self.module_answers.answertuples.get(item, (None, None, None, None))
            return RenderedAnswer(self.module_answers.task, question, is_answered, answerobj, answervalue, self)

        # The context also provides the project and organization that the Task belongs to,
        # and other task attributes, assuming the keys are not overridden by question IDs.
        if self.module_answers and self.module_answers.task:
            if item == "title" and (not self.is_computing_title or not self.root):
                return self.module_answers.task.title
            if item == "task_link":
                return self.module_answers.task.get_absolute_url()
            if item == "project":
                if self.parent_context is not None: # use parent's cache
                    return self.parent_context[item]
                return RenderedProject(self.module_answers.task.project, parent_context=self)
            if item == "organization":
                if self.parent_context is not None: # use parent's cache
                    return self.parent_context[item]
                return RenderedOrganization(self.module_answers.task, parent_context=self)
            if item == "control_catalog":
                # Retrieve control catalog(s) for project
                # Temporarily retrieve a single catalog
                # TODO: Retrieve multiple catalogs because we could have catalogs plus overlays
                #       Will need a better way to determine the catalogs on a system so we can retrieve at once
                #       Maybe get the catalogs as a property of the system
                # Retrieve a Django dictionary of dictionaries object of full control catalog

                from controls.oscal import Catalog
                # Detect single control catalog from first control
                try:
                    catalog_key = self.module_answers.task.project.system.root_element.controls.first().oscal_catalog_key
                    parameter_values = self.module_answers.task.project.get_parameter_values(catalog_key)
                    sca = Catalog.GetInstance(catalog_key=catalog_key, 
                                              parameter_values=parameter_values)
                    control_catalog = sca.flattened_controls_all_as_dict
                except:
                    control_catalog = None
                return control_catalog
            if item == "system":
                # Retrieve the system object associated with this project
                # Returned value must be a python dictionary
                return self.module_answers.task.project.system
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

        # The 'questions' key returns (question, answer) pairs.
        if item == "questions":
            if self.module_answers is None:
                return []
            self.module_answers.as_dict() # trigger lazy-loading
            ret = []
            for question, is_answered, answerobj, answervalue in self.module_answers.answertuples.values():
                ret.append((
                    question.spec,
                    RenderedAnswer(self.module_answers.task, question, is_answered, answerobj, answervalue, self)
                ))
            return ret

        # The output_documents key returns the output documents as a dict-like mapping
        # from IDs to rendered content.
        if item == "output_documents":
            return TemplateContext.LazyOutputDocuments(self)

        # The item is not something found in the context.
        error_message = "'{item}' is not a question or property of '{object}'."
        error_message_vars = { "item": item, "object": (self.module_answers.task.title if self.module_answers and self.module_answers.task else self.module_answers.module.spec["title"]) }
        if self.errorfunc:
            return UndefinedReference(item, self.errorfunc, self.source + ["(" + error_message_vars["object"] + ")"])
        raise AttributeError(error_message.format(**error_message_vars))

    def __iter__(self):
        self._execute_lazy_module_answers()

        seen_keys = set()

        # question names
        for q in self._module_questions.values():
            seen_keys.add(q.key)
            yield q.key

        # special values
        # List the name of variables that are available in the templatecontext `getitem`
        if self.module_answers and self.module_answers.task:
            # Attributes that are only available if there is a task.
            if not self.is_computing_title or not self.root:
                # 'title' isn't available if we're in the process of
                # computing it
                yield "title"
            for attribute in ("task_link", "project", "organization", "control_catalog", "system"):
                if attribute not in seen_keys:
                    yield attribute

        # Attributes that are available even when peering into unanswered module-type questions.
        for attribute in ("is_started", "is_finished", "questions", "output_documents"):
            if attribute not in seen_keys:
                yield attribute

    def __len__(self):
        return len([x for x in self])


    # Class that lazy-renders output documents on request.
    class LazyOutputDocuments:
        def __init__(self, context):
            self.context = context
        def __getattr__(self, item):
            try:
                # Find the requested output document in the module.
                for doc in self.context.module_answers.module.spec.get("output", []):
                    if doc.get("id") == item:
                        # Render it.
                        content = render_content(doc, self.context.module_answers, "html",
                            "'%s' output document '%s'" % (repr(self.context.module_answers.module), item),
                            {}, show_answer_metadata=self.context.show_answer_metadata)

                        # Mark it as safe.
                        from jinja2 import Markup
                        return Markup(content)
                else:
                    raise ValueError("%s is not the id of an output document in %s." % (item, self.context.module_answers.module))
            except Exception as e:
                return str(e)
        def __contains__(self, item):
            for doc in self.context.module_answers.module.spec.get("output", []):
                if doc.get("id") == item:
                    return True
            return False
        def __iter__(self):
            for doc in self.context.module_answers.module.spec.get("output", []):
                if doc.get("id"):
                    yield doc["id"]


class RenderedProject(TemplateContext):
    def __init__(self, project, parent_context=None):
        self.project = project
        def _lazy_load():
            if self.project.root_task:
                return self.project.root_task.get_answers()
        super().__init__(_lazy_load, parent_context.escapefunc, parent_context=parent_context)
        self.source = self.source + ["project variable"]
    def __str__(self):
        return "<TemplateContext for %s - %s>" % (self.project, self.module_answers)

    def as_raw_value(self):
        if self.is_computing_title:
            # When we're computing the title for "instance-name", prevent
            # infinite recursion.
            return self.project.root_task.module.spec['title']
        return self.project.title
    def __html__(self):
        return self.escapefunc(None, None, None, None, self.as_raw_value())

class RenderedOrganization(TemplateContext):
    def __init__(self, task, parent_context=None):
        self.task =task
        def _lazy_load():
            project = self.organization.get_organization_project()
            if project.root_task:
                return project.root_task.get_answers()
        super().__init__(_lazy_load, parent_context.escapefunc, parent_context=parent_context)
        self.source = self.source + ["organization variable"]

    @property
    def organization(self):
        if not hasattr(self, "_org"):
            self._org = self.task.project.organization
        return self._org

    def __str__(self):
        return "<TemplateContext for %s - %s>" % (self.organization, self.module_answers)

    def as_raw_value(self):
        return self.organization.name
    def __html__(self):
        return self.escapefunc(None, None, None, None, self.as_raw_value())

class RenderedAnswer:
    def __init__(self, task, question, is_answered, answerobj, answer, parent_context):
        self.task = task
        self.question = question
        self.is_answered = is_answered
        self.answerobj = answerobj
        self.answer = answer
        self.parent_context = parent_context
        self.escapefunc = parent_context.escapefunc
        self.question_type = self.question.spec["type"]
        self.cached_tc = None

    def __html__(self):
        # This method name is a Jinja2 convention. See http://jinja.pocoo.org/docs/2.10/api/#jinja2.Markup.
        # Jinja2 calls this method to get the string to put into the template when this value
        # appears in template in a {{variable}} directive.
        #
        # So this method returns how the templates render a question's answer when used as in e.g. {{q0}}.

        if self.answer is None:
            # Render a non-answer answer.
            if self.parent_context.is_computing_title:
                # When computing an instance-name title,
                # raise an exception (caught higher up) if
                # an unanswered question is rendered.
                raise ValueError("Attempt to render unanswered question {}.".format(self.question.key))
            value = "<%s>" % self.question.spec['title']

        elif self.question_type == "multiple-choice":
            # Render multiple-choice as a comma+space-separated list of the choice keys.
            value = ", ".join(self.answer)

        elif self.question_type == "datagrid":
            # Render datagrid as an array of dictionaries
            value = str(self.answer)

        elif self.question_type == "file":
            # Pass something to the escapefunc that HTML rendering can
            # recognize as a file but non-HTML rendering sees as a string.
            class FileValueWrapper:
                def __init__(self, answer):
                    self.file_data = answer
                def __str__(self):
                    return "<uploaded file: " + self.file_data['url'] + ">"
            value = FileValueWrapper(self.answer)

        elif self.question_type in ("module", "module-set"):
            ans = self.answer # ModuleAnswers or list of ModuleAnswers
            if self.question_type == "module": ans = [ans] # make it a lsit
            def get_title(task):
                if self.parent_context.is_computing_title:
                    # When we're computing the title for "instance-name", prevent
                    # infinite recursion.
                    return task.module.spec['title']
                else:
                    # Get the computed title.
                    return task.title
            value = ", ".join(get_title(a.task) for a in ans)

        else:
            # For all other question types, just call Python str().
            value = str(self.answer)

        # And in all cases, escape the result.
        return self.escapefunc(self.question, self.task, self.answer is not None, self.answerobj, value)

    @property
    def text(self):
        # How the template renders {{q0.text}} to get a nice display form of the answer.
        if self.answer is None:
            if self.parent_context.is_computing_title:
                # When computing an instance-name title,
                # raise an exception (caught higher up) if
                # an unanswered question is rendered.
                raise ValueError("Attempt to render unanswered question {}.".format(self.question.key))
            value = "<not answered>"
        elif self.question_type == "date":
            # Format the ISO date for display.
            value = str(self.answer) # fall-back
            import re, datetime
            m = re.match("(\d\d\d\d)-(\d\d)-(\d\d)$", self.answer)
            if m:
                try:
                    year, month, date = [int(x) for x in m.groups()]
                    value = datetime.date(year, month, date).strftime("%x")
                except ValueError:
                    pass
        elif self.question_type == "yesno":
            value = ("Yes" if self.answer == "yes" else "No")
        elif self.question_type == "choice":
            value = get_question_choice(self.question, self.answer)["text"]
        elif self.question_type == "multiple-choice":
            if len(self.answer) == 0:
                value = "<nothing chosen>"
            else:
                choices = [get_question_choice(self.question, c)["text"] for c in self.answer] # get choice text
                delim = "," if ("," not in "".join(choices)) else ";" # separate choices by commas unless there are commas in the choices, then use semicolons
                value = (delim+" ").join(choices)
        elif self.question_type == "datagrid":
            if len(self.answer) == 0:
                value = "<nothing chosen>"
            else:
                value = str(self.answer)

        elif self.question_type in ("integer", "real"):
            # Use a locale to generate nice human-readable numbers.
            # The locale is set on app startup using locale.setlocale in settings.py.
            import locale
            value = locale.format(
                "%d" if self.question_type == "integer" else "%g",
                self.answer,
                grouping=True)
        elif self.question_type == "file":
            value = "<uploaded file: " + self.answer['url'] + ">"
        elif self.question_type in ("module", "module-set"):
            # This field is not present for module-type questions because
            # the keys are attributes exposed by the answer.
            raise AttributeError()
        else:
            # For all other question types, just call Python str().
            value = str(self.answer)

        # Wrap the value in something that provides a __html__
        # method to override Jinja2 escaping so we can use our
        # own function.
        class SafeString:
            def __init__(self, value, ra):
                self.value = value
                self.ra = ra
            def __html__(self):
                return self.ra.escapefunc(self.ra.question, self.ra.task, self.ra.answer is not None, self.ra.answerobj, self.value)
        return SafeString(value, self)

    @property
    def edit_link(self):
        # Return a link to edit this question.
        return self.task.get_absolute_url_to_question(self.question)

    @property
    def choices_selected(self):
        # Return the dicts for each choice that is a part of the answer.
        if self.question_type == "multiple-choice":
            return [
                choice
                for choice in self.question.spec["choices"]
                if self.answer is not None and choice["key"] in self.answer
            ]
        raise AttributeError

    @property
    def choices_not_selected(self):
        # Return the dicts for each choice that is not a part of the answer.
        if self.question_type == "multiple-choice":
            return [
                choice
                for choice in self.question.spec["choices"]
                if choice["key"] not in self.answer or self.answer is None
            ]
        raise AttributeError

    @property
    def not_yet_answered(self):
        return not self.is_answered

    @property
    def imputed(self):
        # The answer was imputed if it's considered 'answered'
        # but there is no TaskAnswerHistory record in the database
        # for it, which means the user didn't provide the answer.
        return self.is_answered and (self.answerobj is None)

    @property
    def skipped(self):
        # The question has a null answer either because it was imputed null
        # or the user skipped it.
        return self.is_answered and (self.answer is None) 

    @property
    def skipped_by_user(self):
        # The question has a null answer but it wasn't imputed null.
        return self.is_answered and (self.answerobj is not None) and (self.answer is None)

    @property
    def answered(self):
        # This question has an answer, either because it was imputed or it was
        # answered by the user, but not if it was imputed null or answered null
        # because those are skipped states above.
        return self.is_answered and (self.answer is not None)

    @property
    def skipped_reason(self):
        if self.answerobj is None:
            return self.answerobj
        return self.answerobj.skipped_reason

    @property
    def unsure(self):
        # If the question was answered by a user, return its unsure flag.
        if not self.answerobj:
            return None
        return self.answerobj.unsure
    
    @property
    def date_answered(self):
        # Date question was answered.
        if not self.answerobj:
            return None
        return self.answerobj.created

    @property
    def reviewed_state(self):
        # Question reviewed value.
        if not self.answerobj:
            return None
        return self.answerobj.reviewed

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
            # Iterate by creating a RenderedAnswer for each selected choice,
            # with a made-up temporary Question instance that has the same
            # properties as the actual multiple-choice choice but whose
            # type is a single "choice".
            from .models import ModuleQuestion
            return (
                RenderedAnswer(
                    self.task,
                    ModuleQuestion(
                        module=self.question.module,
                        key=self.question.key,
                        spec={
                            "type": "choice",
                            "title": self.question.spec['title'],
                            "prompt": self.question.spec['prompt'],
                            "choices": self.question.spec["choices"],
                        }),
                    self.is_answered,
                    self.answerobj,
                    ans, self.parent_context)
                for ans in self.answer)

        elif self.question_type == "datagrid":
            # Iterate by creating a RenderedAnswer for each selected field,
            # with a made-up temporary Question instance that has the same
            # properties as the actual datagrid field but whose
            # type is a single "datagrid".
            from .models import ModuleQuestion
            return (
                RenderedAnswer(
                    self.task,
                    ModuleQuestion(
                        module=self.question.module,
                        key=self.question.key,
                        spec={
                            "type": "datagrid",
                            "title": self.question.spec['title'],
                            "prompt": self.question.spec['prompt'],
                            "fields": self.question.spec["fields"],
                        }),
                    self.is_answered,
                    self.answerobj,
                    ans, self.parent_context)
                for ans in self.answer)

        elif self.question_type == "module-set":
            # Iterate over the sub-tasks' answers. Load each's answers + imputed answers.
            return (TemplateContext(
                v.with_extended_info(parent_context=self.parent_context if not v.task or not self.task or v.task.project_id==self.task.project_id else None),
                self.escapefunc, parent_context=self.parent_context)
                for v in self.answer)

        raise TypeError("Answer of type %s is not iterable." % self.question_type)

    def __len__(self):
        if self.question_type in ("multiple-choice", "module-set"):
            if self.answer is None: return 0
            return len(self.answer)

        if self.question_type in ("datagrid"):
            if self.answer is None: return 0
            return len(self.answer)

        raise TypeError("Answer of type %s has no length." % self.question_type)

    def __getattr__(self, item):
        # For module-type questions, provide the answers of the
        # sub-task as properties of this context variable.
        if self.question_type == "module":
            # Pass through via a temporary TemplateContext.
            if self.answer is not None:
                # If the question was not skipped, then we have the ModuleAnswers for it.
                # Load its answers + evaluate impute conditions.
                if not self.cached_tc:
                    self.cached_tc = TemplateContext(
                        lambda : self.answer.with_extended_info(parent_context=self.parent_context if not self.answer.task or not self.task or self.answer.task.project_id==self.task.project_id else None),
                        self.escapefunc,
                        parent_context=self.parent_context)
                tc = self.cached_tc
            else:
                # The question was skipped -- i.e. we have no ModuleAnswers for
                # the question that this RenderedAnswer represents. But we want
                # to gracefully represent the inner item attribute as skipped too.
                # If self.question.answer_type_module is set, then we know the
                # inner Module type, so we can create a dummy instance that
                # represents an unanswered instance of the Module.
                if self.question.answer_type_module is not None:
                    ans = ModuleAnswers(self.question.answer_type_module, None, None)
                else:
                    ans = None
                tc = TemplateContext(ans, self.escapefunc, parent_context=self.parent_context)
            return tc[item]

        # For the "raw" question type, the answer value is any
        # JSONable Python data structure. Forward the getattr
        # request onto the value.
        # Similarly for file questions which have their own structure.
        elif self.question_type in ("raw", "file"):
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

    def __gt__(self, other):
        if isinstance(other, RenderedAnswer):
            other = other.answer
        if self.answer is None or other is None:
            # if either represents a skipped/imputed-null question,
            # prevent a TypeError by just returning false
            return False
        try:
            return self.answer > other
        except TypeError:
            # If one tries to compare a string to an integer, just
            # say false.
            return False

    def __lt__(self, other):
        if isinstance(other, RenderedAnswer):
            other = other.answer
        if self.answer is None or other is None:
            # if either represents a skipped/imputed-null question,
            # prevent a TypeError by just returning false
            return False
        try:
            return self.answer < other
        except TypeError:
            # If one tries to compare a string to an integer, just
            # say false.
            return False
