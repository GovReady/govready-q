id: pia_retention
format: html
title: PIA Retention
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
  <h2>Section 5.0 Data Retention</h2>
</div>

<div class="dos-pta-form">

  <h2>5.1 Length and Reason for Retention</h2>
  <div class="cell-full">
    <p>{{project.pia_retention.q1}}</p>
  </div>

  <h2>5.2 Related to Retention</h2>
  <div class="cell-full">
    <p>{{project.pia_retention.q2}}</p>
  </div>
 
</div>
