id: ptr_purpose_01
title: Purpose 1
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

  <h2>1. The purpose of this information collection is:</h2>

  <div class="cell-full">
    a. Describe the purpose of the information collection or form. <i>Please provide a general description of the project and its purpose, including how it supports the DOS mission, in a way a non-technical person could understand (you may use information from the Supporting Statement).</i>
    <div style="margin-left: -18px;">
    <i>If this is an updated PTA, please specifically describe what changes or upgrades are triggering the update to this PTA.</i>
    </div>
  </div>
  <div class="cell-full">
    {{ collection_purpose|safe }}
  </div>

  <div class="cell-full">
    b. List the DOS (or component) authorities to collect, store, and use this information. <i>If this information will be stored and used by a specific DOS component, list the component-specific authorities.</i>
  </div>
  <div class="cell-full">
    {% if statutes_agency_policies == "yes" %}
    <pre style="background-color: white; border: 0px solid black; font-family: TimesNewRoman, Times, serif;">{{statutes_agency_policies_list}}</pre>
    {% endif %}
    {% if component_policies == "yes" %}
    <pre style="background-color: white; border: 0px solid black; font-family: TimesNewRoman, Times, serif;">{{component_policies_list}}</pre>
    {% endif %}
  </div>

</div>
