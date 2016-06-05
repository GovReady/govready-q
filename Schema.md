Schema for Modules and Questions
================================

A module and its questions are defined in YAML specification files. The schema for the specification files is as follows:

Module
------

Each file is a Module. A Module has the following required fields:

	id: module_id
	title: Your Title Here

The `module_id` must match the file name that the YAML is saved into, without the file extension.

Several optional fields can be specified:

	version: 1
	instance-name: "Module for {{q1}}"

The `version` field is used only to force changes in the specification to be considered incompatible with any existing user answers (see Updating Modules).

The `instance-name` is a template to generate a dynamic title for in-progress and completed modules. The `instance-name` is rendered like other Module documents but it is always specified in `text` format (see Documents).

In addition, a Module must have an `introduction` document and a list of one or more `output` documents. For example:

	introduction:
	  format: markdown
	  template: |
	    Welcome to the module.

	    This module should take you two minutes.

	output:
	  - name: Document 1
	    format: markdown
	    template: |
	      # Document for {{project}}

	      Hello! This is the output of the module. You answered {{q1}}.

	  - name: Document 2
	    format: html
	    template: |
	      <h1># Document for {{project}}</h1>

	      <p>Hello! This is the output of the module. You answered {{q1}}.</p>

The format of documents are described in a later section.

Finally, a Module contains a list of one or more Questions:

	questions:
	  - id: q1
	    title: Your Favorite Animal
	    prompt: What's your favorite animal?
	    type: text

	  - id: q2
	    title: What Kind of Animal Is It
	    prompt: How would you classify this animal?
	    type: choice
	    choices:
	      - key: pet
	        text: common pet
	        help: Is this animal a common pet?
	      - key: wild
	        text: wild animal
	        help: Is this animal an undomesticated wild animal?

The schema for questions is documented in a later section.

Documents
---------

Documents occur as `introduction` and `output` documents of Modules as well as Question prompts.

The `introduction` and `output` documents of Modules allow a format to be specified. The document formats are:

* `markdown` --- The document is entered in [CommonMark](http://commonmark.org/) ([quick guide](http://commonmark.org/help/)) in the specification file, but it will be rendered into a richly formatted presentation on screen.
* `html` --- The document is given in raw HTML, but it will be rendered on screen.
* `text` --- The document is given in plain text, and it will display as preformatted (fixed-width) text on screen.
* `json`, `yaml` --- Experimental.

All document formats are evaluated as [Jinja2 templates](http://jinja.pocoo.org/docs/dev/templates/). That means within your document you can embed special tags that are replaced prior to the document being displayed to the user:

* `{{ question_id }}` will be replaced with the user's answer to the question whose `id` is `question_id`. For choice-type questions, the value is replaced by the choice `key`. Use `{{ question_id.text }}` to get display text. See the question types documentation below for details.
* `{% if question_id == 'value' %}....{% endif %}` is a conditional block. The contents inside the block (`....`) will be included in the output if the condition is true. In this example, the contents inside the block will be included in the output if the user's answer to `question_id` is `value`.

Output documents and question prompts have access to the user's answers to questions in question variables. The introduction document does not because questions have not yet been answered.

All documents also have access to the project title as `{{project}}`.

Questions
---------

Questions have the following required fields:

	  - id: q1
	    title: Your Favorite Animal
	    prompt: What's your favorite animal?
	    type: text

The question `id` is used to refer to this Question in other questions and in the output documents.

The `title` is used to describe the Question in places where a long-form prompt would not be appropriate.

The `prompt` is the text the user is prompted with when presented with the question. The prompt is rendered like other Module documents but it is always specified in `markdown` format (see Documents).

Removing a question, changing a question type, and other changes as noted below are incompatible changes (see Updating Modules).

### Question Types

#### `text`

This type asks the user for a single line of free-form text. The text cannot be empty.

A `placeholder` can be specified which provides "placeholder" text displayed inside the form field when the user has not yet entered anything.

`help` text can be specified which provides an additional prompt smaller and below the field input.

Example:

	  - id: q1
	    title: Your Favorite Animal
	    prompt: What's your favorite animal?
	    type: text
	    placeholder: enter a type of animal
	    help: Examples: dog, cat, turtle, lion

In document templates and impute conditions, the value of `text` questions is simply the text the user entered.

#### `password`

This type asks the user for a password. It is the same as the `text` question type, except that a password input field is used to mask the input. `placeholder` and `help` can be specified.

#### `email-address`

This type asks the user for an email address. It is the same as the `text` question type, except that the value entered must be a valid email address. `placeholder` and `help` can be specified.

#### `url`

This type asks the user for a web address (a URL). It is the same as the `text` question type, except that the value entered must be a valid web address. `placeholder` and `help` can be specified. The web address is not checked for existence --- only the form (syntax) of the address is checked.

#### `longtext`

This type asks the user for free-form text using a large text input area that allows for multiple lines of text. The text cannot be empty.

`help` text can be specified which provides an additional prompt smaller and below the field input.

In document templates and impute conditions, the value of `longtext` questions is simply the text the user entered.

#### `choice`

This type asks the user to choose one of several options. The options are given as:

	    choices:
	      - key: pet
	        text: common pet
	        help: Is this animal a common pet?
	      - key: wild
	        text: wild animal
	        help: Is this animal an undomesticated wild animal?

The user must select exactly one choice.

The `help` text is optional. It is displayed smaller and below each choice. (Unlike some other question types, there is no `help` field on the question as a whole.)

In document templates and impute conditions, the value of `choice` questions is the `key` of the choice selected by the user. Use `questionid.text` to access the display text for the choice.

Removing a choice is an incompatible change (see Updating Modules).

#### `yesno`

This type is the same as `choice` but with built-in choices for yes and no. It is the same as a `choice` question type with these choices:

	    choices:
	      - key: yes
	        text: Yes
	      - key: no
	        text: No

The user _must_ choose either yes or no.

#### `multiple-choice`

The `multiple-choice` question type is similar to the `choice` question type except that:

* The user can select multiple choices.
* In document templates and impute conditions, the value of `multiple-choice` questions is a list of the `key`s of the choices selected by the user. When used bare, this renders as a comma-separated list of keys. One can use the [`|length` filter](http://jinja.pocoo.org/docs/dev/templates/#length) and `{% for ... in ... %}... {% endfor %}` loops to access the individual choices the user selected. Use `questionid.text` to render a comma-separated list of the display text of the selected choices.
* `min` and `max` may be specified. If `min` is specified, it must be greater than or equal to zero and requires that the user choose at least that many choices. If `max` is specified, it must be greater than or equal to one (and if `min` is specified, it must be at least `min`) and requires that the user choose at most that number of choices.

Increasing the `min` or decreasing the `max` are incompatible changes (see Updating Modules).

#### `integer`

This question type asks for a numeric, integer input.

If `min` and `max` are set, then the value is restricted to that range. If `min` is omitted, then negative numbers are allowed!

As with the text question types, `placeholder` and `help` text can also be specified.

In document templates and impute conditions, the value of `integer` questions is the numeric value entered by the user.

#### `real`

This question type asks for a numeric input, allowing for real (floating-point) numbers.

If `min` and `max` are set, then the value is restricted to that range. If `min` is omitted, then negative numbers are allowed!

As with the text question types, `placeholder` and `help` text can also be specified and in document templates and impute conditions the value of these questions is the numeric value entered by the user.
.

#### `module`, `module-set`

These question type prompt the user to select another completed module as the answer to the question. The `module-id` field specifies the ID of another module specification. The `module` question type allows for a single other module to answer the question. The `module-set` question type allows for zero or more other modules to answer the question.

Changing the `module-id` is considered an incompatible change (see Updating Modules), and if the referenced Module's specification is changed on disk in an incompatible way with existing user answers, the Module in which the question occurs is also considered to have an incompatible change. Thus an incompatible change in a module triggers an incompatible change in any other Module that refers to it (and so on recursively).

In document templates and impute conditions, the value of `module` questions is a dictionary of the answers to that module. For example, if `q5` is the ID of a question whose type is `module`, then `{{q5.q1}}` will provide the answer to `q1` within the module the user selected that answers `q5`.

### Imputing Answers

The answer to one question may provide the answer to another. In such cases, the latter question is said to have an imputed value and the user is not asked to answer the question. To imput a value, specify on the question whose value is being imputed:

    impute:
      - condition: q1 == 'no'
        value: don't know

This example says that if the answer to `q1` is `no`, then the answer to this question is `don't know`.

The `condition` is a [Jinja2 expression](http://jinja.pocoo.org/docs/dev/templates/#expressions). Any question can be referred to in the expression (by its `id`). Questions are tested on their internal values. For `choice` and `multiple-choice` questions, their values are their `key`s, not their label text, and `multiple-choice` questions are _lists_ of keys.

The `value` provided must be a valid value for the question type it is a part of. For `choice` questions, the value must be a choice `key`, not the label text. For `multiple-choice` questions, the value must be a _list_ of keys.

Multiple condition/value blocks can be provided. They are evaluated in order, with the first matching condition taking precedence.

    impute:
      - condition: q1 == 'no'
        value: I don't know.
      - condition: q1 == 'yes'
        value: I do know.


Question Order
--------------

The order in which Questions are asked is determined through an algorithm. The algorithm determines which questions need to be asked before other questions and which need to be asked in order to generate the output documents.

The only Questions that are asked of the user are those that are mentioned in any of the output templates or other Questions that required to be asked before those mentioned Questions can be answered.

If a Question mentions another question in its prompt text or impute conditions, the other question must be answered first. A Question can also list other Questions that should be answered first as:

	ask-first:
	 - q1
	 - q2

Updating Modules
----------------

When a Module file specification is changed, the change is considered "compatible" or "incompatible" with existing user answers.

Many changes are "compatible": Changing the introduction or output documents, question prompts, and adding new questions and choices are all compatible changes. These changes can be made "live" on any existing user answers.

Other changes are "incompatible": Removing a choice is an incompatible change because a user may have already chosen it. Removing a question is incompatible because it would result in a loss of user data.

When there is an incompatible change in a Module specification, a new iteration of the Module will be stored in the program database but existing user answers will continue to be tied to the previous iteration of the Module specification.
