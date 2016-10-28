from django.test import TestCase
from django.conf import settings

from siteapp.models import Organization, Project, User
from .models import Module, Task
from .module_logic import *

class TestCaseWithFixtureData(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # Load modules from the fixtures directory.
        settings.MODULES_PATH = 'fixtures/modules'
        from guidedmodules.management.commands.load_modules import Command as load_modules
        load_modules().handle()

        # Create a dummy organization, project, and user.
        self.organization = Organization.objects.create(name="Organization")
        self.project = Project.objects.create(title="Project", organization=self.organization)
        self.user = User.objects.create(username="unit.test")


class ImputeConditionTests(TestCaseWithFixtureData):
    # Tests that expressions have the expected value in impute conditions
    # and that they have the *same* truthy-ness when used in {% if ... %}
    # blocks in templates.

    def _helper(self, module, answers, condition, expected):
        m = Module.objects.get(key=module)
        answers = ModuleAnswers(m, None, answers)

        # Test that the impute condition works correctly.
        # Run the impute condition and test whether or not
        # it matched. Don't look at it's value -- the value
        # is always (True,) (a tuple containing True).
        context = TemplateContext(answers, str) # parallels ModuleAnswers.add_imputed_answers
        actual = run_impute_conditions([{ "condition": condition, "value": True }], context)
        self.assertEqual(actual is not None, expected)

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
        self.assertEqual(if_block, expected)

    def _helper2(self, module, question, value, condition, expected):
        return self._helper(module, { question: value }, condition, expected)

    def test_impute_using_text_questions(self):
        test = lambda *args : self._helper2("question_types_text", *args)

        test("q_text", "Hello!", "q_text", True) # answered is truthy
        test("q_text", "Hello!", "q_text=='Hello!'", True)
        test("q_text", "Hello!", "q_text!='Hello!'", False)
        test("q_text", None, "q_text", False) # skipped is falsey

        # password, email, url, and longtext should have the same behavior as above.
        # so does date, but there are other things to check
        
        #test("q_date", "2016-10-28", "q_text < '2017-01-01'", True)

    def test_impute_using_choice_questions(self):
        test = lambda *args : self._helper2("question_types_choice", *args)

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
        test = lambda *args : self._helper2("question_types_numeric", *args)

        test("q_integer", 0, "q_integer", True) # answered is truthy, even if answer would be falsey in Python
        test("q_integer", 0, "q_integer == 0", True)
        #test("q_integer", 1, "q_integer > 0", True)
        test("q_integer", None, "q_integer", False) # skipped is falsey

        test("q_real", 0.0, "q_real", True) # answered is truthy, even if answer would be falsey in Python
        test("q_real", 0.0, "q_real == 0", True)
        #test("q_real", 1.0, "q_real > 0", True)
        test("q_real", None, "q_real", False) # skipped is falsey

    def test_impute_using_media_questions(self):
        test = lambda *args : self._helper2("question_types_media", *args)

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
        test = lambda *args : self._helper2("question_types_module", *args)

        # Create a sub-task that answers a question.
        m = Module.objects.get(key="simple") # the module ID that can answer the q_module question
        value = ModuleAnswers(
            m,
            Task.objects.create(module=m, title="My Task", editor=self.user, project=self.project),
            {
                "q1": "My Answer",
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
        self.assertEqual(
            self.render_content(
                "question_types_text",
                "markdown", "*Hello*",
                { }, "html"),
            "<p><em>Hello</em></p>")

    def render_content(self, module, template_format, template, answers, output_format):
        m = Module.objects.get(key=module)
        return render_content(
            {
                "format": template_format,
                "template": template,
            },
            ModuleAnswers(m, None, answers),
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
        test("q_text", None, escape("<text>")) # is actually the question's title, not its type
        test("q_text.text", None, escape("<not answered>"))

        test("q_password", "1234", "1234")
        test("q_password.text", "1234", "1234")
        test("q_password", None, escape("<password>")) # is actually the question's title, not its type
        test("q_password.text", None, escape("<not answered>"))
        
        test("q_email_address", "invalid@govready.com", "invalid@govready.com")
        test("q_email_address.text", "invalid@govready.com", "invalid@govready.com")
        test("q_email_address", None, escape("<email-address>")) # is actually the question's title, not its type
        test("q_email_address.text", None, escape("<not answered>"))
        
        test("q_url", "https://www.govready.com?unit#test", "https://www.govready.com?unit#test")
        test("q_url.text", "https://www.govready.com?unit#test", "https://www.govready.com?unit#test")
        test("q_url", None, escape("<url>")) # is actually the question's title, not its type
        test("q_url.text", None, escape("<not answered>"))
        
        test("q_longtext", "This is a paragraph.\n\nThis is another paragraph.", "<p>This is a paragraph.</p>\n<p>This is another paragraph.</p>")
        test("q_longtext.text", "This is a paragraph.\n\nThis is another paragraph.", "<p>This is a paragraph.</p>\n<p>This is another paragraph.</p>")
        test("q_longtext", None, escape("<longtext>")) # is actually the question's title, not its type
        test("q_longtext.text", None, escape("<not answered>"))
        
        test("q_date", "2016-10-28", "2016-10-28")
        test("q_date.text", "2016-10-28", "10/28/2016")
        test("q_date", None, escape("<date>")) # is actually the question's title, not its type
        test("q_date.text", None, escape("<not answered>"))


    def test_render_choice_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_choice", *args)

        from html import escape

        test("q_choice", "choice1", "choice1")
        test("q_choice.text", "choice1", "Choice 1")
        test("q_choice", None, escape("<choice>")) # is actually the question's title, not its type
        test("q_choice.text", None, escape("<not answered>"))

        test("q_yesno", "yes", "yes")
        test("q_yesno.text", "yes", "Yes")
        test("q_yesno", "no", "no")
        test("q_yesno.text", "no", "No")
        test("q_yesno", None, escape("<yesno>")) # is actually the question's title, not its type
        test("q_yesno.text", None, escape("<not answered>"))

        test("q_multiple_choice", [], "")
        test("q_multiple_choice.text", [], escape("<nothing chosen>"))
        test("q_multiple_choice", ["choice1", "choice3"], "choice1, choice3")
        test("q_multiple_choice.text", ["choice1", "choice3"], "Choice 1, Choice 3")
        test("q_multiple_choice", None, escape("<multiple-choice>")) # is actually the question's title, not its type
        test("q_multiple_choice.text", None, escape("<not answered>"))

    def test_render_numeric_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_numeric", *args)

        from html import escape

        test("q_integer", 0, "0")
        test("q_integer.text", 0, "0")
        test("q_integer", None, escape("<integer>")) # is actually the question's title, not its type
        test("q_integer.text", None, escape("<not answered>"))

        test("q_real", 0.5, "0.5")
        test("q_real.text", 0.5, "0.5")
        test("q_real", None, escape("<real>")) # is actually the question's title, not its type
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
        test("q_file.url", file_metadata, "some-url-here")
        test("q_file", None, escape("<file>")) # is actually the question's title, not its type
        test("q_file.text", None, escape("<not answered>"))

        # Interstitial questions never have value.
        test("q_interstitial", None, escape("<interstitial>")) # is actually the question's title, not its type
        test("q_interstitial.text", None, escape("<not answered>"))

        # We're not calling the external function here - just rendering it
        # given some return value. It's not really intended to be rendered
        # since its value can be any Python data structure.
        test("q_external_function", "VALUE", "VALUE")
        test("q_external_function.text", "VALUE", "VALUE")
        test("q_external_function", None, escape("<external-function>")) # is actually the question's title, not its type
        test("q_external_function.text", None, escape("<not answered>"))

    def test_render_module_questions(self):
        def test(*args):
            self._test_render_single_question_md("question_types_module", *args)

        from html import escape

        # Create a sub-task that answers a question.
        m = Module.objects.get(key="simple") # the module ID that can answer the q_module question
        value = ModuleAnswers(
            m,
            Task.objects.create(module=m, title="My Task", editor=self.user, project=self.project),
            {
                "q1": "My Answer",
            })

        # When substituting the module plainly ("{{q_module}}") it substitutes
        # with the title of the sub-task, but because this sub-module has an
        # instance-name attribute and that attribute says to give the value
        # of "{{q1}}", but the Task object itself doesn't have any answers
        # because we faked it above, we get back the same as "{{q_module.q1}}",
        # which is the title of q1.
        test("q_module", value, escape("<The Question>"))

        test("q_module.q1", value, "My Answer")
        test("q_module.q1.text", value, "My Answer")
        test("q_module", None, escape("<module>")) # the title of the question q_module
        test("q_module.q1", None, escape("<The Question>")) # the title of q1
        test("q_module.q1.text", None, escape("<not answered>"))

        # TODO: Test module-set questions.

    def _test_render_single_question_md(self, module, question, value, expected_output):
        # Render the "{{question}}" or "{{question.text}}" using the given module.
        actual = self.render_content(
            module,
            "markdown", "{{%s}}" % question,
            {
                question.split(".")[0]: value # if question looks like "id.text" just use "id" here
            },
            "html")

        # unwrap the <p> tags for simplicity, so the caller doesn't have to supply it
        import re
        strip_p_tags = re.compile("^<p>(.*)</p>$", re.S)
        self.assertRegex(actual, strip_p_tags)
        actual = strip_p_tags.match(actual).group(1).strip()

        # test that the output matches what the caller gave
        self.assertEqual(actual, expected_output)
