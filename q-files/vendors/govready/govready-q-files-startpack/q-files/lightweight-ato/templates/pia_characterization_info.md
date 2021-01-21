id: pia_characterization_info
format: html
title: PIA Characterization of Information
...

<style>

  h2 {
    font-family: TimesNewRoman, Times, serif;
    display: block;
    font-size: 16pt;
    font-weight: bold;
    text-decoration: none;
  }

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

<div>
  <h2>Section 2.0 Characterization of the Information</h2>
</div>

<div class="dos-pta-form">

  <h2>2.1.a Information Identification</h2>
  <div class="cell-full">
    <p>{{project.pia_info_characterization.q1}}</p>
  </div>

  <h2>2.1.b New Information Description</h2>
  <div class="cell-full">
    {% if project.pia_info_characterization.q2 == 'yes' %}
    {{project.pia_info_characterization.information_created}}
    {% elif project.pia_info_characterization.q2 == 'no' %} N/A
    {% endif %}
  </div>

  <h2>2.1.c Information from Other Systems</h2>
  <div class="cell-full">
    {% if project.pia_info_characterization.q3 == 'yes' %}
    {{project.pia_info_characterization.information_connected}}
    {% elif project.pia_info_characterization.q3 == 'no' %} N/A
    {% endif %}
  </div>

  <h2>2.2 Information Sources</h2>
  <div class="cell-full">
    <p>{{project.pia_info_characterization.q4}}</p>
  </div>

  <h2>2.3 Commercial and Public Information</h2>
  <div class="cell-full">
    {% if project.pia_info_characterization.q5 == 'yes' %}
    {{project.pia_info_characterization.commercial_public_info}}
    {% elif project.pia_info_characterization.q5 == 'no' %} N/A
    {% endif %}
  </div>

  <h2>2.4 Information Accuracy</h2>
  <div class="cell-full">
    <p>{{project.pia_info_characterization.q6}}</p>
  </div>

  <h2>2.5 Characterization of Information</h2>
  <div class="cell-full">
    <p>{{project.pia_info_characterization.q8}}</p>
    <p>{{project.pia_info_characterization.q9}}</p>
    <p>{{project.pia_info_characterization.q10}}</p>
    <p>{{project.pia_info_characterization.q11}}</p>
  </div>

 
</div>
