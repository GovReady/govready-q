id: rtm_report.md
format: markdown
title: RTM Report
...

<style type="text/css" scoped>
    h2 { border-bottom:1px solid #888; margin-top: 3em; color: red;}
    h3 { border-bottom: 0.5px solid #aaa; color: #777; font-size: 14pt; font-weight: bold;}
    h4 { margin-top: 15px; font-weight: bold; font-size: 1em; }
    blockquote { color: #666; font-size:0.8em; margin: 0 10px; }
    .notice {color: red; font-size:3.0em; text-align:center; transform: scaleY(.85);
    font-weight: bold;}
    table { border: none; border-collapse: collapse; }
    th, td { border: 1px solid #888; padding: 15px; text-align: left;}
    @media all {
        .page-break     { display: none; }
    }
    .table-caption {
      color: red;
      text-align: center;
      font-style: italic;
      margin: 1em; 0 0.33em; 0;
    }
    table.table-ssp {
      margin-bottom: 1.0em;
      width: 100%;
    }
    table.table-ssp th, table.table-ssp td {
      padding: 4px;
    }
    td.td-header, th.th-header {
      color: white;
      background-color: rgb(31, 58, 105);
      text-align:center;
      font-weight: bold;
    }
    td.td-c-name-part, td.td-row-title {
      width: 125px;
      background-color: rgb(219, 228, 244);
      font-weight: bold;
      padding-left: 12px;
    }
    table.table-ssp td {
      padding-left: 12px;
    }
    .soft {
      color: #aaa;
    }
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

<center>
<h1 class="title">{{project.system_info.system_name}}<br/>Requirements Traceability Matrix<br/>(RTM) Report</h1>
<img style="max-width:70%;height:auto;" src="{{static_asset_path_for('app.png')}}">
<br></br>
<h1>Prepared for</br/>{{project.system_info.system_org}}</h1>
<br></br>
{{project.rtm_doc.rtm_date}}
</center>




* * *

## Table of Contents

*   [1. RTM](#rtm)
    *   [1.1 Introduction](#introduction)
    *   [1.2 Plan of Action and Milestone Table](#rtmtable)

* * *

## 1. RTM
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1.1 Introduction
The Requirements Traceability Matrix (RTM) relates requirements from requirement source documents to the security certification process. It ensures that all security requirements are identified and investigated. Each row of the matrix identifies a specific requirement and provides the details of how it was tested or analyzed and the results.

The table is arranged to display the system security requirements from the applicable regulation documents, which are listed below:

* NIST 800-53 w/ DHS 4300A - Department of Homeland Security Sensitive Systems Policy Directive 4300A Version 10

The descriptions of the RTM are defined as follows:

<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}
</style>
<table class="tg">
  <tr>
    <th class="tg-0pky">RTM Column</th>
    <th class="tg-0pky">Column Description</th>
  </tr>
  <tr>
    <td class="tg-0pky">Control Ref.</td>
    <td class="tg-0pky">Refers to the name (short title) of the source document and the ID or paragraph number of the listed control or requirement.</td>
  </tr>
  <tr>
    <td class="tg-0pky">Security Req./Control</td>
    <td class="tg-0pky">Short title describing the security control or requirement (and the text of the control/requirement, which may be paraphrased for brevity).</td>
  </tr>
  <tr>
    <td class="tg-0pky">Security Category</td>
    <td class="tg-0pky">Category and class associated with the security control.</td>
  </tr>
  <tr>
    <td class="tg-0pky">Control Type</td>
    <td class="tg-0pky">Auto populated if the requirement is identified with two security control types: common and system-specific; i.e., a part of the requirement is identified as common type and another part of it is system-specific.<br><br><li>Common. Auto populated if the requirement is designated to one or more information systems.</li><li>Hybrid. Auto populated if the requirement is identified with two security control types: common and system-specific; i.e., a part of the requirement is identified as common type and another part of it is system-specific.</li><li>System-Specific. Auto populated if the requirement is assigned to a specific information system.</li><li>Inherited. Auto populated if the requirement is inherited from another system.</li><li>Not Specified. Auto populated if the requirement does not require any security control.</li></td>
  </tr>
  <tr>
    <td class="tg-0pky">Planned Imp.</td>
    <td class="tg-0pky">Auto populated if the requirement is identified with two security control types: common and system-specific; i.e., a part of the requirement is identified as common type and another part of it is system-specific.<br><br><li>Common. Auto populated if the requirement is designated to one or more information systems.</li><li>Hybrid. Auto populated if the requirement is identified with two security control types: common and system-specific; i.e., a part of the requirement is identified as common type and another part of it is system-specific.</li><li>System-Specific. Auto populated if the requirement is assigned to a specific information system.</li><li>Inherited. Auto populated if the requirement is inherited from another system.</li><li>Not Specified. Auto populated if the requirement does not require any security control.</li></td>
  </tr>
  <tr>
    <td class="tg-0pky">Actual Imp.</td>
    <td class="tg-0pky">Identification whether the control is in place and how it has been implemented, or differences in how the control was implemented compared to what was planned.<br><br><li>As Planned. Auto populated if Implemented control status is selected and Planned Implementation column does not read Not Entered.</li><li>Pending Implementation. Auto populated if Planned control status is selected and Planned Implementation column does not read Not Entered.</li><li>Partially Implemented. Auto populated if Partial control status is selected and Planned Implementation column does not read Not Entered.</li><li>Not Entered. Auto populated if the Planned Implementation column reads Not Entered.</li><li>Not Assigned. Auto populated if the Control Type and/or Control Status were not selected.</li></td>
  </tr>
  <tr>
    <td class="tg-0pky">Test #(s)</td>
    <td class="tg-0pky">The ID number of the specific test procedure(s) that is used to validate the requirement or control.<br>The control is not applicable.</td>
  </tr>
  <tr>
    <td class="tg-0pky">Methods</td>
    <td class="tg-0pky">The evaluation method (or methods) used to assess the requirement.<li>I. Interview.</li><li>E. Examine.</li><li>T. Testing.</li><li>The control is not applicable.</li></td>
  </tr>
  <tr>
    <td class="tg-0pky">Tailored</td>
    <td class="tg-0pky">The tailored control that modifies the control set.<li>In. The control was tailored in.</li><li>Out. The control was tailored out.</li><br>The control was not affected from tailoring.</td>
  </tr>
  <tr>
    <td class="tg-0pky">Overlays</td>
    <td class="tg-0pky">The controls included or excluded from the controls already in the baseline.<li>In. The control was added in to the controls in the baseline.</li><li>Out. The control was removed from the controls in the baseline.</li><br>The control was not affected from overlay(s).</td>
  </tr>
  <tr>
    <td class="tg-0pky">Result</td>
    <td class="tg-0pky">The summarized result for the test procedures that cover the requirement/control.<li>Met - Requirement fully satisfied.</li><li>Not Met - Requirement not satisfied.</li><li>Not Applicable - Requirement not applicable.</li></td>
  </tr>
  <tr>
    <td class="tg-0pky">Notes</td>
    <td class="tg-0pky">Identifies the factor, and the basis for; any tailoring of controls from the NIST 800-53 w/ DHS 4300A baseline or organizational overlay that was used for the system.</td>
  </tr>
</table>



<br></br>

### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1.2 Requirement Traceability Matrix Table

{% set meta = {"current_family": "", "current_control": "", "current_control_part": ""} %}
{% for ctl in ["AC_11_a_1", "AC_11_a_2", "AC_23_1", "AC_23_2", "AC_23_3", "AC_2_a_1", "AC_2_a_2", "AC_2_b", "AC_2_c", "AC_2_d_1", "AC_2_d_2", "AC_2_d_3", "AC_2_d_4", "AC_2_e_1", "AC_2_e_2", "AC_2_f_1_a", "AC_2_f_1_b", "AC_2_f_1_c", "AC_2_f_1_d", "AC_2_f_1_e", "AC_2_f_2_a", "AC_2_f_2_b", "AC_2_f_2_c", "AC_2_f_2_d", "AC_2_f_2_e", "AC_2_g", "AC_2_h_1", "AC_2_h_2", "AC_2_h_3", "AC_2_i_1", "AC_2_i_2", "AC_2_i_3", "AC_2_j_1", "AC_2_j_2", "AC_2_k", "AC_3", "AC_3_my_org_1", "AC_4_1", "AC_4_2", "AC_4_21_1", "AC_4_21_2", "AC_4_21_3", "AC_6", "ac_6_9", "ac_6_9_test", "AU_12_a_1", "au_12_a_2", "au_12_a_2_test", "AU_12_b_1", "au_12_b_2", "au_12_b_2_test", "au_12_c", "au_12_c_test", "au_12_my_org_1", "au_12_my_org_2", "AU_2_a_1", "au_2_a_2", "au_2_a_2_test", "AU_2_b", "AU_2_c", "AU_2_d_1", "AU_2_d_2", "AU_2_d_3", "AU_6_a_1", "AU_6_a_2", "AU_6_a_3", "AU_6_b_1", "AU_6_b_2", "AU_6_my_org_1", "AU_6_my_org_2", "AU_6_my_org_3", "CA_3_a", "CA_3_b_1", "CA_3_b_2", "CA_3_b_3", "CA_3_c_1", "CA_3_c_2", "CA_5_a_1", "CA_5_a_2", "CA_5_b_1", "CA_5_b_2_a", "CA_5_b_2_b", "CA_5_b_2_c", "CA_5_my_org_1", "CA_7_a_1", "CA_7_a_2"]
   if "test" not in ctl %}
  {# Are we changing families? #}
  {% if ctl.split("_")[0].upper() != meta["current_family"].upper() %}
    {% set var_ignore = meta.update({"current_family": ctl.split("_")[0].upper()}) %}
    <h3 style="margin-bottom: 30px;">{{meta["current_family"]|upper}}</h3>
  {% endif %}
  {% set ctl_od_title = "nist_80053rev4_ssp_{}".format(ctl) %}
  {% set odl = ctl_od_title.split('_') %}
  {% set c_name = "{}-{}".format(odl[3].upper(), "".join(odl[4])) %}
  {# Are we changing control name? #}
  {% if c_name.upper() != meta["current_control"].upper() %}
    {# Close previous control table if this is not first time through loop #}
    {% if not loop.first %}
      </table>
    {% endif %}
    {% set var_ignore = meta.update({"current_control": c_name}) %}
      <h4 style="">{{meta["current_control"]|upper}} {{control_catalog[meta["current_control"]|upper]['title']}}</h4>
      <table class="table-ssp">
        <tr>
          <td colspan="2" class="td-header">
          {{meta["current_control"]|upper}}: What is the solution and how is it implemented?
        </td></tr>
  {% endif %}
  {% set c_name_part = "{}-{}".format(odl[3].upper(), " ".join(odl[4:])) %}
  <tr>
    <td class="td-c-name-part">{{c_name_part}}</td>
    <td>
      {{control_catalog[meta["current_control"]|upper]['title']}}
    </td>
  </tr>
  {% if not loop.last %}
    {% if loop.nextitem.split("_")[0].upper() != meta["current_family"].upper() %}
      </table>
    {% endif %}
  {% endif %}
{% endfor %}<!-- /for ctl in -->






