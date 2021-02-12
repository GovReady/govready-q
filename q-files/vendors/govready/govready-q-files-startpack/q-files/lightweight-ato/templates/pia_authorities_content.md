id: pia_authorities_content
format: html
title: PIA Authorities and Content
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
  <h2>Section 1.0 Authorities and Other Requirements</h2>
</div>

<div class="dos-pta-form">

  <h2>1.1 Specific Legal Authorities</h2>
  <div class="cell-full">
    <p>{{project.pia_authorities.q1}}
  </div>

  <h2>1.2 Applicable SORNs</h2>
  <div class="cell-full">
    <p>{{project.pia_authorities.q2}}
  </div>

  <h2>1.3 System Security Plan Information</h2>
  <div class="cell-full">
    <p>{{project.pia_authorities.q3}}
  </div>

  <h2>1.4 Records Retention Scheulde</h2>
  <div class="cell-full">
    <p>{{project.pia_authorities.q4}}
  </div>

  <h2>1.5 OMB Control Number</h2>
  <div class="cell-full">
    <p>{{project.pia_authorities.q5}}
  </div>

 
</div>

<br>