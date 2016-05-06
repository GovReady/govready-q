var invite_modal_extra_data = { };
var invite_modal_callback = function() { };
function show_invite_modal(title, prompt, info, message_default_text, data, callback) {
  var m = $('#invitation_modal');
  m.find('h4').text(title);
  m.find('p').text(prompt);

  var s = m.find('form select[name=user]');
  s.prop('disabled', false);
  s.text('');
  if (info.users.length > 0)
    s.append($("<option/>").attr('value', '').text('Select team member...'))
  else
    m.find('label[for="invite-user-email"] span').remove(); // hide link to hide the email address input and show the dropdown because drop-down is empty
  info.users.forEach(function(user) {
    s.append($("<option/>").attr('value', user.id).text(user.name))
  })
  s.append($("<option/>").attr('value', '__invite__').text("Invite someone new..."))
  if (data.user_id) {
    s.val(data.user_id);
    if (s.val() == data.user_id) // valid?
      s.prop('disabled', true);
  }
  invite_toggle_mode();

  $('#invite-message').text(message_default_text);

  invite_modal_extra_data = data;
  invite_modal_callback = callback;

  m.modal();
}
function invite_toggle_mode() {
  var m = ($('#invite-user-select').val() == '__invite__'); // inviting by email
  $('#invite-user-select').parent().toggle(!m);
  $('#invite-user-email').parent().toggle(m);
  $('#invite-addtoteam-container').toggle(m);
}
function send_invitation(form) {
  var data = {
     //prompt_task
     //prompt_question_id
     add_to_team: $('#invitation_modal form input[name=add-to-team]').attr('checked') != null ? "1" : "0",
     into_new_task_module_id: $('#invitation_modal form select[name=module]').val(),
     //into_task_editorship
     //into_discussion
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
