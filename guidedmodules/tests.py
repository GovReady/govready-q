from django.test import TestCase
from django.conf import settings

from siteapp.models import Organization, Project, User
from .models import Module, Task, TaskAnswer
from .module_logic import *

class TestCaseWithFixtureData(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # Load modules from the fixtures directory.
        from guidedmodules.models import ModuleSource
        from guidedmodules.management.commands.load_modules import Command as load_modules
        from guidedmodules.module_sources import MultiplexedAppStore, AppImportUpdateMode
        ModuleSource.objects.create(
            namespace="fixture",
            spec={
                "type": "local",
                "path": "fixtures/modules/other",
            }
        )
        with MultiplexedAppStore(ms for ms in ModuleSource.objects.all()) as store:
            for app in store.list_apps():
                app.import_into_database(AppImportUpdateMode.ForceUpdateInPlace)


        # Create a dummy organization, project, and user.
        self.organization = Organization.objects.create(name="Organization")
        self.project = Project.objects.create(title="Project", organization=self.organization)
        self.user = User.objects.create(username="unit.test")


class ImputeConditionTests(TestCaseWithFixtureData):
    # Tests that expressions have the expected value in impute conditions
    # and that they have the *same* truthy-ness when used in {% if ... %}
    # blocks in templates.

    def _test_condition_helper(self, module, context_key, context_value, condition, expected):
        m = Module.objects.get(key="fixture/simple_project/" + module)
        answers = ModuleAnswers(m, None, { context_key: (m.questions.get(key=context_key), True, None, context_value) })

        # Test that the impute condition works correctly.
        # Run the impute condition and test whether or not
        # it matched. Don't look at it's value -- the value
        # is always (True,) (a tuple containing True).
        context = TemplateContext(answers, lambda v, mode : str(v)) # parallels evaluate_module_state
        actual = run_impute_conditions([{ "condition": condition, "value": True }], context)
        self.assertEqual(actual is not None, expected, msg="impute condition: %s" % condition)

        # Test that an {% if ... %} block has the same truth value when
        # used in a template.
        if_block = render_content(
            {
                "format": "text",
                "template": r"{% if " + condition + r" %}TRUE{% else %}FALSE{% endif %}",
            },
            answers,
            "text",
            str(self), # source
        ) == "TRUE"
        self.assertEqual(if_block, expected, msg="{%% if %s %%}" % condition)

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

        # We're not calling the external function here - just using it
        # given some return value.
        test("q_external_function", False, "q_external_function", True) # answered is truthy, even if False
        test("q_external_function", "VALUE", "q_external_function", True) # should be Pythonic truthy
        test("q_external_function", None, "q_external_function", False) # but skipped/None are falsey

    def test_impute_using_module_questions(self):
        test = lambda *args : self._test_condition_helper("question_types_module", *args)

        # Create a sub-task that answers a question.
        m = Module.objects.get(key="fixture/simple_project/simple") # the module ID that can answer the q_module question
        value = ModuleAnswers(
            m,
            Task.objects.create(module=m, title="My Task", editor=self.user, project=self.project),
            {
                "_introduction": (m.questions.get(key="_introduction"), True, None, None), # must be answered for q1 to have a value
                "q1": (m.questions.get(key="q1"), True, None, "My Answer"),
            })

        test("q_module", value, "q_module", True) # answered is truthy
        test("q_module", value, "q_module.q1", True) # sub-answer test
        test("q_module", None, "q_module", False) # skipped is falsey
        test("q_module", None, "q_module.q1", False) # skipped is falsey for all sub-answers

        # TODO: Test module-set questions.


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
            """<p><img alt="" src="/user-mediaguidedmodules/module-assets/642396ce610f24a112d3feda9833dfddddd9fff7.png"></p>""")

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
                "q_longtext": '''<a href="" onclick="alert('uh-oh')">click me</a>''',
            },
            '<p><!-- raw HTML omitted -->click me<!-- raw HTML omitted --></p>')

    def render_content(self, module, template_format, template, answers, output_format):
        m = Module.objects.get(key="fixture/simple_project/" + module)
        return render_content(
            {
                "format": template_format,
                "template": template,
            },
            ModuleAnswers(m, None, { k: (m.questions.get(key=k), True, None, v) for k, v in answers.items() }),
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
        def test(*args):
            self._test_render_single_question_md("question_types_choice", *args)

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
        }
        test("q_file", file_metadata, escape("<uploaded file: %s>" % file_metadata["url"]), file_metadata) # renders as <uploaded file: ...> but impute value gives it back raw
        test("q_file.url", file_metadata, "some-url-here")
        test("q_file.text", file_metadata, escape("<uploaded file: %s>" % file_metadata["url"]))
        test("q_file", None, escape("<file>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_file.text", None, escape("<not answered>"))

        # Interstitial questions never have value.
        test("q_interstitial", None, escape("<interstitial>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_interstitial.text", None, escape("<not answered>"))

        # We're not calling the external function here - just rendering it
        # given some return value. It's not really intended to be rendered
        # since its value can be any Python data structure.
        test("q_external_function", "VALUE", "VALUE")
        test("q_external_function.text", "VALUE", "VALUE")
        test("q_external_function", None, escape("<external-function>"), None) # is actually the question's title, not its type, and {{...}} differently than in an impute condition
        test("q_external_function.text", None, escape("<not answered>"))

    def test_render_module_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_module", *args)

        from html import escape

        # Create a sub-task that answers a question.
        m = Module.objects.get(key="fixture/simple_project/simple") # the module ID that can answer the q_module question
        value = ModuleAnswers(
            m,
            Task.objects.create(module=m, title="My Task", editor=self.user, project=self.project),
            {
                "_introduction": (m.questions.get(key="_introduction"), True, None, None), # must be answered for q1 to have a value
                "q1": (m.questions.get(key="q1"), True, None, "My Answer"),
            })


        test("q_module", value, escape("A Simple Module"), value)
        test("q_module.q1", value, "My Answer")
        test("q_module.q1.text", value, "My Answer")
        test("q_module", None, escape("<module>"), None) # renders as the title of the question q_module, but in an impute condition value gives None
        test("q_module.q1", None, escape("<The Question>"), None) # the title of q1, but in an impute condition value None
        test("q_module.q1.text", None, escape("<not answered>"))

        # TODO: Test module-set questions.

    def _test_render_single_question_md(self, module, expression, value, expected, expected_impute_value="__NOT__PROVIDED__"):
        # Render the "{{question}}" or "{{question.text}}" using the given module.
        m = Module.objects.get(key="fixture/simple_project/" + module)
        key = expression.split(".")[0]
        answers = ModuleAnswers(m, None, {
            key: (m.questions.get(key=key), True, None, value) # if expression looks like "id.text" just use "id" here to set the answer
        })
        actual = render_content(
            {
                "format": "markdown",
                "template": "{{%s}}" % expression,
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

        # test that we get the same thing if we use an impute condition with value-mode: expression,
        # but since the test is only given its string output convert the impute condition value
        # to a string
        context = TemplateContext(answers, lambda v, mode : str(v)) # parallels evaluate_module_state
        actual = run_impute_conditions([{ "condition": "1", "value": expression, "value-mode": "expression" }], context)
        self.assertIsNotNone(actual, msg="'1' impute condition failed")
        actual = actual[0] # unwrap
        if expected_impute_value == "__NOT__PROVIDED__":
            # when comparing with render output stringify and escape
            # the imputed value
            import html
            actual = html.escape(str(actual))
            expected_impute_value = expected
        self.assertEqual(actual, expected_impute_value, msg="impute value expression %s" % expression)


class EncryptionTests(TestCaseWithFixtureData):
    def test_encryption(self):
        # Create an empty Task.
        m = Module.objects.get(key="fixture/simple_project/question_types_encrypted")
        task = Task.objects.create(module=m, title="Test Task", editor=self.user, project=self.project)
        answer, _ = TaskAnswer.objects.get_or_create(
            task=task,
            question=m.questions.get(key="q_text"),
        )

        # What value should we put in the database?
        value = "This is a value!!!"

        # Create an EncryptionProvider to manage keys.
        class EncryptionProvider:
            def __init__(self):
                self.keys = { }
            def set_new_ephemeral_user_key(self, key):
                key_id = len(self.keys)
                self.keys[key_id] = key
                return (key_id, 60) # 60 is the lifetime in seconds, not used for anything currently
            def get_ephemeral_user_key(self, key_id):
                return self.keys.get(key_id)
        encryptionProvider = EncryptionProvider()

        # Save answer to database.
        self.assertTrue(answer.save_answer(value, [], None,
            self.user, "web", encryption_provider=encryptionProvider))

        # Check that we got a key of 44 characters.
        self.assertEqual(len(encryptionProvider.keys), 1)
        self.assertEqual(len(encryptionProvider.keys[0]), 44)

        # Check that the answer is actually encrypted.
        answer = answer.get_current_answer()
        self.assertIsNone(answer.get_value()) # without EncryptionProvider, it comes back None
        self.assertEqual( # with EncryptionProvider we can see the value
            answer.get_value(decryption_provider=encryptionProvider),
            value)
        self.assertIsNone(answer.get_value(decryption_provider=EncryptionProvider())) # fresh provider without the key, is None again


class ImportExportTests(TestCaseWithFixtureData):
    ## IMPORT/EXPORT TASK DATA TESTS ##

    class DummySerializer:
        def __init__(self, include_metadata):
            self.include_metadata = include_metadata
        def serializeOnce(self, object, preferred_key, value_func):
            return value_func()

    class DummyDeserializer:
        def __init__(self, user, included_metadata):
            self.user = user
            self.log_capture = []
            self.included_metadata = included_metadata
            self.answer_method = "web"
            def logger(message):
                print(message)
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
                "external-function": [{ "arbitrary": ["data"] }],
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
        m = Module.objects.get(key="fixture/simple_project/" + module_name)
        task = Task.objects.create(module=m, title="My Task", editor=self.user, project=self.project)

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
        task.import_json_update(task_dict, ImportExportTests.DummyDeserializer(self.user, include_metadata))

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