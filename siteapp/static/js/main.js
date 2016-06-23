$(function() {
  // General Event Handlers

  // [CTRL/Meta]+Enter in any textarea triggers submission of the form it is
  // contained in.
  $('textarea').keydown(textarea_ctrlenter_handler);
})

function textarea_ctrlenter_handler(e) {
  if ((e.ctrlKey || e.metaKey) && (e.keyCode == 13 || e.keyCode == 10))
    $(this).parents('form').submit();
}

var invite_modal_info_data = { };
var invite_modal_extra_data = { };
var invite_modal_callback = function() { };
function show_invite_modal(title, prompt, info, message_default_text, data, callback) {
  var m = $('#invitation_modal');
  m.find('h4').text(title);
  m.find('p').text(prompt);

  var s = m.find('form select[name=user]');
  s.prop('disabled', false);
  s.text('');
  if (info.users.length > 0 && !data.add_to_team && !data.into_discussion) {
    // The users list only has project members. They are already in the project/discussion,
    // so it doesn't make sense to list them if we are doing an invite to a project/discussion.
    s.append($("<option/>").attr('value', '').text('Select team member...'))
    info.users.forEach(function(user) {
      s.append($("<option/>").attr('value', user.id).text(user.name))
    })
  } else {
    m.find('label[for="invite-user-email"] span').remove(); // hide link to hide the email address input and show the dropdown because drop-down is empty
  }
  s.append($("<option/>").attr('value', '__invite__').text("Invite someone new..."))
  if (data.user_id) {
    s.val(data.user_id);
    if (s.val() == data.user_id) // valid?
      s.prop('disabled', true);
  }

  $('#invite-message').text(message_default_text);

  invite_modal_info_data = info;
  invite_modal_extra_data = data;
  invite_modal_callback = callback;

  invite_toggle_mode();

  m.modal();
}
function invite_toggle_mode() {
  // inviting by email ?
  var m = ($('#invite-user-select').val() == '__invite__');

  $('#invite-user-select').parent().toggle(!m);
  $('#invite-user-email').parent().toggle(m);

  // show the Add to Team? checkbox if:
  //  * we're inviting someone by email (i.e. they're not already in the project)
  //  * the user has permission to add someone to the team
  //  * the user didn't click an Invite to Project button, so we already know that's what the user wants
  $('#invite-addtoteam-container').toggle(m && invite_modal_info_data.can_add_invitee_to_team && !invite_modal_extra_data.add_to_team);
  if (!(m && invite_modal_info_data.can_add_invitee_to_team))
    $('#invite-addtoteam-container input[name="add-to-team"]').prop('checked', false);
}
function send_invitation(form) {
  var data = {
     add_to_team: $('#invitation_modal form input[name=add-to-team]').is(':checked') ? "1" : "",
     user_id: $('#invite-user-select').is(":visible") ? $('#invite-user-select').val() : null,
     user_email: $('#invite-user-email').is(":visible") ? $('#invite-user-email').val() : null,
     message: $('#invite-message').val()
  };
  for (var k in invite_modal_extra_data)
    data[k] = invite_modal_extra_data[k];
  $('#invitation_modal').modal('hide');
  ajax_with_indicator({
   url: $('#invitation_modal').attr('data-url'),
   method: "POST",
   data: data,
   success: function(res) {
     // status == error is handled by ajax_with_indicator
     show_modal_error("Send Invitation", "The invitation has been sent. We will notify you when the invitation has been accepted.", 
      invite_modal_callback);
   }
  });

  return false;
}


function cancel_invitation(elem, callback) {
  var container = $(elem).parents('[data-invitation-id]');
  var invid = container.attr('data-invitation-id');
  ajax_with_indicator({
   url: '/invitation/_cancel',
   method: "POST",
   data: {
    id: invid
   },
   success: function(res) {
     show_modal_error("Cancel Invitation", "The invitation has been canceled.");
     container.slideUp(function() {
      container.remove();
      if (callback) callback();
     })
   }
  });
  return false;
}

function mark_notifications_read(upto_id) {
  $.ajax({
   url: '/_mark_notifications_as_read',
   method: "POST",
   data: {
    upto_id: upto_id
   }
  });
  $('.notification.unread').removeClass('unread');
  return false;
}