id: poc_details
title: Cover page
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

<div style="font-weight: bold;">
<p style="text-align: center;">
  Privacy Threshold Analysis (PTA)
</p>

<p style="text-align: center;">
  Specialized Template for<br/>
  Information Collections (IC) and Forms
</p>
</div>

<div style="text-indent: 3em;">
<p>
  The Forms-PTA is a specialized template for Information Collections and Forms. This specialized PTA must accompany all Information Collections submitted as part of the Paperwork Reduction Act process (any instrument for collection (form, survey, questionnaire, etc.) from ten or more members of the public). Components may use this PTA to assess internal, component-specific forms as well.
</p>

</div>

<div style="font-weight: bold; text-align: center;">
  PROJECT OR PROGRAM MANAGER
</div>

<div style="padding:0px; border-top: 1px solid rgb(89, 129, 187);">
  <div style="padding: 4px 8px 4px 8px; font-weight: bold;">
    Name: {{ poc_name }}
  </div>

  <div style="background-color: rgb(211, 223, 237); border-top: 1px solid rgb(89, 129, 187); padding: 4px 8px 4px 8px;">
    <div style="display: inline-block; width: 140px; font-weight: bold">Office:</div>
    <div style="display: inline-block; width: 140px;">{{ poc_office }}</div>
    <div style="display: inline-block; width: 140px; font-weight: bold">Title:</div>
    <div style="display: inline-block; width: 140px;">{{ poc_title }}</div>
  </div>

  <div style="border-top: 1px solid rgb(89, 129, 187); padding: 4px 8px 4px 8px;">
    <div style="display: inline-block; width: 140px; font-weight: bold">Phone:</div>
    <div style="display: inline-block; width: 140px;">{{ poc_phone }}</div>
    <div style="display: inline-block; width: 140px; font-weight: bold">Email:</div>
    <div style="display: inline-block; width: 140px;">{{ poc_email }}</div>
  </div>


</div>
