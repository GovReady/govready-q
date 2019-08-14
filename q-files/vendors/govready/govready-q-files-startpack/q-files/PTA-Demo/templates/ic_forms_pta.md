id: ic_forms_pta
title: IC / Form Description
format: html
...

<style>
  .dos-pta-form {
    font-family: TimesNewRoman, Times, serif;
    width: 650px;
    margin: auto;
  }

  .dos-pta-form h2 {
    font-size: 12pt;
    font-family: TimesNewRoman, Times, serif;
    background-color: rgb(89, 129, 187);
    padding: 4px 30px 4px 30px;
    color: white;
    font-weight: bold;
    margin: 0px 0px 0px 0px;
    margin-top: 2em;
  }

  .dos-pta-form .cell-full {
    border-left: 1px solid rgb(89, 129, 187);
    border-right: 1px solid rgb(89, 129, 187);
    border-bottom: 1px solid rgb(89, 129, 187);padding: 4px 30px 4px 30px;
    font-family: TimesNewRoman, Times, serif;
  }

  .dos-pta-form .cell-left {
    border-left: 1px solid rgb(89, 129, 187);
    border-bottom: 1px solid rgb(89, 129, 187);
    padding: 4px 30px 4px 30px;
    width: 49.5%;
    display: table-cell;
    height: 100%;
  }

  .dos-pta-form .cell-right {
    border-left: 1px solid rgb(89, 129, 187);
    border-right: 1px solid rgb(89, 129, 187);
    border-bottom: 1px solid rgb(89, 129, 187);
    padding: 4px 30px 4px 30px;
    width: 49.5%;
    display: table-cell;
    height: 100%;
    vertical-align: top;
  }

</style>

<div class="dos-pta-form">

  <h2>1. Purpose of the Information Collection or Form</h2>
  <div class="cell-full">
    a. Describe the purpose of the information collection or form. <i>Please provide a general description of the project and its purpose, including how it supports the DOS mission, in a way a non-technical person could understand (you may use information from the Supporting Statement).</i>
    <div style="margin-left: -18px;">
    <i>If this is an updated PTA, please specifically describe what changes or upgrades are triggering the update to this PTA.</i>
    </div>
  </div>
  <div class="cell-full">
    {{ q1a|safe }}
  </div>
  <div class="cell-full">
    b. List the DOS (or component) authorities to collect, store, and use this information. <i>If this information will be stored and used by a specific DOS component, list the component-specific authorities.</i>
  </div>
  <div class="cell-full">
    <pre style="background-color: white; border: 0px solid black; font-family: TimesNewRoman, Times, serif;">{{ q1b }}</pre>
  </div>

  <h2>2. Describe the IC/Form</h2>
  <div class="cell-left">
   a. Does this form collect any "Personally Identifiable Information" (PII)?
  </div>
  <div class="cell-right">
    {{ q2a }}
  </div>

  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
   b. From which type(s) of individuals does this form collect information? <i>(Check all that apply.)</i>
  </div>
  <div class="cell-right">
    <ul>
      {% for item in q2b %}
      <li>
        {{ item.text }}
      </li>
      {% endfor %}
    </ul>
  </div>

  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
   c. Who will complete and submit this form? <i>(Check all that apply.)</i>
  </div>
  <div class="cell-right">
    <ul>
      {% for item in q2c %}
      <li>
        {{ item.text }}
        {% if item == "businessentity" %}<div style="display:inline;margin-left:5em;">If a business entity, is the only information collected business contact information?<br/>{{ q2c_businesscontactinformation }}</div>{% endif %}
        {% if item == "other" %} - {{ q2c_other }}{% endif %}
      </li>
      {% endfor %}
    </ul>
  </div>

  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
   How do individuals complete the form? <i>(Check all that apply.)</i>
  </div>
  <div class="cell-right">
    <ul>
      {% for item in q2d %}
      <li>
        {{ item.text }}
        {% if item == "webform" %} - {{ q2d_link }}{% endif %}
      </li>
      {% endfor %}
    </ul>
  </div>

  <div class="cell-full">
   e. What information will DOS collect on the form? <i>List all PII data elements on the form. If the form will collect information from more than one type of individual, please break down list of data elements collected by type of individual.</i>
  </div>
  <div class="cell-full">
    {{ q2e }}
  </div>

  <div class="cell-full">
    f. Does this form collect Social Security number (SSN) or other element that is stand-alone Sensitive Personally Identifiable Information (SPII)? <i>Check all that apply.</i>
  </div>
  <div class="cell-full">
    <ul>
      {% for item in q2f %}
      <li>
        {{ item.text }}
        {% if item == "other" %} <i>Please list</i>: {{ q2f_other }}{% endif %}
      </li>
      {% endfor %}
    </ul>
  </div>

  <div class="cell-full">
    g. List the <b><i>specific authority</i></b> to collect SSN or these other SPII elements.
  </div>
  <div class="cell-full">
    {{ q2g }}
  </div>

  <div class="cell-full">
    h. How will this information be used? What is the purpose of the collection? Describe <b><i>why</i></b> this collection of SPII is the minimum amount of information necessary to accomplish the purpose of the program.
  </div>
  <div class="cell-full">
    {{ q2h }}
  </div>

  <div class="cell-full">
    i. Are individuals provided notice at the time of collection by DOS?<i>(Does the records subject have notice of the collection or is form filled out by third party?)</i>
  </div>
  <div class="cell-full">
    {{ q2i }}{% if q2i == "yes" %} <i>Please describe how notices is provided.</i>: {{ q2i_describe }}{% endif %}
  </div>

</div>
