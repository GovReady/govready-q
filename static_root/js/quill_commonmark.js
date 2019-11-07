// This module wraps the Quill rich text editor so that it
// allows only CommonMark-supported formating and can export
// its content as CommonMark.

function CommonMarkQuill(element, options) {
  // Default options.
  var opts = {
    // Specify a nice default theme.
    theme: 'snow',

    // Allow only formatting we can convert to CommonMark.
    formats: ['bold', 'italic', 'code', 'link', 'blockquote', 'header', 'list', 'code-block'],

    // Provide a toolbar for creating that formatting.
    modules: {
      toolbar: [['bold', 'italic', 'code'], [{ header: 1 }, { header: 2 }, { list: 'ordered' }, { list: 'bullet' }, 'blockquote', 'code-block'], ['link', 'image']]
    }
  };

  // Override with user options.
  for (var k in options)
    opts[k] = options[k];

  // Create editor.
  var quill = new Quill(element, opts);

  // Add CTRL+Enter functionality to submit the form it is contained in.
  $(element).keydown(function(e) {
    if ((e.ctrlKey || e.metaKey) && (e.keyCode == 13 || e.keyCode == 10))
      $(this).parents('form').submit();
  });

  // Add an isEmpty function.
  quill.isEmpty = function() {
    var content = this.getContents();
    var ret = true;
    content.ops.forEach(function(op) {
        if (typeof op.insert != "string" || /\S/.test(op.insert))
          ret = false;
    })
    return ret;
  }

  // Add a method to return the content as CommonMark.
  quill.getContentsAsCommonMark = function() {
    return quill_delta_to_commonmark(this);
  }

  // Return the instance.
  return quill;
}


function quill_delta_to_commonmark(quill) {
  // Render the Quill widget's content, which we can only obtain
  // in its "Delta" format, into CommonMark.

  if (quill.isEmpty())
    return "";

  var delta = quill.getContents();

  // Form the Markdown document as an array of block, where each
  // block is an array of inlines (strings).
  var md = [[ { raw: "", md: "" } ]];
  delta.ops.forEach(function(op) {
    if (typeof op.insert === "string") {
      // Text insertion.
      op.insert.split(/(\n)/).forEach(function(text) {
        var block = md[md.length-1];

        if (text != "\n") {
          var raw_text = text;

          // Escape punctuation.
          // Backslash escapes do not work in code blocks or code spans.
          // We'll handle code blocks later.
          if (!op.attributes || !op.attributes.code) {
            text = text.replace(
              /[!"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]/g,
              function(p) { return "\\" + p },
              text);
          }

          // Add text as an inline.
          if (op.attributes) {
            var inlink = false;

            if (op.attributes.link) {
              // In order to join consecutive ops with the same link target,
              // we'll insert this text in parts. If we see that we're in the
              // same link, pop the end of the link so we can continue it.
              // Do this ahead of bold/italics so that we can see if we need
              // to alernate the symbol.
              if (block[block.length-1].md == "](" + op.attributes.link + ")") {
                block.pop(); // pop and re-add after the text.
                inlink = true;
              }
            }

            // To avoid clashing emphasis markers, if the last inline
            // ended with * or _, use the other for this inline.
            var em = "*";
            if (/\*$/.test(block[block.length-1].md))
              em = "_";

            if (op.attributes.italic)
              text = em + text + em;
            if (op.attributes.bold)
              text = em + em + text + em + em;
            
            if (op.attributes.code)
              text = "`" + text + "`";

            if (op.attributes.link) {
              if (!inlink)
                block.push({ raw: "", md: "[" });
              block.push({ raw: raw_text, md: text });
              block.push({ raw: "", md: "](" + op.attributes.link + ")" });
              return;
            }
          }

          block.push({ raw: raw_text, md: text });

        } else {
          // This is a newline. Apply block-level attributes to the
          // current block, then start a new block.
          if (op.attributes) {
            if (op.attributes.header) {
              var h = "";
              for (var i = 0; i < op.attributes.header; i++)
                h += "#";
              block.unshift({ raw: "", md: h + " "});
            } else if (op.attributes.list == "ordered") {
              block.unshift({ raw: "", md: "1. "});
            } else if (op.attributes.list == "bullet") {
              block.unshift({ raw: "", md: "* "});
            } else if (op.attributes.blockquote) {
              block.unshift({ raw: "", md: "> "});
            } else if ("code-block" in op.attributes) {
              // Use only raw text in code blocks - no markdown formatting.
              block.forEach(function(inline) { inline.md = inline.raw; });
              block.unshift({ raw: "", md: "    "});
            }
          }
          md.push([{ raw: "", md: "" }]);
        }
      });

    } else if (op.insert.image) {
      // This holds a URL or data URI. We'll convert the data URI
      // to an attachment + a safe URI on the server side, since data URIs
      // are not safe in CommonMark.
      var block = md[md.length-1];
      block.push({ raw: "", md: "![](" + op.insert.image + ")"})
    }
  });
  return md.map(function(block) { return block.map(function(inline) { return inline.md }).join(""); }).join("\n\n");
}
