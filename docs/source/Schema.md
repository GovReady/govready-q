Modules, Questions, and Documents YAML Reference
================================================

A module and its questions are defined in YAML specification files. The schema for the specification files is as follows:

Module
------

Each file is a Module. A Module has the following required fields:

	id: module_id
	title: Your Title Here

The `module_id` must match the file name that the YAML is saved into, without the path or file extension.

Several optional fields can be specified:

	type: project
	version: 1
	instance-name: "Module for {{q1}}"
	invitation-message: "Can you tell me about {{question.text}} and let me know when you are done?"
	icon: app.png

The `type` field is set to `project` just when the Module is to be offered to users when they start a new Project. (`system-project` is used for project-like modules that are system controlled and not offered to the user.)

The `version` field is used only to force changes in the specification to be considered incompatible with any existing user answers (see Updating Modules).

The `instance-name` is a template to generate a dynamic title for in-progress and completed modules. The `instance-name` is rendered like other Module documents but it is always specified in `text` format (see Documents).

For modules that define the root of an application, `icon` specifies a static asset (in the `assets` directory) to use as an application icon.

In addition, a Module may have an `introduction` document (for projects, the introduction appears at the top of the project page; for other module types, it appears as an implicit initial interstitial) and a list of one or more `output` documents. For example:

	introduction:
	  format: markdown
	  template: |
	    Welcome to the module.

	    This module should take you two minutes.

	output:
	  - title: Document 1
	    format: markdown
	    template: |
	      # Document for {{project}}

	      Hello! This is the output of the module. You answered {{q1}}.

	  - title: Document 2
	    glyphicon: dashboard
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

### Additional fields for projects

#### Question Fields

The questions of projects are displayed in a layout of tabs and groups within each tab pane. Each question that shows up on a project page should specify its tab and group name (which are also the display strings):

	questions:
	- id: howto_ssp
	  title: "SSP 101: What's a System Security Plan"
	  type: module
	  module-id: howto_ssp
	  tab: How To
	  group: Start Here
	  icon: ssp.png

`icon` specifies a static asset (in the `assets` directory) to use as an icon for the question. If the question's type is `module` and it is answered and the answer is a Task that has a top-level `icon` field, then the answer's icon is used instead.

Instead of `tab` and `group`, `placement: action-buttons` can be used instead to show the question in an action bar above the tabs, rather than in tabs.

#### Output Document Fields

Output documents of a project module that have an `id` field are used in the following ways:

* They are displayed in the Related Controls page for the project. Add a `title` attribute to set the heading text above the document's content.
* They can be accessed from higher-level apps into which this app has been added. In a higher-level app, access the rendered HTML value of the output document as `{{question.output_documents.document_id}}`.

When `display: top` is set on an output document, it is rendered above the *Your Answers* section.

#### Test Answers

Projects can provide sets of exemplar answers for use in test scripts. e.g.:

	tests:
	  test1: # <-- test suite ID
	    description: "Sample data."
	    answers:
	      q1:
	        answers:  # <-- answers to sub-task's questions
	          q1: desktop
	          q2: My Secure Tool


Documents
---------

Documents occur as `introduction` and `output` documents of Modules, and a restricted form of documents also occurs in Question prompts (see Questions below). A document appearing in the output documents list is given as:

	output:
	  - id: mydoc
	    title: Document 1
	    format: markdown
	    template: |
	      Hello!

The `id` and `title` fields are generally optional and are used for output documents only. An `id` is required to make the document downloadable. The fields also have special uses in projects (see above). The `format` field is described below.

The document can also be stored in a separate file by replacing the document data in the module YAML file with a filename and placing the document properties and template in the named file, as in:

	# module.yaml
	output:
	  - mydoc.md

	# mydoc.md
	id: mydoc
	title: Document 1
	format: markdown
	...
	Hello!

When using a separate file, the document properties (`id`, `title`, and `format`) are given in a YAML block at the top of the file. A line containing just three dots signifies the end of the YAML block, separating it from the document template. The document template follows.

### Document Format

The `introduction` and `output` documents of Modules allow a format to be specified. The document formats are:

* `markdown` --- The document is entered in [CommonMark](http://commonmark.org/) ([quick guide](http://commonmark.org/help/)) in the specification file, but it will be rendered into a richly formatted presentation on screen.
* `html` --- The document is given in raw HTML, but it will be rendered on screen.
* `text` --- The document is given in plain text, and it will display as preformatted (fixed-width) text on screen.
* `json`, `yaml` --- Experimental.

#### Additional Markdown Notes

Documents specified in `markdown` format are rendered according to the [CommonMark 0.25 specification](http://commonmark.org/).

Note that for some things like tables, it is necessary to insert raw HTML right into the document, which is acceptable CommonMark. To create a table:

	<table><thead><th>

	Col 1

	</th>
	<th>

	Col 2

	</th>
	</thead>
	<tbody><tr><td>

	Some [commonmark](http://www.google.com) within the cell.

	</td>
	<td>

	More *content.*

	</td></tr></tbody></table>

Some of the newlines are necessary to get CommonMark to go out of raw HTML mode and back into parsing CommonMark.

### Document Templating

All document formats are evaluated as [Jinja2 templates](http://jinja.pocoo.org/docs/dev/templates/). That means within your document you can embed special tags that are replaced prior to the document being displayed to the user:

* `{{ question_id }}` will be replaced with the user's answer to the question whose `id` is `question_id`. For choice-type questions, the value is replaced by the choice `key`. Use `{{ question_id.text }}` to get display text. See the question types documentation below for details.
* `{% if question_id == 'value' %}....{% endif %}` is a conditional block. The contents inside the block (`....`) will be included in the output if the condition is true. In this example, the contents inside the block will be included in the output if the user's answer to `question_id` is `value`.

Output documents and question prompts have access to the user's answers to questions in question variables. (The introduction document does not have access to the user's answers because questions have not yet been answered.)

The following information is also available within the output template for each question as of version `v0.8.6`:

* `{{ question_id.not_yet_answered }}` Question has not yet been answered.
* `{{ question_id.answered }}`Question has an answer either by user or was imputed, but not imputed `null` or answered `null`.
* `{{ question_id.imputed }}` Question considered "answered" but no TaskAnswerHistory record exists in the database for question meaning a user didn't provide the answer.
* `{{ question_id.skipped }}` Question has a null answer either because imputed `null` or the user skipped it.
* `{{ question_id.skipped_by_user }}` Question has a `null` answer because used a skip button (e.g., question wasn't imputed `null`).
* `{{ question_id.skipped_reason }}` Question's indicated reason for skipping (e.g. "I don't know" or "It doesn't apply")
* `{{ question_id.unsure }}` If question was answered by a user, its unsure flag. (NOTE: Purpose of this flag was to allow users to indicate uncertainty in the answer. Due to usability issues however, this feature is currently hidden.)
* `{{ question_id.date_answered }}` Question answered date.
* `{{ question_id.reviewed_state }}` Question reviewed value.

All documents also have access to the project title as `{{project}}`.

### Project Documents

In addition to the `output` documents described above, a project module may also have a `snippet` that defines how a project appears in the project listing page:

	snippet:
	  format: markdown
	  template: |
	    Project {{name}}


Module Assets
-------------

Modules often make use of assets outside of the YAML file.

### Static Assets

Static assets such as images can be referenced in module content (introductions, question prompts, and output documents). These assets are exposed by the Q web server in its static path. Place static assets in an `assets` subdirectory where the module is. When the asset is referenced in a Markdown document template, its path will be rewritten to be its public (virtual) path on the web server.

For example, to include an image in a module introduction add the image in the Markdown template:

	module.yaml
	-----------

	...
	format: markdown
	template: |
	  ![](my_image.png)
	...

Place the module and image files at the path:

	module.yaml
	assets/my_image.png

### Private Assets

Private assets are other files that are stored with a module but are not exposed by the web server. The directory provides a place to store files for internal use during module development.

Place private assets in a `private-assets` subdirectory next to the module YAML file.


Questions
---------

Questions have the following required fields:

	  - id: q1
	    title: Your Favorite Animal
	    prompt: What's your favorite animal?
	    type: text

The question `id` is used to refer to this Question in other questions and in the output documents.

The `title` is used to describe the Question in places where a long-form prompt would not be appropriate.

The `prompt` is the text the user is prompted with when presented with the question. The prompt is rendered like other Module documents but it is always specified in `markdown` format (see Documents). The first line (paragraph) of the prompt is shown in larger, bold type.

A question may have other optional fields that provide the user with other information, such as:

	    examples:
	    - example: |
	       First example.
	    - example: |
	       Second example.
	    reference_text: See NIST SP 800-171 page 102.

Like the `prompt`, each entry inside `examples` and the `reference_text` are Markdown templates.

Removing a question, changing a question type, and other changes as noted below are incompatible changes (see Updating Modules).

### Question Types

#### `text`

This type asks the user for a single line of free-form text. The text cannot be empty.

A `placeholder` can be specified which places ghosted "placeholder" text inside the form field when the user has not yet entered anything. A `default` value can be specified, instead, which fills in the field with a value that the user can edit (or not) before submitting the answer. The placeholder and default fields are rendered like other Module documents --- just like the `prompt`.

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

This type asks the user for a password. It is the same as the `text` question type, except that a password input field is used to mask the input. `help` can be specified. `placeholder` and `default` are not allowed.

#### `email-address`

This type asks the user for an email address. It is the same as the `text` question type, except that the value entered must be a valid email address. `placeholder`, `default`, and `help` can be specified.

#### `url`

This type asks the user for a web address (a URL). It is the same as the `text` question type, except that the value entered must be a valid web address. `placeholder`, `default`, and `help` can be specified. The web address is not checked for existence --- only the form (syntax) of the address is checked.

#### `longtext`

This type asks the user for free-form text using a large rich text input area that allows for multiple lines of text and some simple formatting. The text cannot be empty.

A `default` value can be specified, which fills in the field with a value that the user can edit (or not) before submitting the answer. The field is rendered like other Module documents --- just like the `prompt`. It is given in Markdown.

`help` text can be specified which provides an additional prompt smaller and below the field input.

In document templates and impute conditions, the value of `longtext` questions is the text the user entered, as a string, with rich formatted represented in CommonMark. In document templates, the text is automatically converted back to rich formatting.

#### `date`

This type asks the user for a date.

`help` text can be specified which provides an additional prompt smaller and below the field input.

In document templates and impute conditions, the value of `date` questions is a text string in YYYY-MM-DD format.

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

#### `datagrid`

The `datagrid` question type is similar to the `multiple-choice` question type except that:

* An array of fields define columns for tabular data (AKA "datagrid").
* Users can enter as many rows of data as desired.
* Results are usually displayed as a table.
* `min` and `max` may be specified. If `min` is specified, it must be greater than or equal to zero and requires that the user add at least that many rows. If `max` is specified, it must be greater than or equal to one (and if `min` is specified, it must be at least `min`) and prevents the user from adding more than that number rows.

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

#### `file`

This question type asks the user to upload a file.

`help` text can also be specified, as in the text question types.

By default, any type of file is permitted to be uploaded. If the optional `file-type` field is set, the uploaded file is validated to be of a particular type. Supported values for the `file-type` field are:

* `image`: Ensures the file is an image. The uploaded file is converted to PNG format internally.

If `file-type` is `image`, then some image transformation can be run, e.g.:

	- id: logo
	  title: Logo
	  prompt: Upload a logo.
	  type: file
	  file-type: image
	  image:
	    max-size:
	      width: 60
	      height: 60

If `image->max-size` is given, then the image will be resized prior to being saved internally so that its width and height do not exceed the given dimensions.

In document templates and impute conditions, the value of these questions is a Python dict (JSON object) containing `url` (a download URL) and `size` (in bytes) fields.

#### `module`, `module-set`

These question type prompt the user to select another completed module as the answer to the question. The `module-id` field specifies the ID of another module specification. The `module` question type allows for a single other module to answer the question. The `module-set` question type allows for zero or more other modules to answer the question.

The `module-id` field specifies a module ID as it occurs in the `id` field of another YAML file in the same application.

##### Example

Here's an example of the `module` question type:

	  - id: evidence
	    title: Evidence
	    type: module
	    module-id: evidence
	    prompt: |
	      Provide evidence of your properly configured firewall, if possible.
	    impute:
	      - condition: not(have_other_dmz == 'ad_hoc_dmz')
	        value: ~

##### App protocols

Instead of using `module-id`, a `protocol` can be specified instead. A protocol is a globally unique identifier that apps in the Compliance Store use to indicate that their questions and output documents meet a certain criteria (i.e. implement the protocol). When a user attempts to answer a `module` or `module-set` question that uses `protocol` instead of `module-id`, instead of starting a particular named module, the user instead can start any app from the Compliance Store that implements the protocol.

For example:

	  - id: evidence
	    title: Evidence
	    type: module
	    protocol: govready.com/apps/compliance/2017/nist-sp-800-171-r1-ssp
	    prompt: |
	      Provide evidence of your properly configured firewall, if possible.

When a user answers this question, they will be redirected to the Compliance Store but will be offered only apps that implement the protocol `govready.com/apps/compliance/2017/nist-sp-800-171-r1-ssp`.

An app implements a protocol by having a `protocol: ` field at the top level of the app's YAML specification file with the same value. For instance, the following app would be offered in the Compliance Store for this example question:

	id: app
	title: My App
	type: project
	protocol: govready.com/apps/compliance/2017/nist-sp-800-171-r1-ssp

Both protocol fields can be either a single string or a list of strings. When the question `protocol` value is a list, then only apps which implement all of the listed protocols will be offered.

##### Question type details

Changing the `module-id` or `protocol` is considered an incompatible change (see Updating Modules), and if the referenced Module's specification is changed on disk in an incompatible way with existing user answers, the Module in which the question occurs is also considered to have an incompatible change. Thus an incompatible change in a module triggers an incompatible change in any other Module that refers to it (and so on recursively).

In document templates and impute conditions, the value of `module` questions is a dictionary of the answers to that module. For example, if `q5` is the ID of a question whose type is `module`, then `{{q5.q1}}` will provide the answer to `q1` within the module the user selected that answers `q5`.

#### `interstitial`

An `interstitial` question is not really a question at all! The `prompt` contains template content, as with other questions, but it is typically longer content with deeper explanatory text. The user is not asked to enter any information.

In document templates and impute conditions, the value of `interstitial` questions is always a null value.

#### `raw`

This type is meant for questions that are always imputed (i.e. that are never presented to the user) and where the answer value can be any JSON-serializable Python data structure, as given by the impute value (see Imputing Answers below).

This question type should be avoided if one of the other question types specifies a more narrow data type. For instance, if the imputed value is always a string, the `text` or `longtext` question types should be used instead.


### Imputing Answers

The answer to one question may provide the answer to another. In such cases, the latter question is said to have an imputed value and the user is not asked to answer the question. To impute a value, specify on the question whose value is being imputed:

    impute:
      - condition: q1 == 'no'
        value: don't know

This example says that if the answer to `q1` is `no`, then the answer to this question is `don't know`.

The `condition` is a [Jinja2 expression](http://jinja.pocoo.org/docs/dev/templates/#expressions). Any question can be referred to in the expression (by its `id`). Questions are tested on their internal values. For `choice` and `multiple-choice` questions, their values are their `key`s, not their label text, and `multiple-choice` questions are _lists_ of keys. If `condition` is omitted, the imputed value is always taken (i.e. the condition is implicitly met).

The `value` provided must be a valid value for the question type it is a part of. For `choice` questions, the value must be a choice `key`, not the label text. For `multiple-choice` questions, the value must be a _list_ of keys.

Multiple condition/value blocks can be provided. They are evaluated in order, with the first matching condition taking precedence.

    impute:
      - condition: q1 == 'no'
        value: I don't know.
      - condition: q1 == 'yes'
        value: I do know.

The `value` field can be evaluated as a [Jinja2 expression](http://jinja.pocoo.org/docs/dev/templates/#expressions), just like the condition, if `value-mode` is set to `expression`. This can be used to pull forward the answers of previous questions:

    impute:
      - condition: q1 == 'same-as-q0'
        value: q0
        value-mode: expression

`value-mode` can also be `template` to evaluate the value as a Jinja2 template, which will yield a text value.

In both conditions and `expression`-type values, as well as in documents, the variables you can use are:

* `id`s of questions in the module
* `question_id.subquestion_id` to access questions within the tasks that are assigned as answers to `module`-type questions
* `project`, which gives the project name
* `project.question_id`, `project.question_id.subquestion_id`, etc. to access questions within the project
* `organization`, which gives the organization name

We also have a function to retrieve the URL of a module's static assets, e.g.:

	<script src="{{static_asset_path_for('myscript.js')}}"></script>

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
