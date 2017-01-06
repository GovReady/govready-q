from django.conf import settings

def get_jinja2_template_vars(template):
    from jinja2 import meta
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    return set(meta.find_undeclared_variables(env.parse(template)))


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
        state = callback(q, state, deps)

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
    # The order is in depth-first order, i.e. all dependencies
    # are listed before what depends on them.
    unanswered = []

    # Build a new array of answer values.
    answers = { }

    # Build a list of questions whose answers were imputed.
    was_imputed = set()

    # Create some reusable context for evaluating impute conditions --- really only
    # so that we can pass down project and organization values. Everything else is
    # cleared from the context's cache for each question because each question sees
    # a different set of dependencies.
    impute_context_parent = TemplateContext(
        ModuleAnswers(current_answers.module, current_answers.task, {}), lambda v, mode : str(v),
        parent_context=parent_context)

    # Visitor function.
    def walker(q, state, deps):
        # If any of the dependencies don't have answers yet, then this
        # question cannot be processed yet.
        for qq in deps:
            if qq.key not in state:
                unanswered.append(q)
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
            v = v[0]
            was_imputed.add(q.key)

        elif q.key in current_answers.as_dict():
            # The user has provided an answer to this question.
            v = current_answers.as_dict()[q.key]

            # If q is a required question and the required argument is true,
            # and the question was skipped ('None' answer) then treat it as unanswered.
            if q.spec.get("required") and required and v is None:
                can_answer.add(q)
                unanswered.append(q)
                return state

        elif current_answers.module.spec.get("type") == "project" and q.key == "_introduction":
            # Projects have an introduction but it isn't displayed as a question.
            # It's not explicitly answered, but treat it as answered so that questions
            # that implicitly depend on it can be evaluated.
            v = None

        else:
            # This question does not have an answer yet. We don't set
            # anything in the state that we return, which flags that
            # the question is not answered.
            #
            # But we can remember that this question *can* be answered
            # by the user, and that it's not answered yet.
            can_answer.add(q)
            unanswered.append(q)
            return state

        # Update the state that's passed to questions that depend on this
        # and also the global state of all answered questions.
        state[q.key] = v
        answers[q.key] = v
        return state

    # Walk the dependency tree.
    walk_module_questions(current_answers.module, walker)

    # There may be multiple routes through the tree of questions,
    # so we'll prefer the question that is defined first in the spec.
    can_answer = sorted(can_answer, key = lambda q : q.definition_order)

    # Create a new ModuleAnswers object that holds the user answers,
    # imputed answers (which override user answers), and next-question
    # information.
    ret = ModuleAnswers(current_answers.module, current_answers.task, answers)
    ret.was_imputed = was_imputed
    ret.unanswered = unanswered
    ret.can_answer = can_answer
    return ret


def get_question_context(answers, question):
    # What is the context of questions around the given question so show
    # the user their progress through the questions?

    # Start with questions in the order in which they were first answered,
    # so that we have a stable representation of what's been seen and that
    # no matter what question the user returns to, the questions listed
    # before and after that point accurately reflect the questions the user
    # actually answered before and after that point.
    context = []
    for ans in answers.task.answers.order_by('created').select_related('question'):
        # We may have a TaskAnswer record (to attach a Discussion to, for
        # instance) but no actual answers yet.
        if not ans.has_answer():
            continue

        q = ans.question

        # Don't show questions that are overridden by imputed values.
        if q.key in answers.was_imputed:
            continue

        # Add this record.
        context.append({
            "key": q.key,
            "title": q.spec['title'],
            "can_link": True, # any non-imputed (checked above) question can be re-answered
            "answered": ans.has_answer() and not ans.get_current_answer().is_skipped(),
            "is_this_question": (question is not None) and (q.key == question.key),
        })

    # Add questions that we will ask in the future. The
    # unanswered list is in depth-first order by the
    # dependency tree, which means it should be in the
    # order that they will get asked of the user.
    for q in answers.unanswered:
        context.append({
            "key": q.key,
            "title": q.spec['title'],
            "can_link": q in answers.can_answer, # any question that can be answered next can be linked to
            "answered": False,
            "is_this_question": (question is not None) and (q.key == question.key),
        })


    return context


def render_content(content, answers, output_format, source, additional_context={}):
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
                    if "\uE000" in node.destination:
                        # Don't mess with the URL if it contains any template
                        # tags. We can't tell what the URL will be, so let's
                        # require that it be absolute.
                        return node.destination
                    import urllib.parse
                    base_path = "/static/module-assets/"
                    if not node.destination.startswith("/") and answers is not None:
                        # Assets are relative to the module's 'path'. (If answers is
                        # none, we're probably just calling this method on test data.)
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

        # Evaluate the template. Ensure autoescaping is turned on. Even though
        # we handle it ourselves, we do so using the __html__ method on
        # RenderedAnswer, which relies on autoescaping logic. This also lets
        # the template writer disable autoescaping with "|safe".
        import jinja2
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment(
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

        # Create an intial context dict and add rendered answers into it.
        context = dict(additional_context) # clone
        context.update(TemplateContext(answers, escapefunc, root=True))

        # Render.
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

        if rule.get("value-mode") == "expression":
            for qid in get_jinja2_template_vars(
                    r"{% if " + rule["value"] + r" %}...{% endif %}"
                    ):
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
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    for rule in conditions:
        condition_func = env.compile_expression(rule["condition"])
        try:
            value = condition_func(context)
        except:
            value = None
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
            else:
                raise ValueError("Invalid impute condition value-mode.")

            # Since the imputed value may be None, return
            # the whole thing in a tuple to distinguish from
            # a None indicating the lack of an imputed value.
            return (value,)
    return None

class question_input_parser:
    # Turns client-side input into the correct JSON-serializable
    # Python data structure for a particular question type.
    #
    # The input is typically a string submitted by an <input> field,
    # which is passed to this function by request.POST.getlist(),
    # giving us an array of strings.
    #
    # But file-type questions are given by request.FILES.get(), which
    # gives a Django UploadedFile instance.
    #
    # The output of the parse function is a JSON-serializable data
    # structure that matches the structure that export_json/import_json
    # functions use, because that's the format that the validator
    # functions expect since the validator is used both for web input
    # and imported input.
    @classmethod
    def parse(_class, question, value):
        # Mangle value a bit.
        if question.spec["type"] == "multiple-choice":
            # A list of strings is what we want here.
            pass

        elif question.spec["type"] == "file":
            # An UploadedFile instance is what we want here.
            pass

        else:
            # For all other question types, turn the array of strings
            # into a single string.
            if len(value) > 1:
                raise ValueError("Invalid input: Multiple values submitted.")
            elif len(value) == 0:
                raise ValueError("Invalid input: No value submitted.")
            else:
                value = value[0].strip()

        # Get the parser function and run it on the value.
        func = getattr(_class, "parse_" + question.spec["type"].replace("-", "_"))
        return func(question, value)

    # The textual question types don't need to be parsed. They come
    # as strings and are stored as strings.
    def parse_text(question, value):
        return value
    def parse_password(question, value):
        return value
    def parse_email_address(question, value):
        return value
    def parse_url(question, value):
        return value
    def parse_longtext(question, value):
        return value
    def parse_date(question, value):
        return value

    # Likewise for the simple choice types.
    def parse_choice(question, value):
        return value
    def parse_yesno(question, value):
        return value

    def parse_multiple_choice(question, value):
        # Comes in from the view function as an array of strings, which is what we want.
        return value

    def parse_integer(question, value):
        # First parse it as a real using localization.
        value = question_input_parser.parse_real(question, value)

        # Then ensure is an integer.
        if value != int(value):
            raise ValueError("Invalid input. Must be a whole number.")

        # Finally, convert data type.
        return int(value)

    def parse_real(question, value):
        try:
            # Use a locale to parse human input since it may have
            # e.g. thousands-commas.
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 
            return locale.atof(value)
        except ValueError:
            # make a nicer error message
            raise ValueError("Invalid input. Must be a number.")

    def parse_file(question, value):
        # This comes in as a Django File instance. Convert it to the
        # data structure used for export/import.

        # Otherwise, we get an UploadedFile instance.
        import django.core.files.uploadedfile
        if not isinstance(value, django.core.files.uploadedfile.UploadedFile):
            raise ValueError("Invalid data type.")

        # Pull the whole file into memory and return the JSON data structure.
        # Encode the content as an array of (short) base-64 strings.
        # TODO: Maybe check value.charset and do transcoding to utf-8?
        import re
        from base64 import b64encode
        return {
            "content": re.findall(".{1,64}", b64encode(value.read()).decode("ascii")),
            "type": value.content_type, # as given by the client
        }

    def parse_module(question, value):
        # handled by view function
        return value

    def parse_interstitial(question, value):
        # interstitials have no actual answer - we should always
        # get "" - and the internal value is always None.
        if value != "":
            raise ValueError("Invalid input.")
        return None

    def parse_external_function(question, value):
        # the user doesn't answer these directly
        if value != "":
            raise ValueError("Invalid input.")
        return None # doesn't matter

class validator:
    # Validate that an answer is of the right data type and meets the
    # criteria of a question, and returns a normalized value.
    @classmethod
    def validate(_class, question, value):
        validate_func = getattr(_class, "validate_" + question.spec["type"].replace("-", "_"))
        return validate_func(question, value)

    def validate_text(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value))
        value = value.strip()
        if value == "":
            raise ValueError("Value is empty.")
        return value

    def validate_password(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)
        return value

    def validate_email_address(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)

        # Then validate and normalize the value as an email address.
        import email_validator
        return email_validator.validate_email(value)["email"]

    def validate_url(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)

        # Then validate and normalize the URL.
        from django.core.validators import URLValidator
        urlvalidator = URLValidator()
        try:
            urlvalidator(value)
        except:
            raise ValueError("That is not a valid web address.")
        return value

    def validate_longtext(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)
        return value

    def validate_date(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)

        # Validate that we have a valid date in YYYY-MM-DD format. A client-side
        # tool should be responsible for ensuring that the user entry is translated
        # into this format.
        import re, datetime
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

        # Return the original string (not a datetime instance).
        return value

    def validate_choice(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value))
        if value not in { choice['key'] for choice in question.spec["choices"] }:
            raise ValueError("invalid choice")
        return value

    def validate_yesno(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value))
        if value not in ("yes", "no"):
            raise ValueError("invalid choice")
        return value

    def validate_multiple_choice(question, value):
        if not isinstance(value, list):
            raise ValueError("Invalid data type (%s)." % type(value))
        for item in value:
            if item not in { choice['key'] for choice in question.spec["choices"] }:
                raise ValueError("invalid choice: " + item)
        if len(value) < question.spec.get("min", 0):
            raise ValueError("not enough choices")
        if question.spec.get("max") and len(value) > question.spec["max"]:
            raise ValueError("too many choices")
        return value

    def validate_integer(question, value):
        if not isinstance(value, int):
            raise ValueError("Invalid data type (%s)." % type(value))
        value = validator._validate_number(question, value)
        return value

    def validate_real(question, value):
        if not isinstance(value, float):
            raise ValueError("Invalid data type (%s)." % type(value))
        value = validator._validate_number(question, value)
        return value

    @staticmethod
    def _validate_number(question, value):
        # This method is used on ints and floats.
        if "min" in question.spec and value < question.spec["min"]:
            raise ValueError("Must be at least %g." % question.spec["min"])
        if "max" in question.spec and value > question.spec["max"]:
            raise ValueError("Must be at most %g." % question.spec["max"])
        return value

    def validate_file(question, value):
        # The JSON-serializable data structure for a file is a dict like:
        #
        # {
        #   "content": [ array of Base64-encoded strings ],
        #   "contentType": "text/plain",
        # }
        #
        # Turn this into a Django ContentFile instance which is how we'll
        # save it into the database.

        # Check data type.
        if not isinstance(value, dict):
            raise ValueError("Invalid data type (%s)." % type(value))
        if not isinstance(value.get("content"), list):
            raise ValueError("Invalid data type.")
        if not isinstance(value.get("type"), str):
            raise ValueError("Invalid data type.")

        # Fetch content.
        from base64 import b64decode
        content = b64decode("".join(str(chunk) for chunk in value["content"]).encode("ascii"))

        # The file must have content.
        if len(content) == 0:
            raise ValueError("File is empty.")

        # If the file is expected to be an image, then load it to ensre it is
        # a valid image, and sanitize it by round-tripping it through Pillow.
        # This purposefully is intended to lose image metadata, to protect
        # the user. (TODO: Test that it actually drops XMP metadata.)
        if question.spec.get("file-type") == "image":
            # Load the image.
            from io import BytesIO
            from PIL import Image
            try:
                im = Image.open(BytesIO(content))
                im.load() # force read from buffer so that exceptions are raised now
            except:
                raise ValueError("That's not an image file.")

            imspec = question.spec.get("image", {})
            
            # Apply a size constraint and resize the image in-place.
            if imspec.get("max-size"):
                # TODO: Validate the size width/height fields are integers.
                size = imspec["max-size"]
                im.thumbnail(( size.get("width", im.size[0]), size.get("width", im.size[1])  ))

            # Write the image back to a new buffer.
            buf = BytesIO()
            im.save(buf, "PNG")
            content = buf.getvalue()

        # Turn it into a Django ContentFile instance.
        from django.core.files.base import ContentFile
        value = ContentFile(content)
        value.name = "image.png" # needs a name for the storage backend?
        return value

    def validate_module(question, value):
        # handled by caller function
        return value

    def validate_module_set(question, value):
        # handled by caller function
        return value

    def validate_interstitial(question, value):
        # interstitials have no actual answer - we should always
        # store None.
        if value is not None:
            raise ValueError("Invalid data type (%s)." % type(value))
        return value

    def validate_external_function(question, value):
        # Any data structure is OK.
        return value

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

    def as_dict(self):
        if self.answers is None:
            # Lazy-load by calling the task's get_answers function
            # and copying its answers dictionary.
            self.answers = self.task.get_answers().answers
        return self.answers

    def with_extended_info(self, required=False, parent_context=None):
        # Return a new ModuleAnswers instance that has imputed values added
        # and information about the next question(s) and unanswered questions.
        return evaluate_module_state(self, required, parent_context=parent_context)

    def render_output(self, additional_context):
        # Now that all questions have been answered, generate this
        # module's output. The output is a set of documents.
        def render_document(d, i):
            ret = { }
            ret.update(d) # keep all original fields (especially 'name', 'tab')
            ret["html"] = render_content(d, self, "html", "%s output document %d" % (repr(self.module), i), additional_context)
            return ret
        return [ render_document(d, i) for i, d in enumerate(self.module.spec.get("output", [])) ]

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
        self._module_questions_map = parent_context._module_questions_map if parent_context is not None else { }

    def __getitem__(self, item):
        # Cache every context variable's value, since some items are expensive.
        if item not in self._cache:
            self._cache[item] = self.getitem(item)
        return self._cache[item]

    def _execute_lazy_module_answers(self):
        if callable(self.module_answers):
            self.module_answers = self.module_answers()

        # Pre-load all of the ModuleQuestions for the Module from the database.
        if not self._module_questions_map.get(self.module_answers.module):
            from collections import OrderedDict
            module_questions = OrderedDict()
            for q in self.module_answers.module.questions.order_by('definition_order'):
                module_questions[q.key] = q
            self._module_questions_map[self.module_answers.module] = module_questions
        self._module_questions = self._module_questions_map[self.module_answers.module]

    def getitem(self, item):
        self._execute_lazy_module_answers()

        # If 'item' matches an external function name (in the root template context only), return it.
        # Un-wrap RenderedAnswer instances so the external function gets the value and not the
        # RenderedAnswer instance.
        if self.root and item in self.module_answers.module.spec.get("external-functions", []):
            func = find_external_function(self.module_answers.module.key, item)
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
            answer = self.module_answers.as_dict().get(item, None)
            return RenderedAnswer(self.module_answers.task, question, answer, self)

        # The context also provides the project and organization that the Task belongs to,
        # and other task attributes, assuming the keys are not overridden by question IDs.
        if self.module_answers.task:
            if item == "task_link":
                return self.module_answers.task.get_absolute_url()
            if item == "project":
                if self.parent_context is not None: # use parent's cache
                    return self.parent_context[item]
                return RenderedProject(self.module_answers.task.project, self.escapefunc, parent_context=self)
            if item == "organization":
                if self.parent_context is not None: # use parent's cache
                    return self.parent_context[item]
                return RenderedOrganization(self.module_answers.task.project.organization, self.escapefunc, parent_context=self)
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
        if self.root:
            for fname in self.module_answers.module.spec.get("external-functions", []):
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
    def __init__(self, project, escapefunc, parent_context=None):
        self.project = project
        def _lazy_load():
            if self.project.root_task:
                return self.project.root_task.get_answers()
        super().__init__(_lazy_load, escapefunc, parent_context=parent_context)

    def as_raw_value(self):
        return self.project.title
    def __html__(self):
        return self.escapefunc(self.as_raw_value(), False)

class RenderedOrganization(TemplateContext):
    def __init__(self, organization, escapefunc, parent_context=None):
        self.organization = organization
        def _lazy_load():
            project = organization.get_organization_project()
            if project.root_task:
                return project.root_task.get_answers()
        super().__init__(_lazy_load, escapefunc, parent_context=parent_context)

    def as_raw_value(self):
        return self.organization.name
    def __html__(self):
        return self.escapefunc(self.as_raw_value(), False)

class RenderedAnswer:
    def __init__(self, task, question, answer, parent_context):
        self.task = task
        self.question = question
        self.answer = answer
        self.parent_context = parent_context
        self.escapefunc = parent_context.escapefunc
        self.question_type = self.question.spec["type"]
        self.cached_tc = None

    def __html__(self):
        # How the template renders a question variable used plainly, i.e. {{q0}}.
        if self.answer is None:
            value = "<%s>" % self.question.spec['title']
        elif self.question_type == "longtext":
            # Use a different escapefunc mode.
            return self.escapefunc(self.answer, True)
        elif self.question_type == "multiple-choice":
            # Render multiple-choice as a comma+space-separated list
            # of the choice keys.
            value = ", ".join(self.answer)
        elif self.question_type == "file":
            value = "<uploaded file: " + self.answer['url'] + ">"
        elif self.question_type == "module":
            value = self.answer.task.render_title()
        else:
            # For all other question types, just call Python str().
            value = str(self.answer)

        # And in all cases, escape the result.
        return self.escapefunc(value, False)

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
            raise Exception() # not reachable because getattr is overridden
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
        return SafeString(value, lambda value : self.escapefunc(value, self.question_type == "longtext" and self.answer is not None))

    @property
    def edit_link(self):
        # Return a link to edit this question.
        return self.task.get_absolute_url_to_question(self.question)

    def rendered_outputs(self):
        if self.question_type == "module":
            try:
                return self.answer.task.render_output_documents()
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
                # to gracefully represent the item attribute as skipped too.
                tc = TemplateContext(ModuleAnswers(self.question.answer_type_module, None, {}), self.escapefunc, parent_context=self.parent_context)
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

def find_external_function(module_id, function_name):
    if "." not in function_name:
        # Load the function from the Python module that is named the same
        # as the questions module. Since our modules directory is in the
        # Python path, those Python files will be available to us to load.
        # See siteapp/wsgi.py.
        module_name = module_id.replace("/", ".")
    else:
        # Split the function name into the module path and function name.
        try:
            module_name, function_name = function_name.rsplit(".", 1)
        except:
            raise Exception("Invalid function name.") # not trapped / not user-visible error

    # Import the module and get the method.
    import importlib
    module = importlib.import_module(module_name)
    return getattr(module, function_name)

def run_external_function(module_id, question, existing_answers):
    # Find and run the method.
    function_name = question.get("function", "")
    method = find_external_function(module_id, function_name)
    return method(question, existing_answers)
