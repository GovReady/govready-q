from django.conf import settings
from jinja2.sandbox import SandboxedEnvironment

def get_jinja2_template_vars(template):
    from jinja2 import meta
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    return set(meta.find_undeclared_variables(env.parse(template)))


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


def evaluate_module_state(current_answers, required, parent_context=None):
    # Compute the next question to ask the user, given the user's
    # answers to questions so far, and all imputed answers up to
    # that point.
    #
    # To figure this out, we walk the dependency tree of questions
    # until we arrive at questions that have no unanswered dependencies.
    # Such questions can be put forth to the user.

    # Build a list of ModuleQuestions that the user may answer now.
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
        ModuleAnswers(current_answers.module, current_answers.task, {}), lambda q, a, v : str(v),
        parent_context=parent_context)

    # Visitor function.
    def walker(q, state, deps):
        # If any of the dependencies don't have answers yet, or if it's been
        # skipped but it's a non-skippable dependency, then this question
        # cannot be processed yet.
        for qq, skippable in deps.items():
            if qq.key not in state or (not skippable and state[qq.key][3] is None):
                unanswered.add(q)
                answertuples[q.key] = (q, False, None, None)
                return { }

        # Can this question's answer be imputed from answers that
        # it depends on? If the user answered this question (during
        # a state in which it wasn't imputed, but now it is), the
        # user's answer is overridden with the imputed value for
        # consistency with the Module's logic.
        
        # Create an evaluation context for evaluating impute conditions
        # that only sees the answers of this question's dependencies,
        # which are in state because we return the answers from this
        # method and they are collected as the walk continues up the
        # dependency tree. 
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
            # The user has provided an answer to this question.
            answerobj = current_answers.answertuples[q.key][2]
            v = current_answers.as_dict()[q.key]

            # If q is a required question and the required argument is true,
            # and the question was skipped ('None' answer) then treat it as unanswered.
            if q.spec.get("required") and required and v is None:
                can_answer.add(q)
                unanswered.add(q)
                answertuples[q.key] = (q, False, None, None)
                return state

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
            if self.answer_value is None:
                return "<i>skipped</i>"
            if not hasattr(LazyRenderedAnswer, 'tc'):
                LazyRenderedAnswer.tc = TemplateContext(answers, HtmlAnswerRenderer(show_metadata=False))
            return RenderedAnswer(answers.task, self.q, self.answer_obj, self.answer_value, LazyRenderedAnswer.tc).__html__()

    answers.as_dict() # force lazy-load
    context = []
    for q, is_answered, answer_obj, answer_value in answers.answertuples.values():
        # Skip imputed questions.
        if is_answered and answer_obj is None: continue
        context.append({
            "key": q.key,
            "title": q.spec['title'],
            "link": (answers.task.get_absolute_url() + "/question/" + q.key) if (answer_obj or q in answers.can_answer) else None, # any question that has been answered or can be answered next can be linked to
            "skipped": (answer_obj is not None and answer_value is None) and (q.spec["type"] != "interstitial"),
            "answered": answer_obj is not None,
            "reviewed": answer_obj.reviewed if answer_obj is not None else None,
            "is_this_question": (question is not None) and (q.key == question.key),
            "value": LazyRenderedAnswer(q, is_answered, answer_obj, answer_value),
        })

    return context


def render_content(content, answers, output_format, source, additional_context={},
    demote_headings=True, show_answer_metadata=False):

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
            from CommonMark import inlines
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
            template_body = re.sub("{%.*?%}|{{.*?}}", replace, template_body)

            # Render with a custom renderer to control output.
            import CommonMark
            class q_renderer(CommonMark.HtmlRenderer):
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
                    output_format,
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
        elif output_format == "PARSE_ONLY":
            # For tests, callers can use the "PARSE_ONLY" output format to
            # stop after the template is prepared.
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
            def escapefunc(question, answerobj, value):
                # Don't perform any escaping.
                return str(value)
    
        elif template_format == "html":
            escapefunc = HtmlAnswerRenderer(show_metadata=show_answer_metadata)

        # Execute the template.

        # Evaluate the template. Ensure autoescaping is turned on. Even though
        # we handle it ourselves, we do so using the __html__ method on
        # RenderedAnswer, which relies on autoescaping logic. This also lets
        # the template writer disable autoescaping with "|safe".
        import jinja2
        env = Jinja2Environment(
            autoescape=True,
            undefined=jinja2.StrictUndefined)
        try:
            template = env.from_string(template_body)
        except jinja2.TemplateSyntaxError as e:
            raise ValueError("There was an error loading the template %s: %s" % (source, str(e)))

        # For tests, callers can use the "PARSE_ONLY" output format to
        # stop after the template is compiled.
        if output_format == "PARSE_ONLY":
            return template

        # Create an intial context dict with the additional_context provided
        # by the caller, add additional context variables and functions, and
        # add rendered answers into it.
        context = dict(additional_context) # clone
        if answers:
            context['static_asset_path_for'] = answers.module.get_static_asset_url

        # Render.
        try:
            # context.update will immediately load all top-level values, which
            # unfortuntately might throw an error if something goes wrong
            if answers:
                context.update(TemplateContext(answers, escapefunc, root=True))

            # Now really render.
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

                def rewrite_url(url):
                    # Rewrite for static assets.
                    if answers is not None:
                        url = answers.module.get_static_asset_url(url)

                    # Check final URL.
                    import urllib.parse
                    u = urllib.parse.urlparse(url)
                    if u.scheme not in ("", "http", "https", "mailto"):
                        return "javascript:alert('Invalid link.');"
                    return url

                import html5lib, xml.etree
                dom = html5lib.HTMLParser().parseFragment(output)
                for node in dom.iter():
                    if node.get("href"):
                        node.set("href", rewrite_url(node.get("href")))
                    if node.get("src"):
                        node.set("src", rewrite_url(node.get("src")))
                output = html5lib.serialize(dom, quote_attr_values="always", omit_optional_tags=False, alphabetical_attributes=True)

                # But the p's within p's fix gives us a lot of empty p's.
                output = output.replace("<p></p>", "")

                return output

        raise ValueError("Cannot render %s to %s." % (template_format, output_format))
         
    else:
        raise ValueError("Invalid template format encountered: %s." % template_format)


class HtmlAnswerRenderer:
    def __init__(self, show_metadata):
        self.show_metadata = show_metadata
    def __call__(self, question, answerobj, value):
        import html

        if question is not None and question.spec["type"] == "longtext":
            # longtext fields are rendered into the output
            # using CommonMark. Escape initial <'s so they
            # are not treated as the start of HTML tags,
            # which are not permitted in safe mode, but
            # <'s appear tag-like in certain cases like
            # when we say <not answerd>.
            if value.startswith("<"): value = "\\" + value
            import CommonMark
            parsed = CommonMark.Parser().parse(value)
            value = CommonMark.HtmlRenderer({ "safe": True }).render(parsed)
            wrappertag = "div"

        elif question is not None and question.spec["type"] == "file" and question.spec.get("file-type") == "image" \
            and hasattr(value, "file_data"):
            # Image files turn into image tags.
            value = "<img src=\"" + html.escape(value.file_data['url']) + "\" style=\"display: block; margin: 1em\">"
            wrappertag = "div"

        else:
            # Regular text fields just get escaped.
            value = html.escape(str(value))
            wrappertag = "span"

        if not self.show_metadata or question is None or answerobj is None:
            return value

        # Wrap the output in a tag that holds metadata.
        return """<{tag} class='question-answer'
          data-module='{module}'
          data-question='{question}'
          data-edit-link='{edit_link}'
          data-answered-by='{answered_by}'
          data-answered-on='{answered_on}'
          data-reviewed='{reviewed}'
          >{value}</{tag}>""".format(
            tag=wrappertag,
            module=html.escape(question.module.spec['title']),
            question=html.escape(question.spec["title"]),
            edit_link=answerobj.taskanswer.get_absolute_url(),
            answered_by=html.escape(str(answerobj.answered_by)) if answerobj else "(value was imputed)",
            answered_on=html.escape(answerobj.created.strftime("%c")) if answerobj else "(n/a)",
            reviewed=str(answerobj.reviewed) if answerobj else "",
            value=value,
        )


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
        q: get_question_dependencies_with_skippable_flag(q, get_from_question_id=all_questions)
        for q in all_questions.values()
    }

    # Find the questions that are at the root of the dependency tree.
    is_dependency_of_something = set()
    for deps in dependencies.values():
        is_dependency_of_something |= set(deps.keys())
    root_questions = { q for q in dependencies if q not in is_dependency_of_something }

    ret = (dependencies, root_questions)

    # Save to in-memory (in-process) cache. Never in debugging.
    if not settings.DEBUG:
        get_all_question_dependencies.cache[module.id] = ret

    return ret

def get_question_dependencies(question, get_from_question_id=None):
    return set(edge[1] for edge in get_question_dependencies_with_type(question, get_from_question_id))

def get_question_dependencies_with_skippable_flag(question, get_from_question_id=None):
    edges = get_question_dependencies_with_type(question, get_from_question_id=get_from_question_id)
    # skippable if the question is not used in an impute condition
    return {
        q: "impute-condition" not in set(edge_type for (edge_type, q1) in edges if q1 == q)
        for q in set(q0 for (edge_type, q0) in edges)
    }

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
                    r"{% if " + rule["condition"] + r" %}...{% endif %}"
                    ):
                ret.append(("impute-condition", qid))

        if rule.get("value-mode") == "expression":
            for qid in get_jinja2_template_vars(
                    r"{% if " + rule["value"] + r" %}...{% endif %}"
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

def run_impute_conditions(conditions, context):
    # Check if any of the impute conditions are met based on
    # the questions that have been answered so far and return
    # the imputed value. Be careful about values like 0 that
    # are false-y --- must check for "is None" to know if
    # something was imputed or not.
    env = Jinja2Environment()
    for rule in conditions:
        if "condition" in rule:
            condition_func = env.compile_expression(rule["condition"])
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
                value = env.compile_expression(rule["value"])(context)
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

    def as_dict(self):
        if self.answertuples is None:
            # Lazy-load by calling the task's get_answers function
            # and copying its answers dictionary.
            if self.task is None:
                self.answertuples = { q.key: (q, False, None, None) for q in self.module.questions.order_by('definition_order') }
            else:
                self.answertuples = self.task.get_answers().answertuples
        if self.answers_dict is None:
            self.answers_dict = { q.key: value for q, is_ans, ansobj, value in self.answertuples.values() if is_ans }
        return self.answers_dict

    def with_extended_info(self, required=False, parent_context=None):
        # Return a new ModuleAnswers instance that has imputed values added
        # and information about the next question(s) and unanswered questions.
        return evaluate_module_state(self, required, parent_context=parent_context)

    def get_questions(self):
        self.as_dict() # lazy load if necessary
        return [v[0] for v in self.answertuples.values()]

    def render_output(self, additional_context):
        # Now that all questions have been answered, generate this
        # module's output. The output is a set of documents. The
        # documents are lazy-rendered because not all of them may
        # be used by the caller.
        class LazyRenderedDocument:
            def __init__(self, module_answers, document, index):
                self.module_answers = module_answers
                self.document = document
                self.index = index
                self.rendered_content = None
            def __getitem__(self, key):
                if key == "html":
                    if self.rendered_content is None:
                        # For errors, what is the name of this document?
                        if "id" in self.document:
                            doc_name = self.document["id"]
                        else:
                            doc_name = "at index " + str(self.index)
                            if "title" in self.document:
                                doc_name = repr(self.document["title"]) + " (" + doc_name + ")"
                        doc_name = "%s output document %s" % (self.module_answers.module.key, doc_name)

                        # Try to render it.
                        try:
                            self.rendered_content = render_content(self.document, self.module_answers, "html", doc_name, additional_context, show_answer_metadata=True)
                        except Exception as e:
                            # Put errors into the output. Errors should not occur if the
                            # template is designed correctly.
                            import html
                            self.rendered_content = "<p class=text-danger>" + html.escape(str(e)) + "</p>"

                    return self.rendered_content
                elif key in self.document:
                    return self.document[key]
                raise KeyError
            def get(self, key, default=None):
                if key == "html" or key in self.document:
                    return self[key]
        return [ LazyRenderedDocument(self, d, i) for i, d in enumerate(self.module.spec.get("output", [])) ]

from collections.abc import Mapping
class TemplateContext(Mapping):
    """A Jinja2 execution context that wraps the Pythonic answers to questions
       of a ModuleAnswers instance in RenderedAnswer instances that provide
       template and expression functionality like the '.' accessor to get to
       the answers of a sub-task."""

    def __init__(self, module_answers, escapefunc, parent_context=None, root=False):
        self.module_answers = module_answers
        self.escapefunc = escapefunc
        self.root = root
        self._cache = { }
        self.parent_context = parent_context

    def __getitem__(self, item):
        # Cache every context variable's value, since some items are expensive.
        if item not in self._cache:
            self._cache[item] = self.getitem(item)
        return self._cache[item]

    def _execute_lazy_module_answers(self):
        if callable(self.module_answers):
            self.module_answers = self.module_answers()
        self._module_questions = { q.key: q for q in self.module_answers.get_questions() }

    def getitem(self, item):
        self._execute_lazy_module_answers()

        # If 'item' matches an external function name (in the root template context only), return it.
        # Un-wrap RenderedAnswer instances so the external function gets the value and not the
        # RenderedAnswer instance.
        if self.root and item in self.module_answers.module.python_functions():
            func = self.module_answers.module.python_functions()[item]
            def arg_filter(arg):
                if isinstance(arg, RenderedAnswer):
                    return arg.answer
                return arg
            def wrapper(*args, **kwargs):
                return func(*map(arg_filter, args), **kwargs)
            return wrapper

        # If 'item' matches a question ID, wrap the internal Pythonic/JSON-able value
        # with a RenderedAnswer instance which take care of converting raw data values
        # into how they are rendered in templates (escaping, iteration, property accessors)
        # and evaluated in expressions.
        question = self._module_questions.get(item)
        if question:
            # The question might or might not be answered. If not, its value is None.
            self.module_answers.as_dict() # trigger lazy-loading
            answerobj, answervalue = self.module_answers.answertuples.get(item, (None, None, None, None))[2:4]
            return RenderedAnswer(self.module_answers.task, question, answerobj, answervalue, self)

        # The context also provides the project and organization that the Task belongs to,
        # and other task attributes, assuming the keys are not overridden by question IDs.
        if self.module_answers.task:
            if item == "task_link":
                return self.module_answers.task.get_absolute_url()
            if item == "project":
                if self.parent_context is not None: # use parent's cache
                    return self.parent_context[item]
                return RenderedProject(self.module_answers.task.project, parent_context=self)
            if item == "organization":
                if self.parent_context is not None: # use parent's cache
                    return self.parent_context[item]
                return RenderedOrganization(self.module_answers.task.project.organization, parent_context=self)
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
        self._execute_lazy_module_answers()

        seen_keys = set()

        # external functions, in the root template context only
        if self.root and self.module_answers.module:
            for fname in self.module_answers.module.python_functions():
                seen_keys.add(fname)
                yield fname

        # question names
        for q in self._module_questions.values():
            seen_keys.add(q.key)
            yield q.key

        # special values
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
    def __init__(self, project, parent_context=None):
        self.project = project
        def _lazy_load():
            if self.project.root_task:
                return self.project.root_task.get_answers()
        super().__init__(_lazy_load, parent_context.escapefunc, parent_context=parent_context)

    def as_raw_value(self):
        return self.project.title
    def __html__(self):
        return self.escapefunc(None, None, self.as_raw_value())

class RenderedOrganization(TemplateContext):
    def __init__(self, organization, parent_context=None):
        self.organization = organization
        def _lazy_load():
            project = organization.get_organization_project()
            if project.root_task:
                return project.root_task.get_answers()
        super().__init__(_lazy_load, parent_context.escapefunc, parent_context=parent_context)

    def as_raw_value(self):
        return self.organization.name
    def __html__(self):
        return self.escapefunc(None, None, self.as_raw_value())

class RenderedAnswer:
    def __init__(self, task, question, answerobj, answer, parent_context):
        self.task = task
        self.question = question
        self.answerobj = answerobj
        self.answer = answer
        self.parent_context = parent_context
        self.escapefunc = parent_context.escapefunc
        self.question_type = self.question.spec["type"]
        self.cached_tc = None

    def __html__(self):
        # How the template renders a question variable used plainly, i.e. {{q0}}.
        if self.answer is None:
            value = "<%s>" % self.question.spec['title']
        elif self.question_type == "multiple-choice":
            # Render multiple-choice as a comma+space-separated list
            # of the choice keys.
            value = ", ".join(self.answer)
        elif self.question_type == "file":
            # Pass something to the escapefunc that HTML rendering can
            # recognize as a file but non-HTML rendering sees as a string.
            class FileValueWrapper:
                def __init__(self, answer):
                    self.file_data = answer
                def __str__(self):
                    return "<uploaded file: " + self.file_data['url'] + ">"
            value = FileValueWrapper(self.answer)
        elif self.question_type == "module":
            value = self.answer.task.render_title()
        else:
            # For all other question types, just call Python str().
            value = str(self.answer)

        # And in all cases, escape the result.
        return self.escapefunc(self.question, self.answerobj, value)

    @property
    def text(self):
        # How the template renders {{q0.text}} to get a nice display form of the answer.
        if self.answer is None:
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
                value = ", ".join(get_question_choice(self.question, c)["text"] for c in self.answer)
        elif self.question_type in ("integer", "real"):
            # Use a locale to generate nice human-readable numbers.
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            value = locale.format(
                "%d" if self.question_type == "integer" else "%g",
                self.answer,
                grouping=True)
        elif self.question_type == "file":
            value = "<uploaded file: " + self.answer['url'] + ">"
        elif self.question_type == "module":
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
                return self.ra.escapefunc(self.ra.question, self.ra.answerobj, self.value)
        return SafeString(value, self)

    @property
    def edit_link(self):
        # Return a link to edit this question.
        return self.task.get_absolute_url_to_question(self.question)

    @property
    def output_documents(self):
        def make_error(item, msg):
            import html
            return "<p class='text-danger'>Template Error: output document %s in %s could not be rendered: %s</p>" % (
                item,
                html.escape(self.question.spec["id"]
                    + ("" if self.answer is None else "=>" + str(self.answer.task.module))),
                html.escape(str(msg)))

        # Return a class that lazy-renders output documents on request.
        answer = self.answer
        class LazyRenderer:
            def __getattr__(self, item):
                if answer is None:
                    return make_error(item, "The question is not answered.")

                try:
                    # Find the requested output document in the module.
                    for doc in answer.task.module.spec.get("output", []):
                        if doc.get("id") == item:
                            return render_content(doc, answer, "html", "%s output document %s" % (repr(answer.module), item), {})
                except AttributeError as e:
                    return make_error(item, e)

                # If the key doesn't match a document name we could throw an error but
                # that's disruptive so we show an error in the document itself.
                return make_error(item, "That is not the name of an output document.")
        return LazyRenderer()

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
                self.answerobj,
                ans, self.parent_context)
                for ans in self.answer)
        
        elif self.question_type == "module-set":
            # Iterate over the sub-tasks' answers. Load each's answers + imputed answers.
            return (TemplateContext(
                v.with_extended_info(parent_context=self.parent_context if not v.task or not self.task or v.task.project_id==self.task.project_id else None),
                self.escapefunc, parent_context=self.parent_context)
                for v in self.answer)

        elif self.question_type == "external-function":
            return iter(self.answer)

        raise TypeError("Answer of type %s is not iterable." % self.question_type)

    def __len__(self):
        if self.question_type in ("multiple-choice", "module-set", "external-function"):
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
                    tc = TemplateContext(ans, self.escapefunc, parent_context=self.parent_context)
                else:
                    # It is None when the question specifies a "protocol", in
                    # which case we don't know what questions the inner Module
                    # would have. Return a value that acts like a dict but always
                    # yields empty values.
                    class DD:
                        def __init__(self, path):
                            self.path = path
                        def __str__(self):
                            return "<not answered>"
                        def __html__(self):
                            import html
                            return html.escape(str(self))
                        def __getattr__(self, key):
                            return DD(self.path+[key])
                    return DD([self.question.spec['id']])
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

def run_external_function(question, answers, **additional_args):
    # Find and run the method.
    import copy # don't give the function referneces to ORM values
    function_name = question.spec.get("function", question.key)
    funcs = question.module.python_functions()
    if function_name not in funcs:
        raise Exception("Invalid function name %s in %s question %s. Available functions are %s." % (
        function_name, question.module, question.key,
        ",".join(name for name in funcs if callable(funcs[name]))
          if funcs else "[no functions defined]"
        )) # not trapped / not user-visible error
    method = funcs[function_name]
    return method(module=copy.deepcopy(question.module.spec), question=copy.deepcopy(question.spec), answers=answers.as_dict(), **additional_args)
