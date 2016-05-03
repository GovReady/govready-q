// https://github.com/JoshData/html5-stub/blob/master/static/js/bootstrap-helpers.js

var global_modal_state = null;
var global_modal_funcs = null;

$(function() {
  $('#global_modal').on('shown.bs.modal', function (e) {
    // set focus to first input in the global modal's body
    var input = $('#global_modal .modal-body input');
    if (input.length > 0) $(input[0]).focus();  
  })  
  $('#global_modal .btn-danger').click(function() {
    // Don't take action now. Wait for the modal to be totally hidden
    // so that we don't attempt to show another modal while this one
    // is closing.
    global_modal_state = 0; // OK
  })
  $('#global_modal .btn-default').click(function() {
    global_modal_state = 1; // Cancel
  })
  $('#global_modal').on('hidden.bs.modal', function (e) {
    // do the cancel function
    if (global_modal_state == null) global_modal_state = 1; // cancel if the user hit ESC or clicked outside of the modal
    if (global_modal_funcs && global_modal_funcs[global_modal_state])
      global_modal_funcs[global_modal_state]();
  })  
})

function show_modal_error(title, message, callback) {
  $('#global_modal h4').text(title);
  $('#global_modal .modal-body').html("<p/>");
  if (typeof question == 'string') {
    $('#global_modal p').text(message);
    $('#global_modal .modal-dialog').addClass("modal-sm");
  } else {
    $('#global_modal p').html("").append(message);
    $('#global_modal .modal-dialog').removeClass("modal-sm");
  }
  $('#global_modal .btn-default').show().text("OK");
  $('#global_modal .btn-danger').hide();
  global_modal_funcs = [callback, callback];
  global_modal_state = null;
  $('#global_modal').modal({});
  return false; // handy when called from onclick
}

function show_modal_confirm(title, question, verb, yes_callback, cancel_callback) {
  $('#global_modal h4').text(title);
  if (typeof question == 'string') {
    $('#global_modal .modal-dialog').addClass("modal-sm");
    $('#global_modal .modal-body').html("<p/>");
    $('#global_modal p').text(question);
  } else {
    $('#global_modal .modal-dialog').removeClass("modal-sm");
    $('#global_modal .modal-body').html("").append(question);
  }
  if (typeof verb == 'string') {
    $('#global_modal .btn-default').show().text("Cancel");
    $('#global_modal .btn-danger').show().text(verb);
  } else {
    $('#global_modal .btn-default').show().text(verb[1]);
    $('#global_modal .btn-danger').show().text(verb[0]);
  }
  global_modal_funcs = [yes_callback, cancel_callback];
  global_modal_state = null;
  $('#global_modal').modal({});
  return false; // handy when called from onclick
}

var ajax_num_executing_requests = 0;
function ajax_with_indicator(options) {
  setTimeout("if (ajax_num_executing_requests > 0) $('#ajax_loading_indicator').fadeIn()", 100);
  function hide_loading_indicator() {
    ajax_num_executing_requests--;
    if (ajax_num_executing_requests == 0)
      $('#ajax_loading_indicator').stop(true).hide(); // stop() prevents an ongoing fade from causing the thing to be shown again after this call
  }
  var old_success = options.success;
  var old_error = options.error;
  options.success = function(data) {
    hide_loading_indicator();
    if (data.status == "error")
      show_modal_error("Error", data.message);
    else if (old_success)
      old_success(data);
  };
  options.error = function(jqxhr) {
    hide_loading_indicator();
    if (!old_error && jqxhr.status == 500 && /^text\/html/.test(jqxhr.getResponseHeader("content-type")) && /^(<!DOCTYPE[\w\W]*>)?\s*<html/.test(jqxhr.responseText)) {
      // We might get back HTML in a 500 error. Flask does this. Show the
      // HTML, in an iframe.
      show_modal_error("Error", '<iframe style="width: 100%; height: 60vh;"></iframe>')
      var ifrm = $('#global_modal').find('iframe')[0];
      ifrm = (ifrm.contentWindow) ? ifrm.contentWindow : (ifrm.contentDocument.document) ? ifrm.contentDocument.document : ifrm.contentDocument;
      ifrm.document.open();
      ifrm.document.write(jqxhr.responseText);
      ifrm.document.close();
    } else if (!old_error) {
      show_modal_error("Error", "Something went wrong, sorry.")
    } else {
      old_error(jqxhr.responseText, jqxhr);
    }
  };
  ajax_num_executing_requests++;
  $.ajax(options);
  return false; // handy when called from onclick
}

function smooth_scroll_to(elem) {
  $('html, body').animate({
      scrollTop: Math.max(elem.offset().top-50, 0)
  });
}

