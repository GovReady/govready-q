id: mou_printable
format: markdown
title: Memorandum of Understanding
...
<style type="text/css" scoped>
    h2 { border-bottom:0px solid #888; margin-top: 3em; color: black;}
    h3 { border-bottom: 0.5px solid #aaa; color: #777; font-size: 14pt; font-weight: bold;}
    h4 { margin-top: 15px; font-weight: bold; font-size: 1em; }
    blockquote { color: #666; font-size:0.8em; margin: 0 10px; }
    .notice {color: red; font-size:3.0em; text-align:center; transform: scaleY(.85);
    font-weight: bold;}
    table { border: none; border-collapse: collapse; }
    th, td { border: 1px solid #888; padding: 15px; text-align: left;}
    @media all {
        .page-break     { display: none; }

    .soft {
      color: #aaa;
    }

    table {border: 0px solid #CCC;
    border-collapse: collapse;}

    td {border: none;}

    @media print {
        h1.title {
            /* v-center, need absolute */
            position: absolute; /* repeats once */
            bottom: 50%;
            /* h-center, for element with absolute positioning */
            left: 0;
            right: 0;
            margin-left: 20%;
            margin-right: 20%;
        }
        .footer {
            position: fixed; /* repeats on every page */
            bottom: 0;
        }
        table.footer {
            width: 95%;
            display: table;
        }
        table.footer td {
            border: none;
            padding: 0px;
            padding-bottom: .1em;
        }
        .page-break { display: block; page-break-after: always; }
    }
</style>

<!-- Cover page -->
<center>
FOR OFFICIAL USE ONLY

<br></br><br></br>

<center>

<h1 class="title">Memorandum of Understanding<br/><br></br>Between {{project.system_info.system_org}} and {{project.mou_intro.q3}}</h1>
</center>

<br></br><br></br><br></br><br></br>
**DATE:
{{project.mou_end.q8}}**
<br></br>
<table>
  <tr>
    <td style="text-align:center">{{project.system_info.system_name}}</td>
    <td></td>
    <td style="text-align:center">{{project.mou_intro.q2}}</td>
  </tr>
  <tr>
    <td style="text-align:center">{{project.system_info.system_org}} </td>
    <td></td>
    <td style="text-align:center">{{project.mou_intro.q3}}</td>
  </tr>
</table>

<br></br>

FOR OFFICIAL USE ONLY




<div style="height: 400px;">
  <!-- Spacer for cover page -->
</div>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

</center>
<center>
FOR OFFICIAL USE ONLY
<br></br>
Memorandum of Understanding
</center>

<h2>SUPERSEDES:</h2>
{% if project.mou_intro.q9 == 'no' %} NONE {% endif %}
{% if project.mou_intro.q9 == 'yes' %} {{project.mou_intro.q10}} {% endif %}

<h2>INTRODUCTION</h2>
The purpose of this memorandum is to establish a management agreement between
{{project.system_info.system_org}} and {{project.mou_intro.q3}} regarding the development, management, operation, and security of a connection between {{project.system_info.system_name}}, owned by {{project.system_info.system_org}}, and {{project.mou_intro.q2}}, owned by {{project.mou_intro.q3}}. This agreement will govern the
relationship between {{project.system_info.system_org}} and {{project.mou_intro.q3}}, including designated
managerial and technical staff, in the absence of a common management authority. 

<h2>AUTHORITY</h2>
{{project.mou_intro.q7}}

<h2>BACKGROUND</h2>
{{project.mou_intro.q8}}
<br></br>
<strong>SYSTEM A</strong>
- {{project.system_info.system_name}}
- {{project.system_info.system_description}}
- {{project.system_info.system_hosting}}
- {{project.system_info.system_data}}

<strong>SYSTEM B</strong>
- {{project.mou_intro.q2}}
- {{project.mou_intro.q4}}
- {{project.mou_intro.q5}}
- {{project.mou_intro.q6}}

<h2>COMMUNICATIONS</h2>
{{project.mou_core.q2}}
- <strong>Security Incidents:</strong>{{project.mou_core.q3}}
- <strong>Disasters and Other Contingencies:</strong>{{project.mou_core.q4}}
- <strong>Material Changes to System Configuration:</strong>{{project.mou_core.q5}}
- <strong>New Interconnections:</strong>{{project.mou_core.q6}}
- <strong>Personnel Changes:</strong>{{project.mou_core.q7}}

<h2>INTERCONNECTION SECURITY AGREEMENT</h2>
{{project.mou_end.q2}}

<h2>SECURITY</h2>
{{project.mou_end.q3}}

<h2>COST CONSIDERATIONS</h2>
{{project.mou_end.q4}}

<h2>TIMELINE</h2>
{{project.mou_end.q5}}

<h2>SIGNATORY AUTHORITY</h2>
I agree to the terms of this Memorandum of Understanding.

<table align="center" >
  <tr>
    <td style="text-align:center" colspan="2">{{project.mou_end.q6}}, {{project.system_info.system_org}}</td>
  </tr>
  <tr>
    <td style="text-align:center"><input type="textfield"/><br />Signature</td>
    <td style="text-align:center"><input type="textfield"/><br />Date</td>
  </tr>
</table>

<br></br>

<table align="center" >
  <tr>
    <td style="text-align:center"colspan="2">{{project.mou_end.q7}}, {{project.mou_intro.q3}}</td>
  </tr>
  <tr>
    <td style="text-align:center"><input type="textfield"/><br />Signature</td>
    <td style="text-align:center"><input type="textfield"/><br />Date</td>
  </tr>
</table>




