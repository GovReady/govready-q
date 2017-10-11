function init_authoring_tool(state) {
  // Save state. Should be:
  // {
  //  task: task_id,
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
  var optgroup_modules = $('<optgroup label="Modules in This App"></optgroup>');
  $('#authoring_tool_qmoduletype').append(optgroup_modules);
  optgroup_apps.append('<option value="/app/">Based on Protocol ID (Enter Next)</option>');
  state.answer_type_modules.forEach(function(item) {
    var opt = $("<option/>");
    opt.attr('value', item.id);
    opt.text(item.title);
    optgroup_modules.append(opt);
  });

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

  // Init autocompletes for inputs/textareas that are interpreted as templates.
  init_authoring_tool_autocomplete($('#authoring_tool_qprompt'), "template");
  init_authoring_tool_autocomplete($('#authoring_tool_mspec'), "template");
}

function init_authoring_tool_autocomplete(elem, expr_type) {
  // Add question IDs as autocompletes to the fields that use Jinja2
  // expressions.
  var question_keys = window.q_authoring_tool_state.autocomplete_questions;

  var trigger = "";
  if (expr_type == "template") trigger = "|\{\{";
  
  elem.textcomplete([{
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
    replace: function(value, event) { return "$1" + value.replace(/\$/g, "$$$$"); } // must escape any dollar signs in the replacement text, and since we're using replace to do it we need to escape the literal $ twice!
  }], {
    style: {
      zIndex: 10000
    }
  });
}

function show_question_authoring_tool(question_key) {
  // Initialize form state.
  window.q_authoring_tool_state.current_question = question_key;
  var qinfo = window.q_authoring_tool_state.questions[question_key];
  var spec = JSON.parse(JSON.stringify(qinfo.spec)); // clone since we delete properties
  $('#authoring_tool_qid').val(question_key); delete spec.id;
  $('#authoring_tool_qtitle').val(spec.title); delete spec.title;
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

function authoring_tool_save_question() {
  var data = $('#question_authoring_tool form').serializeArray();
  data.push( { name: "task", value: q_authoring_tool_state.task } );
  data.push( { name: "question", value: q_authoring_tool_state.current_question } );
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/edit-question",
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
  if (!confirm("Are you sure you want to delete this question?")) return;
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/edit-question",
      method: "POST",
      data: {
        task: q_authoring_tool_state.task,
        question: q_authoring_tool_state.current_question,
        delete: 1
      },
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        // Modal can stay up until the redirect finishes.
        window.location = res.redirect;
        if (window.location.hash.length > 1)
          window.location.reload(); // if there is a # in the URL, the browser won't actually reload
      }
  })
}

function authoring_tool_new_question(task_id, is_project_page) {
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/new-question",
      method: "POST",
      data: { task: task_id },
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

function authoring_tool_reload_app(task_id) {
  if (!confirm("Are you sure you want to reload this app from its source?"))
    return;
  ajax_with_indicator({
      url: "/tasks/_authoring_tool/reload-app",
      method: "POST",
      data: {
        task: task_id,
        force: "false"
      },
      keep_indicator_forever: true, // keep the ajax indicator up forever --- it'll go away when we issue the redirect
      success: function(res) {
        window.location.reload();
      }
  })
}

function show_authoring_tool_module_editor() {
  // Initialize form state.
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
  })
}
