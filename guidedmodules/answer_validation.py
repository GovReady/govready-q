class question_input_parser:
    # Turns client-side input into the correct JSON-serializable
    # Python data structure for a particular question type.
    #
    # The input is typically a string submitted by an <input> field,
    # which is passed to this function by request.POST.getlist(),
    # giving us an array of strings.
    #
    # But file-type questions are given by request.FILES.get(), which
    # gives a Django UploadedFile instance.
    #
    # The output of the parse function is a JSON-serializable data
    # structure that matches the structure that export_json/import_json
    # functions use, because that's the format that the validator
    # functions expect since the validator is used both for web input
    # and imported input.
    @classmethod
    def parse(_class, question, value):
        # Mangle value a bit.
        if question.spec["type"] == "multiple-choice" or question.spec["type"] == "multiple-choice-from-data":
            # A list of strings is what we want here.
            pass

        elif question.spec["type"] == "datagrid":
            # A list of strings is what we want here.
            pass

        elif question.spec["type"] == "file":
            # An UploadedFile instance is what we want here.
            pass

        else:
            # For all other question types, turn the array of strings
            # into a single string.
            if len(value) > 1:
                raise ValueError("Invalid input: Multiple values submitted.")
            elif len(value) == 0:
                raise ValueError("Invalid input: No value submitted.")
            else:
                value = value[0].strip()

        # Get the parser function and run it on the value.
        func = getattr(_class, "parse_" + question.spec["type"].replace("-", "_"))
        return func(question, value)

    # The textual question types don't need to be parsed. They come
    # as strings and are stored as strings.
    def parse_text(question, value):
        return value
    def parse_password(question, value):
        return value
    def parse_email_address(question, value):
        return value
    def parse_url(question, value):
        return value
    def parse_longtext(question, value):
        return value
    def parse_date(question, value):
        return value

    # Likewise for the simple choice types.
    def parse_choice(question, value):
        return value
    def parse_choice_from_data(question, value):
        return value
    def parse_yesno(question, value):
        return value

    def parse_multiple_choice(question, value):
        # Comes in from the view function as an array of strings, which is what we want.
        return value

    def parse_multiple_choice_from_data(question, value):
        # Comes in from the view function as an array of strings, which is what we want.
        return value

    def parse_datagrid(question, value):
        # Comes in from the view function as an array of strings, which is what we want.
        return value

    def parse_integer(question, value):
        # First parse it as a real using localization.
        value = question_input_parser.parse_real(question, value)

        # Then ensure is an integer.
        if value != int(value):
            raise ValueError("Invalid input. Must be a whole number.")

        # Finally, convert data type.
        return int(value)

    def parse_real(question, value):
        try:
            # Use a locale to parse human input since it may have
            # e.g. thousands-commas. The locale is set on app
            # startup using locale.setlocale in settings.py.
            import locale
            return locale.atof(value)
        except ValueError:
            # make a nicer error message
            raise ValueError("Invalid input. Must be a number.")

    def parse_file(question, value):
        # This comes in as a Django File instance. Convert it to the
        # data structure used for export/import.

        # Otherwise, we get an UploadedFile instance.
        import django.core.files.uploadedfile
        if not isinstance(value, django.core.files.uploadedfile.UploadedFile):
            raise ValueError("Invalid data type.")

        # Pull the whole file into memory and return the JSON data structure.
        # Encode the content as an array of (short) base-64 strings.
        # TODO: Maybe check value.charset and do transcoding to utf-8?
        import re
        from base64 import b64encode
        return {
            "content": re.findall(".{1,64}", b64encode(value.open().read()).decode("ascii")),
            "type": value.content_type, # as given by the client
        }

    def parse_module(question, value):
        # handled by view function
        return value

    def parse_interstitial(question, value):
        # interstitials have no actual answer - we should always
        # get "" - and the internal value is always None.
        if value != "":
            raise ValueError("Invalid input.")
        return None


class validator:
    # Validate that an answer is of the right data type and meets the
    # criteria of a question, and returns a normalized value.
    @classmethod
    def validate(_class, question, value):
        validate_func = getattr(_class, "validate_" + question.spec["type"].replace("-", "_"))
        return validate_func(question, value)

    def validate_text(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value).__name__)
        value = value.strip()
        if value == "":
            raise ValueError("Value is empty.")
        return value

    def validate_password(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)
        return value

    def validate_email_address(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)

        # Then validate and normalize the value as an email address.
        # When we're running tests, skip DNS-based deliverability checks
        # so that tests can be run in a completely offline mode. Otherwise
        # dns.resolver.NoNameservers will result in EmailUndeliverableError.
        import email_validator
        from django.conf import settings
        info = email_validator.validate_email(value, check_deliverability=settings.VALIDATE_EMAIL_DELIVERABILITY)
        return info["email"]

    def validate_url(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)

        # Then validate and normalize the URL.
        from django.core.validators import URLValidator
        urlvalidator = URLValidator()
        try:
            urlvalidator(value)
        except:
            raise ValueError("That is not a valid web address.")
        return value

    def validate_longtext(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)
        return value

    def validate_date(question, value):
        # Run the same checks as text (data type is str, stripped, and is not empty).
        value = validator.validate_text(question, value)

        # Validate that we have a valid date in YYYY-MM-DD format. A client-side
        # tool should be responsible for ensuring that the user entry is translated
        # into this format.
        import re, datetime
        m = re.match("(\d\d\d\d)-(\d\d)-(\d\d)$", value)
        if not m:
            raise ValueError("Date is not in YYYY-MM-DD format.")

        # Convert to ints, raising ValueError if they are not.
        try:
            year, month, date = [int(x) for x in m.groups()]
        except ValueError:
            raise ValueError("Date is not in YYYY-MM-DD format.")

        # Instantiate a datetime.date object. It will raise a ValueError if the
        # year, month, or day is out of range.
        datetime.date(year, month, date)

        # Return the original string (not a datetime instance).
        return value

    def validate_choice(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value))
        if value not in { choice['key'] for choice in question.spec["choices"] }:
            raise ValueError("invalid choice")
        return value

    def validate_choice_from_data(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value))
        # TODO: Check against generated data?
        # if value not in { choice['key'] for choice in question.spec["choices"] }:
        #     raise ValueError("invalid choice")
        return value

    def validate_yesno(question, value):
        if not isinstance(value, str):
            raise ValueError("Invalid data type (%s)." % type(value))
        if value not in ("yes", "no"):
            raise ValueError("invalid choice")
        return value

    def validate_multiple_choice(question, value):
        if not isinstance(value, list):
            raise ValueError("Invalid data type (%s)." % type(value))
        for item in value:
            if item not in { choice['key'] for choice in question.spec["choices"] }:
                raise ValueError("invalid choice: " + item)
        if len(value) < question.spec.get("min", 0):
            raise ValueError("not enough choices")
        if question.spec.get("max") and len(value) > question.spec["max"]:
            raise ValueError("too many choices")
        return value

    def validate_multiple_choice_from_data(question, value):
        if not isinstance(value, list):
            raise ValueError("Invalid data type (%s)." % type(value))
        # TODO: Check against generated data?
        # for item in value:
        #     if item not in { choice['key'] for choice in question.spec["choices"] }:
        #         raise ValueError("invalid choice: " + item)
        if len(value) < question.spec.get("min", 0):
            raise ValueError("not enough choices")
        if question.spec.get("max") and len(value) > question.spec["max"]:
            raise ValueError("too many choices")
        return value

    def validate_datagrid(question, value):
        # print("datagrid question: {}".format(question))
        # print("datagrid value: {}".format(value))
        # De-stringify object
        import ast
        value = ast.literal_eval(value[0])
        if not isinstance(value, list):
            raise ValueError("Invalid data type (%s)." % type(value))
        if len(value) < question.spec.get("min", 0):
            raise ValueError("not enough rows")
        if question.spec.get("max") and len(value) > question.spec["max"]:
            raise ValueError("too many rows")
        return value

    def validate_integer(question, value):
        if not isinstance(value, int):
            raise ValueError("Invalid data type (%s)." % type(value))
        value = validator._validate_number(question, value)
        return value

    def validate_real(question, value):
        if not isinstance(value, float):
            raise ValueError("Invalid data type (%s)." % type(value))
        value = validator._validate_number(question, value)
        return value

    @staticmethod
    def _validate_number(question, value):
        # This method is used on ints and floats.
        if "min" in question.spec and value < question.spec["min"]:
            raise ValueError("Must be at least %g." % question.spec["min"])
        if "max" in question.spec and value > question.spec["max"]:
            raise ValueError("Must be at most %g." % question.spec["max"])
        return value

    def validate_file(question, value):
        # The JSON-serializable data structure for a file is a dict like:
        #
        # {
        #   "content": [ array of Base64-encoded strings ],
        #   "contentType": "text/plain",
        # }
        #
        # Turn this into a Django ContentFile instance which is how we'll
        # save it into the database.

        # Check data type.
        if not isinstance(value, dict):
            raise ValueError("Invalid data type (%s)." % type(value))
        if not isinstance(value.get("content"), list):
            raise ValueError("Invalid data type.")
        if not isinstance(value.get("type"), str):
            raise ValueError("Invalid data type.")

        # Fetch content.
        from base64 import b64decode
        content = b64decode("".join(chunk for chunk in value["content"]).encode("ascii"))

        # The file must have content.
        if len(content) == 0:
            raise ValueError("File is empty.")

        # If the "file-type" field is set and it's set to "image", then
        # load the file using Pillow to ensre it actually is a valid image.
        # Also sanitize it by round-tripping it through Pillow.
        # This purposefully is intended to lose image metadata, to protect
        # the user. (TODO: Test that it actually drops XMP metadata.)
        if question.spec.get("file-type") == "image":
            # Load the image.
            from io import BytesIO
            from PIL import Image
            try:
                im = Image.open(BytesIO(content))
                im.load() # force read from buffer so that exceptions are raised now
            except:
                raise ValueError("That's not an image file.")

            imspec = question.spec.get("image", {})
            
            # Apply a size constraint and resize the image in-place.
            if imspec.get("max-size"):
                # TODO: Validate the size width/height fields are integers.
                size = imspec["max-size"]
                im.thumbnail(( size.get("width", im.size[0]), size.get("width", im.size[1])  ))

            # Write the image back to a new buffer.
            buf = BytesIO()
            im.save(buf, "PNG")
            content = buf.getvalue()

        # Turn it into a Django ContentFile instance.
        from django.core.files.base import ContentFile
        value = ContentFile(content)
        value.name = "unknown.dat" # needs a name for the storage backend?
        return value

    def validate_module(question, value):
        # handled by caller function
        return value

    def validate_module_set(question, value):
        # handled by caller function
        return value

    def validate_interstitial(question, value):
        # interstitials have no actual answer - we should always
        # store None.
        if value is not None:
            raise ValueError("Invalid data type (%s)." % type(value))
        return value

