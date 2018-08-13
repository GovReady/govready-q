var widgets = {
  'interstitial': {
    initialize: function(key, qdiv, existing_answer) {
    },
    focus: function(control) {
    },
    validate_answer: function(control, spec, has_existing_answer) {
      return undefined;
    },
    value: function(control) {
      return "";
    },
    on_input_changed: function(control, handler) {
    },
    disable_input_controls: function(control, disabled) {
    },
    user_has_entered_clearable_answer: function(control) {
      return false;
    }
  },

  'text': {
    initialize: function(key, qdiv, existing_answer) {
      return qdiv.find(".inputctrl");
    },
    focus: function(control) {
      control.focus();
    },
    validate_answer: function(control, spec, has_existing_answer) {
      var val = control.val();
      if (/^ *$/.exec(val))
          return "You must enter something.";
      return undefined;
    },
    value: function(control) {
      return control.val();
    },
    on_input_changed: function(control, handler) {
      control.change(handler);
      control.on('keyup', handler);
    },
    disable_input_controls: function(control, disabled) {
      control.prop('disabled', disabled);
    },
    user_has_entered_clearable_answer: function(control) {
      // any non-whitespace character
      return /\S/.test(control.val());
    }
  },

  'date': {
    initialize: function(key, qdiv, existing_answer) {
      var date;
      if (existing_answer)
        date = [parseInt(existing_answer.slice(0, 4)), parseInt(existing_answer.slice(5, 7)), parseInt(existing_answer.slice(8, 10))];
      else
        date = [(new Date()).getFullYear(), (new Date()).getMonth()+1, (new Date()).getDate()];
      qdiv.find("select.value_year").val(date[0]);
      qdiv.find("select.value_month").val(date[1]);
      qdiv.find("select.value_day").val(date[2]);
      return qdiv;
    },
    focus: function(control) {
      control.find("select[0]").focus();
    },
    validate_answer: function(control, spec, has_existing_answer) {
      // The value is always valid, unless the user chooses February 31st,
      // but we'll let the server handle that.
      return undefined;
    },
    value: function(control) {
      // Copy the values of the selects into the hidden submission field in YYYY-MM-DD format.
      function zeropad(value, length) { value = ""+value; while (value.length < length) value = "0" + value; return value; }
      return (
        zeropad(control.find("select.value_year").val(), 4)
        + "-" +
        zeropad(control.find("select.value_month").val(), 2)
        + "-" +
        zeropad(control.find("select.value_day").val(), 2)
      );
    },
    on_input_changed: function(control, handler) {
      control.find('select').change(handler);
    },
    disable_input_controls: function(control, disabled) {
      control.find("select").prop('disabled', disabled);
    },
    user_has_entered_clearable_answer: function(control) {
      // there's no UI to clear their answer
      return false;
    }
  },

  'longtext': {
    initialize: function(key, qdiv, existing_answer) {
      return CommonMarkQuill("#question-" + key + " .inputctrl", {
        "modules": {
          "toolbar": {
            "container": "#inputctrl-quill-toolbar-" + key,
          }
        }
      });
    },
    focus: function(control) {
      control.focus();
    },
    validate_answer: function(control, spec, has_existing_answer) {
        var val = control.getContentsAsCommonMark();
        if (/^ *$/.exec(val))
            return "You must enter something."
        return undefined;
    },
    value: function(control) {
      return control.getContentsAsCommonMark();
    },
    on_input_changed: function(control, handler) {
      control.on('text-change', function(delta, oldDelta, source) {
        if (source == 'user')
          handler();
      });
    },
    disable_input_controls: function(control, disabled) {
      control.enable(!disabled);
    },
    user_has_entered_clearable_answer: function(control) {
      // any non-whitespace character
      var val = control.getContentsAsCommonMark();
      return /\S/.test(val);
    }
  },

  'choice': {
    initialize: function(key, qdiv, existing_answer) {
      return qdiv;
    },
    focus: function(control) {
      control.find('input[0]').focus();
    },
    validate_answer: function(control, spec, has_existing_answer) {
        var val = control.find('input[type="radio"]:checked').val();
        if (!val)
            return "You must make a selection."
        return undefined;
    },
    value: function(control) {
      return control.find('input:checked').val();
    },
    on_input_changed: function(control, handler) {
      control.find('input').click(handler);
    },
    disable_input_controls: function(control, disabled) {
      control.find("input[type='radio']").prop('disabled', disabled);
    },
    user_has_entered_clearable_answer: function(control) {
      // there's no UI to clear their answer
      return false;
    }
  },

  'multiple-choice': {
    initialize: function(key, qdiv, existing_answer) {
      return qdiv;
    },
    focus: function(control) {
      control.find('input[0]').focus();
    },
    validate_answer: function(control, spec, has_existing_answer) {
        // Collect the checked values.
        var vals = [];
        control.find('input[type="checkbox"]:checked').each(function() {
            vals.push($(this).val());
        });
        if (vals.length < spec.min)
            return "You must choose at least " + spec.min + " options.";
        if (spec.max && vals.length > spec.max)
            return "You must choose at most " + spec.max + " options.";
        return undefined;
    },
    value: function(control) {
      return $.makeArray(control.find('input:checked')).map(function(item) { return item.getAttribute("value"); });
    },
    on_input_changed: function(control, handler) {
      control.find('input').click(handler);
    },
    disable_input_controls: function(control, disabled) {
      control.find("input[type='checkbox']").prop('disabled', disabled);
    },
    user_has_entered_clearable_answer: function(control) {
      return control.find('input[type="checkbox"]:checked').length > 0;
    }
  },

  'file': {
    initialize: function(key, qdiv, existing_answer) {
      return qdiv.find(".inputctrl");
    },
    focus: function(control) {
      control.focus();
    },
    validate_answer: function(control, spec, has_existing_answer) {
      // There is an existing uploaded file. If the user doesn't
      // choose a new file, then Submit just keeps the old value.
      if (has_existing_answer)
        return undefined;
      if (control[0].files.length == 0)
        return "Select a file to upload.";
      return undefined;
    },
    value: function(control) {
      return control[0].files[0];
    },
    on_input_changed: function(control, handler) {
      // Add the handler to the file input control.
      control.change(handler);

      // Add the handler to the reset button, but it has to be
      // run after this event is finished to occur after the
      // form state is reset.
      //control.find('input[type=reset]').click(function() { setTimeout(handler, 0); });
    },
    disable_input_controls: function(control, disabled) {
      control.prop('disabled', disabled);
    },
    user_has_entered_clearable_answer: function(control) {
      return (control[0].files.length > 0);
    }

  }
};

widgets["password"] = widgets["text"];
widgets["email-address"] = widgets["text"];
widgets["integer"] = widgets["text"];
widgets["real"] = widgets["text"];
widgets["url"] = widgets["text"];
widgets["yesno"] = widgets["choice"];
widgets["module"] = widgets["choice"];

