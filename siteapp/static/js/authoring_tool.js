function init_authoring_tool(state) {
  // Save state. Should be:
  // {
  //  module: { module spec data },
  //  questions: {
  //    question_key: {
  //      spec: { spec data },
  //      choices: "choices encoded as CSV string",
  //      answer_type_module_id: (integer)
  //    }
  //  },
  //  answer_type_modules: [ { id: module_id, title: "Module Name" } ],
  //  autocomplete_questions: {
  //    question_key: help_text
  //  }
  // }
  window.q_authoring_tool_state = state;

  // Project questions do not have a prompt, impute conditions, and only module-type questions
  // are available.
  $('#authoring_tool_qprompt').parents('.form-group').toggle(state.module.type != "project");
  $('#question_authoring_tool .impute-condtions-holder, #authoring_tool_type optgroup:not(.available-for-projects)').toggle(state.module.type != "project");

  // Create the drop-down options for module-type questions.
  $('#authoring_tool_qmoduletype').html('<option value="">(select)</option>'); // clear options
  var optgroup_apps = $('<optgroup label="From the Compliance Store"></optgroup>');
  $('#authoring_tool_qmoduletype').append(optgroup_apps);
  optgroup_apps.append('<option value="/app/">Based on Protocol ID (Enter Next)</option>');
  if (state.answer_type_modules.length > 0) {
    var module_question = Object.keys(state.questions)[0];
    var module_question_module_id = state.questions[module_question].spec['module-id'];
    var optgroup_modules = $('<optgroup label="Modules in This App"></optgroup>');
    $('#authoring_tool_qmoduletype').append(optgroup_modules);
    state.answer_type_modules.forEach(function(item) {
      var opt = $("<option/>");
      opt.attr('value', item.id);
      opt.text(item.title);
      // select current module
      if (item.id == module_question_module_id) {
        opt.attr('selected', 'selected');
      }
      optgroup_modules.append(opt);
    });
  }

  // The protocol ID field is only visible if needed.
  $('#authoring_tool_qmoduletype').change(function() {
    $('#authoring_tool_qmoduleprotocol').parents('.form-group')
      .toggle($(this).val() == "/app/");
  });

  // Make the prompt textarea auto-resizing when the modal first is shown,
  // so that it is autosized to any text already inside it, which must be
  // done after it's visible.
  $('#question_authoring_tool').on('shown.bs.modal', function() { autosize.update($(this).find('textarea')) });
  $('#module_authoring_tool').on('shown.bs.modal', function() { autosize.update($(this).find('textarea')) });
  $('#questionnaire_authoring_tool').on('shown.bs.modal', function() { autosize.update($(this).find('textarea')) });

  // Init autocompletes for inputs/textareas that are interpreted as templates.
  init_authoring_tool_autocomplete($('#authoring_tool_qprompt'), "template");
  init_authoring_tool_autocomplete($('#authoring_tool_mspec'), "template");
}

function init_authoring_tool_autocomplete(elem, expr_type) {
  // Add question IDs as autocompletes to the fields that use Jinja2
  // expressions.
    if(elem[0] === undefined)
        return
  var question_keys = window.q_authoring_tool_state.autocomplete_questions;

  var trigger = "{{";
  if (expr_type == "template") trigger = "\{\{";
  
  var textcomplete = new Textcomplete(new Textcomplete.editors.Textarea(elem[0]));
  textcomplete.register([{
    match: new RegExp("(^|\\s" + trigger + ")([a-zA-Z_][a-zA-Z0-9_]*)?$"),
    search: function (term, callback, match) {
      // Perform a fuzzy match.
      var matches = [];
      term = (match[2] || "").toLowerCase().replace(/_/, "");
      Object.keys(question_keys).forEach(function(key) {
        var search_key = key.toLowerCase().replace(/_/, "");
        if (search_key.indexOf(term) >= 0)
          matches.push(key);
      });
      callback(matches)
    },
    template: function(value) {
      var node = $("<span><span class='term'/> <span class='info' style='font-style: italic; padding-left: 1.5em;'/></span>");
      node.find(".term").text(value);
      node.find(".info").text(question_keys[value]);
      return node.html();
    },
    replace: function(value, event) { return "$1" + value.replace(/\$/g, "$$$$") + "}}"; } // must escape any dollar signs in the replacement text, and since we're using replace to do it we need to escape the literal $ twice!
  }], {
    style: {
      zIndex: 10000
    }
  });
}

function show_question_authoring_tool(question_id, question_key) {
  // Initialize form state.
  window.q_authoring_tool_state.current_question = question_key;
  var qinfo = window.q_authoring_tool_state.questions[question_key];
  var spec = JSON.parse(JSON.stringify(qinfo.spec)); // clone since we delete properties

  $('#at_q_id').val(question_id);
  $('#authoring_tool_qid').val(question_key); delete spec.id;
  $('#authoring_tool_q_title').val(spec.title); delete spec.title;
  $('#authoring_tool_qprompt').val(spec.prompt); delete spec.prompt;
  $('#authoring_tool_type').val(spec.type)
    .change(); // trigger event that hides/shows the appropriate fields
    delete spec.type;
  $('#authoring_tool_placeholder').val(spec.placeholder); delete spec.placeholder;
  $('#authoring_tool_default').val(spec.default); delete spec.default;
  $('#authoring_tool_qchoices').val(qinfo.choices); delete spec.choices;
  $('#authoring_tool_qmin').val(spec.min); delete spec.min;
  $('#authoring_tool_qmax').val(spec.max); delete spec.max;
  $('#authoring_tool_filetype').val(spec["file-type"]); delete spec['file-type'];
  $('#authoring_tool_qhelp').val(spec.help); delete spec.help;
  if (qinfo.answer_type_module_id)
    $('#authoring_tool_qmoduletype').val(qinfo.answer_type_module_id);
  else if (spec.protocol)
    $('#authoring_tool_qmoduletype').val("/app/");
  delete spec['module-id'];
  $('#authoring_tool_qmoduletype').change(); // run event handler to hide/show protocol field
  if (spec.protocol) {
    $('#authoring_tool_qmoduleprotocol').val(spec.protocol.join(" "));
    delete spec.protocol;
  }

  $('#authoring_tool_impute_conditions').html('');
  (spec.impute || []).forEach(function(impute) {
    var value_mode = impute['value-mode'] || "raw";
    var n = authoring_tool_add_impute_condition_fields();
    $(n.find('input')[0]).val(impute.condition);
    $(n.find('input')[1]).val(value_mode == "raw" ? jsyaml.safeDump(impute.value) : impute.value);
    n.find('select').val(value_mode);
  });
  delete spec.impute;
  
  if (Object.keys(spec).length == 0) spec = "";
  else spec = jsyaml.safeDump(spec);
  $('#authoring_tool_qspec').val(spec);
  // Show modal.
  $('#question_authoring_tool').modal();
}

function authoring_tool_add_impute_condition_fields() {
  var ctr = $('#authoring_tool_impute_conditions .impute-condition').length + 1;
  var n = $(
  	  "<div class='impute-condition' style='padding-bottom: .5em'>"

    + "<div class='form-group'>"
    + "<label for='authoring_tool_impute_condition_" + ctr + "_condition' class='col-sm-2 control-label' style='font-weight: normal'>Condition " + ctr + "</label>"
    + "<div class='col-sm-10'>"
    + "<input type='text' class='form-control' id='authoring_tool_impute_condition_" + ctr + "_condition' name='impute_condition_" + ctr + "_condition'>"
    + "</div>"
    + "</div>"

    + "<div class='form-group'>"
    + "<label for='authoring_tool_impute_condition_" + ctr + "_value' class='col-sm-2 control-label' style='font-weight: normal'>Value " + ctr + "</label>"
    + "<div class='col-sm-7'>"
    + "<input type='text' class='form-control' id='authoring_tool_impute_condition_" + ctr + "_value' name='impute_condition_" + ctr + "_value'>"
    + "</div>"
    + "<div class='col-sm-3'>"
    + "<select class='form-control' name='impute_condition_" + ctr + "_valuemode'><option value='raw'>YAML Value</option><option value='expression'>Jinja2 Expression</option><option value='template'>Jinja2 Template</option></select>"
    + "</div>"
    + "</div>"

    + "</div>");
  $('#authoring_tool_impute_conditions').append(n);
  init_authoring_tool_autocomplete($(n.find("input")[0], "expression"));
  return n;
}

function authoring_tool_download_app() {
  var data = [{ name: "task", value: q_authoring_tool_state.task }]
  data.push( { name: "question", value: Object.getOwnPropertyNames(q_authoring_tool_state.questions)[0] } );
  ajax_with_indicator({
    url: "/tasks/_authoring_tool/download-app",
    method: "POST",
    data: data,
    keep_indicator_forever: false,
    success: function(res) {
      // Stay on same page to see new content
      $('#questionnaire_authoring_tool_mspec').val(res.data);
      // Show modal.
      $('#questionnaire_authoring_tool').modal();
    }
  });
}

function authoring_tool_download_app_project(task_id, is_project_page) {
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/download-app-project",
      method: "POST",
      // we may not need to send any data because view understands the task from the decorator
      // var data = [{ name: "task", value: q_authoring_tool_state.task }]
      data: { task: task_id },
      // keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        console.log("success");
        console.log(res.data);
        // Stay on same page to see new content
        $('#questionnaire_authoring_tool_mspec').val(res.data);
        // Show modal
        $('#questionnaire_authoring_tool').modal();
      }
  })
}

function authoring_tool_save_question() {
  var data = $('#question_authoring_tool form').serializeArray();
  if (q_authoring_tool_state.task) {
    data.push( { name: "task", value: q_authoring_tool_state.task } );
  }
  data.push( { name: "question", value: q_authoring_tool_state.current_question } );
  console.log('authoring_tool_save_question')
  console.log(data)
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/edit-question2",
      method: "POST",
      data: data,
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
      	// Modal can stay up until the redirect finishes.
        window.location = res.redirect;
        if (window.location.hash.length > 1)
          window.location.reload(); // if there is a # in the URL, the browser won't actually reload
      }
  })
}

function authoring_tool_delete_question() {
  if (!confirm("WARNING! CLICKING 'OK' WILL PERMANENTLY DELETE THIS QUESTION (AND ANSWERS) FROM ALL PROJECTS USING THIS TEMPLATE.")) return;
  var data = $('#question_authoring_tool form').serializeArray();
  if (q_authoring_tool_state.task) {
    data.push( { name: "task", value: q_authoring_tool_state.task } );
  }
  data.push( { name: "question", value: q_authoring_tool_state.current_question } );
  data.push( { name: "delete", value: 1 } );
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/edit-question2",
      method: "POST",
      data: data,
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        // Modal can stay up until the redirect finishes.
        window.location = res.redirect;
        if (window.location.hash.length > 1)
          window.location.reload(); // if there is a # in the URL, the browser won't actually reload
      }
  })
}

function authoring_tool_new_question(task_id, question_id, is_project_page) {
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/new-question",
      method: "POST",
      data: { "task": task_id, "question_id": question_id },
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        // Modal can stay up until the redirect finishes.
        if (is_project_page)
          window.location.reload();
        else
          window.location = res.redirect;
      }
  })
}

function authoring_tool_new_question2(question_id) {
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/new-question2",
      method: "POST",
      data: { "question_id": question_id },
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        window.location = res.redirect;
      }
  })
}

function show_authoring_tool_module_editor() {
  // Initialize form state for the compliance app catalog information
  // field and the module specification field.
  $('#authoring_tool_catalog_metadata').parents('.form-group').toggle(typeof window.q_authoring_tool_state.catalog_yaml != "undefined");
  $('#authoring_tool_catalog_metadata').val(window.q_authoring_tool_state.catalog_yaml);
  $('#authoring_tool_mspec').val(window.q_authoring_tool_state.module_yaml);

  // Show modal.
  $('#module_authoring_tool').modal();
}

function authoring_tool_save_module() {
  var data = $('#module_authoring_tool form').serializeArray();
  data.push( { name: "task", value: q_authoring_tool_state.task } );
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/edit-module",
      method: "POST",
      data: data,
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        // Modal can stay up until the redirect finishes.
        window.location = res.redirect;
        if (window.location.hash.length > 1)
          window.location.reload(); // if there is a # in the URL, the browser won't actually reload
      }
  });
}

function authoring_tool_create_q_form(argument) {
  console.log(argument);
  $('#create_q_authoring_tool').modal();
  console.log(Object.keys(argument))
  if (Object.keys(argument).includes('app_id')) {
    $('#authoring_tool_app_id').val(argument['app_id']);
  }
  if (Object.keys(argument).includes('app_title')) {
    console.log(argument);
    $('#authoring_tool_q_2_title').val(argument['app_title']+" Copy");
    var slug = $('#authoring_tool_q_2_title').val();
    slug = slug.toLowerCase().replace(/[^a-z0-9--]+/g, "_");
    $('#authoring_tool_q_name').val(slug);
  }
  if (Object.keys(argument).includes('app_description')) {
    $('#authoring_tool_q_description').val(argument['app_description'].replace('<p>','').replace('</p>',''));
  }
  if (Object.keys(argument).includes('app_category_title')) {
    $('#authoring_tool_q_category').val(argument['app_category_title']);
  }
  if (Object.keys(argument).includes('modal_title')) {
    $('#create_q_authoring_tool_title').html(argument['modal_title']);
  }
}

function authoring_tool_create_q() {
  var data = $('#create_q_authoring_tool form').serializeArray();
  console.log("data is: "+JSON.stringify(data));
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/create-app-project",
      method: "POST",
      data: data,
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        // Modal can stay up until the redirect finishes.
        window.location = res.redirect;
        if (window.location.hash.length > 1)
          window.location.reload(); // if there is a # in the URL, the browser won't actually reload
      }
  });
}

function authoring_tool_import_appsource_form(argument) {
  $('#import_appsource_authoring_tool').modal();
}

function authoring_tool_import_appsource() {
  // Use FormData to serialize form object including uploaded file
  var data = new FormData($('#import_appsource_authoring_tool form')[0]);
  console.log("data is: "+JSON.stringify(data));
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/import-appsource",
      method: "POST",
      data: data,
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        // Modal can stay up until the redirect finishes.
        window.location = res.redirect;
        if (window.location.hash.length > 1)
          window.location.reload(); // if there is a # in the URL, the browser won't actually reload
      }
  });
}
