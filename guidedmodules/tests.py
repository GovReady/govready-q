from django.contrib.auth.models import Permission
from django.db.models import Q
from django.test import TestCase
from siteapp.models import Organization, Project, User
from .app_loading import load_app_into_database
from .models import Module, Task, AppVersion
from .module_logic import *


class TestCaseWithFixtureData(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # In order for these tests to succeed when not connected to the
        # Internet, disable email deliverability checks which query DNS.
        settings.VALIDATE_EMAIL_DELIVERABILITY = False

        # Load modules from the fixtures directory.
        from .models import AppSource, AppVersion
        from .app_source_connections import MultiplexedAppSourceConnection
        src = AppSource.objects.create(
            slug="fixture",
            spec={
                "type": "local",
                "path": "fixtures/modules/other",
            }
        )
        with MultiplexedAppSourceConnection(ms for ms in AppSource.objects.all()) as store:
            for app in store.list_apps():
                appver = load_app_into_database(app)
                appver.show_in_catalog = True
                appver.save()
        self.fixture_app = AppVersion.objects.get(source=src, appname="simple_project")

        # Create a dummy organization, project, and user.
        self.user = User.objects.create(username="unit.test", email='regular@example.org')
        self.superuser = User.objects.create_superuser(username="superunit.test", email='super@example.org')
        self.organization = Organization.objects.create(name="My Supreme Organization")
        self.project = Project.objects.create(organization=self.organization)
        self.project.root_task = Task.objects.create(module=Module.objects.get(app=self.fixture_app, module_name="app"), project=self.project, editor=self.user)
        self.project.save()

    def getModule(self, module_name):
        return self.fixture_app.modules.get(module_name=module_name)

class ImputeConditionTests(TestCaseWithFixtureData):
    # Tests that expressions have the expected value in impute conditions
    # and that they have the *same* truthy-ness when used in {% if ... %}
    # blocks in templates.

    def _test_impute_condition(self, module, question_key, question_value, condition, value, value_mode, expected_to_match, expected_value):
        # Create a context to evaluate the impute condition in, using
        # the provided module and with a single question answered.
        m = self.getModule(module)
        answers = ModuleAnswers(m, None, { question_key: (m.questions.get(key=question_key), True, None, question_value) })
        context = TemplateContext(answers, lambda question, task, is_answered, answerobj, value : str(value)) # escapefunc

        # Build the impute condition.
        impute_condition = { }
        if condition is not None: impute_condition["condition"] = condition
        impute_condition["value"] = value
        if value_mode is not None: impute_condition["value-mode"] = value_mode

        # Run the impute condition.
        result = run_impute_conditions([impute_condition], context)

        # Test if the impute condition properly matched or didn't match.
        self.assertEqual(result is not None, expected_to_match, msg="impute condition '{}' condition test".format(condition))

        # Test if the impute condition had the right value. The result, if not None,
        # comes back wrapped in a tuple.
        if result is not None:
            result = result[0]
            self.assertEqual(result, expected_value, msg="impute condition '{}' value".format(condition))

        if condition is not None:
            # Test that an {% if ... %} block around the condition has the same truth value when used in a template.
            if_block = render_content(
                {
                    "format": "text",
                    "template": r"{% if " + condition + r" %}TRUE{% else %}FALSE{% endif %}",
                },
                answers,
                "text",
                str(self), # source
            )
            self.assertEqual(if_block == "TRUE", expected_to_match, msg="{%% if %s %%}" % condition)


    def _test_condition_helper(self, module, question_key, question_value, condition, expected):
        # Test the condition part of an impute condition. The value is hard-coded as True.
        self._test_impute_condition(
            module,
            question_key, question_value,
            condition, True, None,
            expected, True)


    def test_impute_using_text_questions(self):
        test = lambda *args : self._test_condition_helper("question_types_text", *args)

        # all of the text field types have the same behavior in impute conditions
        for fieldname in ("q_text", "q_password", "q_email_address", "q_url", "q_longtext", "q_date"):
            test(fieldname, "Hello!", "%s" % fieldname,           True) # answered is truthy
            test(fieldname, "Hello!", "%s=='Hello!'" % fieldname, True)
            test(fieldname, "Hello!", "%s!='Hello!'" % fieldname, False)
            test(fieldname, None,     "%s" % fieldname,           False) # skipped is falsey

        # Are there other sensible things we can do with dates?
        #test("q_date", "2016-10-28", "q_text < '2017-01-01'", True)

    def test_impute_using_choice_questions(self):
        test = lambda *args : self._test_condition_helper("question_types_choice", *args)

        test("q_choice", "choice1", "q_choice", True) # answered is truthy
        test("q_choice", "choice1", "q_choice == 'choice1'", True)
        test("q_choice", None, "q_choice", False) # skipped is falsey

        test("q_yesno", "yes", "q_yesno", True) # answered yes is truthy
        test("q_yesno", "no", "q_yesno", False) # answered no is falsey
        test("q_yesno", "yes", "q_yesno == 'yes'", True)
        test("q_yesno", "no", "q_yesno == 'no'", True)
        test("q_yesno", None, "q_yesno", False) # skipped is falsey

        test("q_multiple_choice", [], "q_multiple_choice", True) # answered is truthy even if answered with nothing chosen
        test("q_multiple_choice", ["choice1", "choice3"], "'choice1' in q_multiple_choice", True)
        test("q_multiple_choice", ["choice1", "choice3"], "'choice2' in q_multiple_choice", False)
        test("q_multiple_choice", None, "q_multiple_choice", False) # skipped is falsey

        # test("q_datagrid", [], "q_datagrid", True) # answered is truthy even if answered with nothing chosen
        # test("q_datagrid", ["field1", "field3"], "'field1' in q_datagrid", True)
        # test("q_datagrid", ["field1", "field3"], "'field2' in q_datagrid", False)
        # test("q_datagrid", None, "q_datagrid", False) # skipped is falsey

    def test_impute_using_numeric_questions(self):
        test = lambda *args : self._test_condition_helper("question_types_numeric", *args)

        test("q_integer", 0, "q_integer", True) # answered is truthy, even if answer would be falsey in Python
        test("q_integer", 0, "q_integer == 0", True)
        #test("q_integer", 1, "q_integer > 0", True)
        test("q_integer", None, "q_integer", False) # skipped is falsey

        test("q_real", 0.0, "q_real", True) # answered is truthy, even if answer would be falsey in Python
        test("q_real", 0.0, "q_real == 0", True)
        #test("q_real", 1.0, "q_real > 0", True)
        test("q_real", None, "q_real", False) # skipped is falsey

    def test_impute_using_media_questions(self):
        test = lambda *args : self._test_condition_helper("question_types_media", *args)

        # The "file" question type yields a dictionary with metadata about
        # the uploaded file -- it isn't normally rendered directly.
        file_metadata = {
            "url": "some-url-here",
            "size": 1024,
            "type": "text/plain",
        }
        test("q_file", file_metadata, "q_file", True) # answered is truthy
        test("q_file", None, "q_file", False) # skipped is falsey

        # Interstitial questions never have value.
        test("q_interstitial", None, "q_interstitial", False)

    def test_impute_using_module_questions(self):
        test = lambda *args : self._test_condition_helper("question_types_module", *args)

        # Create a sub-task that answers a question.
        m = Module.objects.get(module_name="simple") # the module ID that can answer the q_module question
        value = ModuleAnswers(
            m,
            Task.objects.create(module=m, editor=self.user, project=self.project),
            {
                "_introduction": (m.questions.get(key="_introduction"), True, None, None), # must be answered for q1 to have a value
                "q1": (m.questions.get(key="q1"), True, None, "My Answer"),
            })

        test("q_module", value, "q_module", True) # answered is truthy
        test("q_module", value, "q_module.q1", True) # sub-answer test
        test("q_module", None, "q_module", False) # skipped is falsey
        test("q_module", None, "q_module.q1", False) # skipped is falsey for all sub-answers

        # TODO: Test module-set questions.

    def test_impute_value_mode_expression(self):
        # Test the `value-mode: expression` impute conditions.

        # In normal impute conditions the value is interpreted as a Python data structure,
        # as parsed by YAML. This method evaluates a Jinja2 expression. In these tests the
        # condition is passed as None, which omits the condition, which means it always
        # matches --- we're only testing the value here.

        def test(expression, expected_value):
            self._test_impute_condition(
                "question_types_text",
                "q_text", "HELLO THERE",
                None, expression, "expression",
                True, expected_value)

        # various Jinja2 expressions
        test("1", 1)
        test("'1'", '1')
        test("q_text", 'HELLO THERE')


    def test_impute_value_mode_template(self):
        # Test the `value-mode: template` impute conditions.

        # In normal impute conditions the value is interpreted as a Python data structure,
        # as parsed by YAML. This method evaluates a Jinja2 template. In these tests the
        # condition is passed as None, which omits the condition, which means it always
        # matches --- we're only testing the value here.

        def test(expression, expected_value):
            self._test_impute_condition(
                "question_types_text",
                "q_text", "HELLO THERE",
                None, expression, "template",
                True, expected_value)

        # various Jinja2 templates
        test("1", "1")
        test("{% if 0 %}HELLO{% endif %}", '')
        test("{{q_text}}", 'HELLO THERE')

    def test_impute_conditions_in_module(self):
        # Test that impute conditions are actually working in a real module.

        # Take a Module and start it with no answers.
        m = self.getModule("impute_conditions")
        answers = ModuleAnswers(m, None, { })

        # Run impute conditions.
        answers = answers.with_extended_info()
        self.assertEqual(len(answers.was_imputed), 3)

        # Check imputed values.
        answers = answers.as_dict()
        self.assertEqual(answers.get("im_expr_1"), 2)
        self.assertEqual(answers.get("im_templ_1"), '1')
        self.assertEqual(answers.get("im_templ_2"), '2')

class RenderTests(TestCaseWithFixtureData):
    ## GENERAL RENDER TESTS ##

    def test_render_markdown_to_text(self):
        self.assertEqual(
            self.render_content(
                "question_types_text",
                "markdown", "*Hello*",
                { }, "text"),
            "*Hello*")

    def test_render_markdown_to_html(self):
        def test(template, context, expected):
            self.assertEqual(
                self.render_content(
                    "question_types_text",
                    "markdown", template,
                    context,
                    "html"),
                expected)

        # test that CommonMark rules are applied
        test("*Hello*", { }, "<p><em>Hello</em></p>")

        # test that some unsafe parts of CommonMark are applied, since we
        # are using them, though this is probably bad.
        test("<style>style tags</style>", { }, "<style>style tags</style>")

        # test that CommonMark in a regular text field is *not* applied
        test(
            "{{q_text}}",
            {
                "q_text": "**Hello** <b>not bold</b>",
            },
            "<p>**Hello** &lt;b&gt;not bold&lt;/b&gt;</p>")

        # test that CommonMark in a longtext field *is* applied
        # (It's output isn't create because it nests <p>'s but
        # that's something to fix later. TODO.)
        test(
            "{{q_longtext}}",
            {
                "q_longtext": "**Hello**",
            },
            "<p><strong>Hello</strong></p>")

        # test variable substitutions mixed with CommonMark links
        test(
            "[{{q_text}}](https://www.google.com/)",
            {
                "q_text": "**Hello**",
            },
            """<p><a href="https://www.google.com/">**Hello**</a></p>""")
        test(
            "[This is a Link!]({{q_text}})",
            {
               "q_text": "https://www.google.com/",
            },
            """<p><a href="https://www.google.com/">This is a Link!</a></p>""")

        # test URL rewriting on links & images for module static content
        test("![](test_asset.png)", { },
            """<p><img alt="" src="/tasks/500/test-the-text-input-question-types/media/test_asset.png"></p>""")

        # test variable substitutions mixed with CommonMark block elements
        test(
            "> This is a\n> blockquote with\n> {{q_text}}\n\n> This is blockquote has\n> {{q_longtext}}\n\n",
            {
                "q_text": "newlines\n\ncollapsed.",
                "q_longtext": "substituted\n\nmulti-paragraph\n\ntext.",
            },
            '<blockquote>\n<p>This is a\nblockquote with\nnewlines\n\ncollapsed.</p>\n</blockquote>\n<blockquote>\n<p>This is blockquote has\n</p><p>substituted</p>\n<p>multi-paragraph</p>\n<p>text.</p>\n\n</blockquote>')

    def test_render_markdown_to_html_exploits(self):
        def test(template, context, expected):
            self.assertEqual(
                self.render_content(
                    "question_types_text",
                    "markdown", template,
                    context,
                    "html"),
                expected)

        # Test that templates are rendered in safe mode.
        # (We don't turn on safe mode currently because we are using those
        # aspects of CommonMark in our templates.)

        # # Unsafe URLs are blocked.
        # test(
        #     r"[link](javascript:alert\(window\))",
        #     { },
        #     "<p><a>link</a></p>")
        # test(
        #     r"![link](data:image/svg+xml,<svg></svg>)",
        #     { },
        #     '<p><img src="" alt="link" /></p>')

        # # Raw HTML is blocked.
        # test(
        #     '''<a href="" onclick="alert('uh-oh')">click me</a>''',
        #     { },
        #     '<p><!-- raw HTML omitted -->click me<!-- raw HTML omitted --></p>')


        # Test that unsafe script content cannot be inserted by
        # variable substitution.

        test(
            "[This is a Link]({{q_text}})",
            {
                "q_text": r"javascript:alert(window)",
            },
            '<p><a href="javascript:alert(\'Invalid link.\');">This is a Link</a></p>')

        test(
            "![image]({{q_text}})",
            {
                "q_text": "data:image/svg+xml,<svg></svg>",
            },
            '<p><img alt="image" src="javascript:alert(\'Invalid link.\');"></p>')

        test(
            "```info{{q_text}}\nFenced block\n```",
            {
                "q_text": " myclass",
            },
            '<pre><code>Fenced block\n</code></pre>')

        # Since longtext fields are evaluated as CommonMark, they
        # create another vector.

        # Unsafe URLs are blocked.
        test(
            "{{q_longtext}}",
            {
                "q_longtext": r"[link](javascript:alert\(window\))",
            },
            "<p><a>link</a></p>")
        test(
            "{{q_longtext}}",
            {
                "q_longtext": r"![image](data:image/svg+xml,<svg></svg>)",
            },
            '<p><img alt="image" src=""></p>')

        # Raw HTML is blocked.
        test(
            "{{q_longtext}}",
            {
                "q_longtext": '''this is bad: <a href="" onclick="alert('uh-oh')">click me</a>''',
            },
            '<p>this is bad: <!-- raw HTML omitted -->click me<!-- raw HTML omitted --></p>')

    def render_content(self, module, template_format, template, answers, output_format):
        m = self.getModule(module)
        t = Task(id=500, module=m, project=self.project, extra={})
        return render_content(
            {
                "format": template_format,
                "template": template,
            },
            ModuleAnswers(m, t, { k: (m.questions.get(key=k), True, None, v) for k, v in answers.items() }),
            output_format,
            str(self), # source
        ).strip()

    ## RENDERING ANSWERS ##
    #
    # Render {{question}}, which yields (a display form of) the raw value,
    # and {{question.text}} which yields a human-readable value. Do this for
    # test values as well as the None value which represents an unanswered
    # or skipped question.

    def test_render_text_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_text", *args)

        from html import escape

        test("q_text", "Hello!", "Hello!")
        test("q_text.text", "Hello!", "Hello!")
        test("q_text", None, escape("<text>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_text.text", None, escape("<not answered>"))

        test("q_password", "1234", "1234")
        test("q_password.text", "1234", "1234")
        test("q_password", None, escape("<password>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_password.text", None, escape("<not answered>"))
        
        test("q_email_address", "invalid@govready.com", "invalid@govready.com")
        test("q_email_address.text", "invalid@govready.com", "invalid@govready.com")
        test("q_email_address", None, escape("<email-address>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_email_address.text", None, escape("<not answered>"))
        
        test("q_url", "https://www.govready.com?unit#test", "https://www.govready.com?unit#test")
        test("q_url.text", "https://www.govready.com?unit#test", "https://www.govready.com?unit#test")
        test("q_url", None, escape("<url>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_url.text", None, escape("<not answered>"))
        
        test("q_longtext", "This is a paragraph.\n\nThis is another paragraph.", "This is a paragraph.</p>\n<p>This is another paragraph.", 'This is a paragraph.\n\nThis is another paragraph.') # renders w/ Markdown, but impute condition gives it raw
        test("q_longtext.text", "This is a paragraph.\n\nThis is another paragraph.", "This is a paragraph.</p>\n<p>This is another paragraph.", 'This is a paragraph.\n\nThis is another paragraph.') # renders w/ Markdown, but impute condition gives it raw
        test("q_longtext", None, escape("<longtext>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_longtext.text", None, escape("<not answered>"))
        
        test("q_date", "2016-10-28", "2016-10-28")
        test("q_date.text", "2016-10-28", "10/28/2016")
        test("q_date", None, escape("<date>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_date.text", None, escape("<not answered>"))


    def test_render_choice_questions(self):
        def test(*args, **kwargs):
            self._test_render_single_question_md("question_types_choice", *args, **kwargs)

        from html import escape

        test("q_choice", "choice1", "choice1")
        test("q_choice.text", "choice1", "Choice 1")
        test("q_choice", None, escape("<choice>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_choice.text", None, escape("<not answered>"))

        test("q_yesno", "yes", "yes")
        test("q_yesno.text", "yes", "Yes")
        test("q_yesno", "no", "no")
        test("q_yesno.text", "no", "No")
        test("q_yesno", None, escape("<yesno>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_yesno.text", None, escape("<not answered>"))

        test("q_multiple_choice", [], "", []) # renders empty, but impute value is the list
        test("q_multiple_choice.text", [], escape("<nothing chosen>"))
        test("q_multiple_choice", ["choice1", "choice3"], "choice1, choice3", ["choice1", "choice3"]) # renders as a string, but imputes as a list
        test("q_multiple_choice.text", ["choice1", "choice3"], "Choice 1, Choice 3")
        test("q_multiple_choice", None, escape("<multiple-choice>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_multiple_choice.text", None, escape("<not answered>"))
        test("q_multiple_choice", ["choice1", "choice3"], "[choice1][choice3]",
            template="{% for choice in q_multiple_choice %}[{{choice}}]{% endfor %}")
        test("q_multiple_choice", None, "", # not answered appears as nothing selected
            template="{% for choice in q_multiple_choice %}[{{choice}}]{% endfor %}")

    def test_render_datagrid_questions(self):
        def test(*args, **kwargs):
            self._test_render_single_question_md("question_types_choice", *args, **kwargs)

        # TODO: Update tests for datagrid question
        # test("q_datagrid", [], "", []) # renders empty, but impute value is the list
        # test("q_datagrid.text", [], escape("<nothing chosen>"))
        # test("q_datagrid", ["field1", "field3"], "field1, field3", ["field1", "field3"]) # renders as a string, but imputes as a list
        # test("q_datagrid.text", ["field1", "field3"], "Field 1, Field 3")
        # test("q_datagrid", None, escape("<multiple-choice>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        # test("q_datagrid.text", None, escape("<not answered>"))
        # test("q_datagrid", ["field1", "field3"], "[field1][field3]",
        #     template="{% for field in q_datagrid %}[{{field}}]{% endfor %}")
        # test("q_datagrid", None, "", # not answered appears as nothing selected
        #     template="{% for field in q_datagrid %}[{{field}}]{% endfor %}")

    def test_render_numeric_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_numeric", *args)

        from html import escape

        test("q_integer", 0, "0")
        test("q_integer.text", 0, "0")
        test("q_integer", None, escape("<integer>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_integer.text", None, escape("<not answered>"))

        test("q_real", 0.5, "0.5")
        test("q_real.text", 0.5, "0.5")
        test("q_real", None, escape("<real>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_real.text", None, escape("<not answered>"))

    def test_render_media_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_media", *args)

        from html import escape

        # The "file" question type yields a dictionary with metadata about
        # the uploaded file -- it isn't normally rendered directly.
        file_metadata = {
            "url": "some-url-here",
            "size": 1024,
            "type": "text/plain",
            "type_display": "plain text",
        }
        test("q_file", file_metadata, '<a href="some-url-here">Download attachment (plain text; 1.0 kB; )</a>', file_metadata)
        test("q_file.url", file_metadata, "some-url-here")
        test("q_file.text", file_metadata, escape("<uploaded file: %s>" % file_metadata["url"]))
        test("q_file", None, escape("<file>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_file.text", None, escape("<not answered>"))

        # Interstitial questions never have value.
        test("q_interstitial", None, escape("<interstitial>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_interstitial.text", None, escape("<not answered>"))


    def test_render_module_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_module", *args)

        from html import escape

        # Create a sub-task that answers a question.
        m = Module.objects.get(module_name="simple") # the module ID that can answer the q_module question
        value = ModuleAnswers(
            m,
            Task.objects.create(module=m, editor=self.user, project=self.project),
            {
                "_introduction": (m.questions.get(key="_introduction"), True, None, None), # must be answered for q1 to have a value
                "q1": (m.questions.get(key="q1"), True, None, "My Answer"),
            })

        # When substituting the variable plainly ("{{q_module}}") it substitutes
        # with the title of the sub-task. This sub-module has an instance-name
        # field that overrides the default title with a rendered template "{{q1}}",
        # but the sub-task doesn't have any answers because we faked it above,
        # so substituton of q1 fails, and the instance-name is ignored. The
        # sub-task title is then the module title.
        # Note that in an impute condition w/ value-mode
        # "expression", we get back the ModuleAnswers instance.
        test("q_module", value, escape("A Simple Module"), value)

        test("q_module.q1", value, "My Answer")
        test("q_module.q1.text", value, "My Answer")
        test("q_module", None, escape("<module>"), None) # renders as the title of the question q_module, but in an impute condition value gives None
        test("q_module.q1", None, escape("<The Question>"), None) # the title of q1, but in an impute condition value None
        test("q_module.q1.text", None, escape("<not answered>"))

        # TODO: Test module-set questions.

    def test_render_global_context_variables(self):
        # test that the organization and project render as their names

        # Create a Task instance to include in the render context so
        # that it is tied to a project and organization.
        module = Module.objects.get(module_name="simple")
        task = Task.objects.create(module=module, project=self.project, editor=self.user)
        answers = ModuleAnswers(module, task, {})

        def test(expression, expected):
            self._test_render_single_question_md(
                "simple",
                expression,
                None,
                expected,
                answers=answers
                )

        test("organization", "My Supreme Organization")
        test("project", "I want to answer some questions on Q.")

        # Test that setting an overridden root_task title causes the
        # project variable to render with that value.
        self.project.root_task.title_override = "The Singleton Project"
        self.project.root_task.save()
        test("project", "The Singleton Project")

    def _test_render_single_question_md(self, module, expression, value, expected, expected_impute_value="__NOT__PROVIDED__", answers=None, template=None):
        # Render the "{{question}}" or "{{question.text}}" using the given module.

        # create a ModuleAnswers instance that provides context for evaluating the template
        if answers is None:
            m = self.getModule(module)
            key = expression.split(".")[0]
            answers = ModuleAnswers(m, None, {
                key: (m.questions.get(key=key), True, None, value) # if expression looks like "id.text" just use "id" here to set the answer
            })

        # render the template. Wrap `expression` in "{{...}}" if template isn't provided.
        actual = render_content(
            {
                "format": "markdown",
                "template": template or ("{{%s}}" % expression),
            },
            answers,
            "html",
            str(self), # source
        ).strip()

        # unwrap the <p> tags for simplicity, so the caller doesn't have to supply it
        import re
        strip_p_tags = re.compile("^<p>(.*)</p>$", re.S)
        m = strip_p_tags.match(actual)
        if m:
            actual = m.group(1).strip()

        # test that the output matches what the caller gave
        self.assertEqual(actual, expected)

        # test that including answer metadata doesn't break. just executed it. if
        # it doesn't crash, good.
        render_content(
            {
                "format": "markdown",
                "template": template or ("{{%s}}" % expression),
            },
            answers,
            "html",
            str(self), # source
            show_answer_metadata=True,
        )

        # Test that we get the same thing if we use an impute condition with `value-mode: expression`
        # or, if template is provided, `value-mode: template`. For `value-mode: expression`, convert
        # the imputed value to a string since the test is only given its string form.
        def escapefunc(question, task, is_answered, answerobj, value):
            # ignores longtext rendering
            return value
        context = TemplateContext(answers, escapefunc) # parallels evaluate_module_state
        if not template:
            impute_condition = { "value": expression, "value-mode": "expression" }
        else:
            impute_condition = { "value": template, "value-mode": "template" }
        actual = run_impute_conditions([impute_condition], context)
        self.assertIsNotNone(actual, msg="'1' impute condition failed")
        actual = actual[0] # unwrap
        if expected_impute_value == "__NOT__PROVIDED__":
            # when comparing with render output stringify and escape
            # the imputed value
            import html
            actual = html.escape(str(actual))
            expected_impute_value = expected
        self.assertEqual(actual, expected_impute_value, msg="impute value expression %s" % expression)

class ImportExportTests(TestCaseWithFixtureData):
    ## IMPORT/EXPORT TASK DATA TESTS ##

    class DummySerializer:
        def __init__(self, include_metadata=True):
            self.include_metadata = include_metadata
            self.include_file_content = True
        def serializeOnce(self, object, preferred_key, value_func):
            return value_func()

    class DummyDeserializer:
        def __init__(self, user, included_metadata):
            self.user = user
            self.log_capture = []
            self.included_metadata = included_metadata
            self.answer_method = "web"
            def logger(message):
                self.log_capture.append(message)
            self.log = logger

    def test_round_trip(self):
        # The normal question types all have the same import/export semantics but
        # validation requires that we give it sane values.
        tests = {
            "question_types_text": {
                "text": ["Hello!"],
                "password": ["1234"],
                "email-address": ["unit+test@govready.com"],
                "url": ["https://www.govready.com"],
                "longtext": ["Paragraphs are\n\nin need of testing."],
                "date": ["2016-11-03"],
            },
            "question_types_choice": {
                "choice": ["choice1"],
                "yesno": ["yes", "no"],
                "multiple-choice": [[], ["choice1"], ["choice1", "choice2"]],
            },
            "question_types_numeric": {
                "integer": [0, 1, -1],
                "real": [0.0, 1.5, -2.1],
            },
            "question_types_media": {
                "interstitial": [None],
            },
        }

        for module_name, tests in tests.items():
            for qtype, test_values in tests.items():
                for test_value in [None] + test_values:
                    for include_metadata in (True, False):
                        self._test_round_trip(module_name, "q_" + qtype.replace("-", "_"), include_metadata, qtype, test_value)

        # TODO: file, module, module-set

    def _test_round_trip(self, module_name, question_name, include_metadata, question_type, answer_value):
        # Create an empty Task.
        m = self.getModule(module_name)
        task = Task.objects.create(module=m, editor=self.user, project=self.project)

        # Import some data to set answers.
        if include_metadata:
            task_dict = {
                "answers": {
                    question_name: {
                        "questionType": question_type,
                        "value": answer_value,
                    }
                }
            }
        else:
            task_dict = {
                question_name: answer_value
            }
        deserializer = ImportExportTests.DummyDeserializer(self.user, include_metadata)
        task.import_json_update(task_dict, deserializer)

        # Check that the log of what occurred during import matches expectations.
        self.assertEqual(deserializer.log_capture, [
            "'{}' was updated.".format(m.questions.get(key=question_name).spec['title'])
        ])

        # Export it and check that the exported JSON matches the JSON that we imported.
        # In other words, it should round-trip. Only check that the keys in the test JSON
        # are present and have the correct values in the exported JSON. The exported JSON
        # may have other keys that we don't care about. Check recursively.
        export = task.export_json(ImportExportTests.DummySerializer(include_metadata))
        def check_dict(a, b, path):
            for k, v in a.items():
                if isinstance(v, dict):
                    # Check dicts recursively.
                    self.assertIsInstance(b.get(k), dict, "->".join(path+[k]))
                    check_dict(v, b[k], path+[k])
                else:
                    # Check other value types for equality.
                    self.assertEqual(b.get(k), v, "->".join(path+[k]))
        check_dict(task_dict, export, [module_name, question_name])

class ComplianceAppTests(TestCaseWithFixtureData):
    ## COMPLIANCE APP VISIBILITY DATA TESTS ##

    def add_perm_fetch(self):
        """
        Adds the view appsource permission to the given user and fetches the updated user
        """

        # add the view_appsource permission and test again
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.user = User.objects.get(pk=self.user.pk)


    def app_filter(self, role_bool):

        app_filter = AppVersion.objects \
            .filter(show_in_catalog=True) \
            .filter(source__is_system_source=self.fixture_app.source.is_system_source) \
            .filter(Q(source__available_to_role=role_bool)) \
            .filter(Q(source__available_to_all_individuals=self.fixture_app.source.available_to_all_individuals) | Q(source__available_to_individual=self.user)) \
            .filter(Q(source__available_to_all=self.fixture_app.source.available_to_all) | Q(source__available_to_orgs=self.organization))
        return app_filter

    def role_bool(self):
        """
        Returns a boolean if the given
        """
        role_bool = self.user.has_perm("guidedmodules.view_appsource")
        return role_bool

    def test_available_to_individuals(self):
        """
        Testing the limitation of compliance app view by individual
        """

        # Regular user does not have permission
        self.assertIsNone(ComplianceAppTests.app_filter(self, self.role_bool()).first())

        # Compliance app view only available to certain individuals
        self.fixture_app.source.available_to_individual.add()

        # Given permission to this individual user
        self.add_perm_fetch()
        # Should return
        self.assertIsNotNone(ComplianceAppTests.app_filter(self, self.role_bool()).first())

    def test_available_to_roles(self):
        """
        Users without viewing permission should not be able to request compliance apps
        """

        # In this scenario a regular user will not have permission to view compliance apps
        self.user.user_permissions.remove(Permission.objects.get(codename='view_appsource'))

        # User won't have viewing permission
        self.assertFalse(self.user.has_perm("guidedmodules.view_appsource"))

        self.add_perm_fetch()

        self.assertIsNotNone(ComplianceAppTests.app_filter(self, self.role_bool()).first())
        
    def test_available_to_organizations(self):
        """
        Testing the limitation of compliance app view by organization
        """

        # Regular user does not have permission
        self.assertIsNone(ComplianceAppTests.app_filter(self, self.role_bool()).first())

        # Compliance app view only available to a certain organizations
        self.fixture_app.source.available_to_orgs.add(self.organization)

        # Given permission to this individual user
        self.add_perm_fetch()
        # Should return
        self.assertIsNotNone(ComplianceAppTests.app_filter(self, self.role_bool()).first())
