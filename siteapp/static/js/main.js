$(function() {
  // General Event Handlers

  // [CTRL/Meta]+Enter in any textarea triggers submission of the form it is
  // contained in.
  $('textarea').keydown(textarea_ctrlenter_handler);

  // Make textareas auto-sizing.
  autosize($('textarea'));

  // Make all tab navs responsive.
  $(".nav-tabs, .tab-content").addClass('responsive');
  fakewaffle.responsiveTabs(['xs', 'sm'])

  // Make question answers show popovers with additional information.
  $('.question-answer[data-answer-type=user-answer], .question-answer[data-edit-link]').popover({
    html: true,
    content: function() {
      var template = $(
          "<div><p class='author-info'>Answered by <span class='answered-by'></span> on <span class='answered-on'></span>.</p>"
        + "<p class='edit-link'>Edit answer to <a><span class='question'></span></a> in <span class='module'></span>.</p></div>");
      template.find('.author-info').toggle(this.getAttribute("data-answer-type") == "user-answer");
      template.find('.edit-link').toggle(this.hasAttribute("data-edit-link"));
      template.find('.answered-by').text(this.getAttribute("data-answered-by"));
      template.find('.answered-on').text(this.getAttribute("data-answered-on"));
      template.find('.question').text(this.getAttribute("data-question"));
      template.find('.module').text(this.getAttribute("data-module"));
      template.find('a').attr('href', this.getAttribute("data-edit-link"));
      return template.html();
    }
  })
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

  s.append($("<option/>").attr('value', '').text('Select a user...'))
  s.append($("<option/>").attr('value', '__invite__').text("Invite someone new by email..."))
  info.users.forEach(function(user) {
    s.append($("<option/>").attr('value', user.id).text(user.name))
  })

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
    window.location.reload()
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

function mark_notifications_read(data, callback) {
  // ajax call
  $.ajax({
   url: '/_mark_notifications_as_read',
   method: "POST",
   data: data,
   complete: callback
  });

  // update DOM (all .notification's or just those
  // that match the given ID)
  var f = "";
  if (data.id)
    f = "[data-notification-id=" + data.id + "]";
  $('.notification.unread' + f).removeClass('unread');
  return false;
}

function make_editable_div(elem, save_func) {
  // Create the input field, initially hidden.
  var input = $("<input type='text' class='form-control' style='display:none; font-size: inherit; height: inherit; padding: 0; margin: 0; border: 1px;'>");
  input.insertAfter(elem);
  input.keydown(function(e) {
    if (e.keyCode == 13 || e.keyCode == 10)
      $(this).blur();
  });

  // Toggle it on click.
  var field = elem.data('field');
  elem.css({ cursor: "pointer" });
  elem.click(function() {
    elem.hide();
    input.val(elem.attr("data-value"));
    input.show();
    input.focus();
  })

  // Update and restore on blur.
  input.blur(function() {
    var value = $(this).val();
    var none_text = elem.attr("data-none-text");
    elem.text(value || none_text);
    elem.attr("data-value", value);
    input.hide();
    elem.show();
    save_func(value);
  });
}

// For automated generation of screenshots and videos,
// add a picture of a cursor that follows the mouse cursor.
// Adapted from:
// https://stackoverflow.com/questions/35867776/visualize-show-mouse-cursor-position-in-selenium-2-tests-for-example-phpunit
function enableMouseCursorFollower()
{
  // Initialize a div that has an icon of a mouse cursor in it
  // and put it where we last saw the mouse on a previous page.
  var mouseimg = document.createElement("img");
  mouseimg.setAttribute('src', 'data:image/png;base64,'
    + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
    + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
    + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
    + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
    + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
    + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
    + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
    + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
    + 'dAAAAABJRU5ErkJggg==');
  mouseimg.setAttribute('id', 'selenium_mouse_follower');
  mouseimg.setAttribute('style', 'display: none; position: absolute; z-index: 99999999999; pointer-events: none;');
  document.body.appendChild(mouseimg);
  var xy = sessionStorage.getItem("mouse_cursor_follower_mouse_position");
  if (xy) {
    xy = xy.split(/,/);
    mouseimg.style.display = "block";
    mouseimg.style.left = xy[0] + "px";
    mouseimg.style.top = xy[1] + "px";
  }

  // Track the actual mouse. Selenium clicks cause the mouse position
  // to move.
  window.addEventListener("mousemove", function(e) {
    mouseimg.style.display = "block";
    mouseimg.style.left = e.pageX + "px";
    mouseimg.style.top = e.pageY + "px";
    sessionStorage.setItem("mouse_cursor_follower_mouse_position", e.pageX + "," + (e.pageY-$(window).scrollTop()));
  });

  // Move the mouse manually, with animation.
  window.moveMouseToElem = function(elem, animation_duration) {
    //var bounds = elem.getBoundingClientRect();
    //mouseimg.style.left = (bounds.left+bounds.width/2) + "px";
    //mouseimg.style.top = (bounds.top+bounds.height/2) + "px";

    // Create a function that smoothly moves the cursor between its current
    // position and the target location on the passed element.
    var current_pos = [$(mouseimg).offset().left, $(mouseimg).offset().top];
    var target_pos = [$(elem).offset().left+$(elem).width()/2, $(elem).offset().top+$(elem).height()/2];
    function move_cursor(t) {
      // make the motion curved
      // var tx = t**1.5;
      // var ty = t**.5;
      var tx = Math.pow(t,1.5);
      var ty = Math.pow(t,0.5);

      // move toward target
      var new_pos = [(1-tx)*current_pos[0] + tx*target_pos[0], (1-ty)*current_pos[1] + ty*target_pos[1]];
      mouseimg.style.display = "block";
      mouseimg.style.left = new_pos[0] + "px";
      mouseimg.style.top = new_pos[1] + "px";

      // Ensure mouse is in view.
      mouseimg.scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });

      // Save mouse position relative to the top of the viewport.
      sessionStorage.setItem("mouse_cursor_follower_mouse_position", new_pos[0] + "," + (new_pos[1]-$(window).scrollTop()));
    }

    // Adjust the animation duration so the mouse moves at
    // constant speed.
    // var distance = ((target_pos[0]-current_pos[0])**2 + (target_pos[1]-current_pos[1])**2)**.5;
    var distance = Math.pow((Math.pow((target_pos[0]-current_pos[0]),2) + Math.pow((target_pos[1]-current_pos[1]),2)),.5);
    // var base_distance = ($(window).width()**2 + $(window).height()**2)**.5 / 2;
    var base_distance = Math.pow(Math.pow(Math.pow($(window).width(),2) + $(window).height(),2),.5) / 2;
    animation_duration *= distance/base_distance;

    // Run an animation.
    var delay = 33;
    var steps = parseInt(animation_duration*1000/delay) + 1;
    function make_animation_frame_function(t) {
      return (function() {
        if (t > 1) t = 1; // clip
        move_cursor(t);
        if (t >= 1) {
          // no more frames
          window.moveMouseToElem_finished = true;
          return;
        }
        setTimeout(make_animation_frame_function(t+1/steps), delay);
      });
    }
    var initial_keyframe = make_animation_frame_function(0);
    initial_keyframe();
    window.moveMouseToElem_finished = false;
  }
};
