id: pia_notice
format: html
title: PIA Notice
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
  <h2>Section 4.0 Notice</h2>
</div>

<div class="dos-pta-form">

  <h2>4.1 Notice Before Collection</h2>
  <div class="cell-full">
    <p>{{project.pia_notice.q1}}</p>
  </div>

  <h2>4.2 User Consent</h2>
  <div class="cell-full">
    <p>{{project.pia_notice.q2}}</p>
  </div>


  <h2>4.3 Related to Notice</h2>
  <div class="cell-full">
    <p>{{project.pia_info_usage.q3}}</p>
  </div>
 
</div>
