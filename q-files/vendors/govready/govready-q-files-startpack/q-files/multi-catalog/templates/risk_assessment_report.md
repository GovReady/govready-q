id: risk_assessment_report.md
format: markdown
title: Risk Assessment Report
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
<h1 class="title">Risk Assessment Report<br/>for {{project.system_info.system_name}}</h1>
<img style="max-width:70%;height:auto;" src="{{static_asset_path_for('app.png')}}">
<br></br>
<h1>Prepared for</br/>{{project.system_info.system_org}}</h1>
<br></br>
{{project.risk_assessment_report_doc.rar_date}}
</center>




* * *

## Table of Contents

*   [Risk Assessment Report](#rap)
    *   [Section 1: Hardware](#hardware)
    *   [Section 2: Published Software](#software)
    *   [Section 3: Organization Address](#address)
    *   [Section 4: Document Purpose, Assumptions, and Constraints](#purpose)
    *   [Section 5: Control Analysis Table](#controlanalysis)
    *   [Section 6: System Interfaces](#systeminterface)
    *   [Section 7: Information Gathered](#infogather)
    *   [Section 8: Vulnerabilities](#vulnerabilities)
    *   [Section 9: List of Observations](#observations)
    *   [Section 10: Participants, Personnel, and Location](#participantspersonnellocation)


* * *

## Risk Assessment Report

### Section 1: Hardware

{% if project.risk_assessment_report.hardware == "yes" %} Yes, hardware was entered for this project's risk assessment. </br>
{{project.risk_assessment_report.hardware_yes}}{% endif %}

{% if project.risk_assessment_report.hardware == "no" %} No hardware was entered for this project's risk assessment.{% endif %}

</br>

### Section 2: Published Software

{% if project.risk_assessment_report.software == "yes" %} Yes, software was entered for this project's risk assessment. </br>
{{project.risk_assessment_report.software_yes}}{% endif %}

{% if project.risk_assessment_report.software == "no" %} No software was entered for this project's risk assessment.{% endif %}

</br>

### Section 3: Address for Organization

<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-lboi{border-color:inherit;text-align:left;vertical-align:middle}
</style>
<table class="tg" align="center">
  <tr>
    <th class="tg-lboi">Component's Address</th>
    <th class="tg-lboi">{{project.risk_assessment_report.component_address}}</th>
  </tr>
</table>

</br>

### Section 4, Document Purpose, Assumptions, and Constraints

The Risk Assessment identifies risk to the system operation based on vulnerabilities (those areas that do not meet minimum requirements and for which adequate countermeasures have not been implemented). The Risk Assessment also determines the likelihood of occurrence and suggests countermeasures to mitigate identified risks in an effort to provide an appropriate level-of-protection and to meet all minimum requirements imposed on the system.   

The system security policy requirements are being met at this time with the exception of those areas identified in this report. The countermeasures recommended in this report specify the additional security controls needed to meet policies and to effectively manage the security risk to the system and its operating environment. Ultimately, the Security Control Assessor and the Authorizing Official must determine whether the totality of the protection mechanisms approximate a sufficient level of security, and are adequate for the protection of this system and its resources/information. The Risk Assessment Results supplied critical information and should be carefully reviewed by the AO prior to making a final security authorization decision. The control categories for both technical and nontechnical control methods can be further classified as either preventive or detective. 
These two subcategories are explained as follows: 
* Preventive controls inhibit attempts to violate security policy and include such controls as access control enforcement, encryption, and authentication.
* Detective controls warn of violations or attempted violations of security policy and include such controls as audit trails, intrusion detection methods, and checksums

</br>

### Section 5, Control Analysis Table

[[[THIS SECTION NEEDS ATTENTION]]]

[[[Note: Counts the amount of control categories and files them as preventive or defective. And out of those two subcategories, they are matrixed as either being implemented or not implemented.]]]

</br>

Preventive controls provide greater risk mitigation than detective controls. Preventive controls properly implemented and operating as intended provide automatic risk mitigation without the need for additional manual procedures. Detective controls require additional procedures to ensure that risks, incidents, and vulnerabilities they uncover are properly mitigated or remediated.  

{{project.risk_assessment_report.rar_version_grid}}

</br>

### Section 6, System Interfaces

{% if project.risk_assessment_report.sys_interface == "yes" %} Yes, system interfaces were entered for this project's risk assessment. </br>
{{project.risk_assessment_report.sys_interface_yes}}{% endif %}

{% if project.risk_assessment_report.sys_interface == "no" %} No sys_inter was entered for this project's risk assessment.{% endif %}

</br>

### Section 7, How was information gathered?

The information for this Risk Assessment Report was gathered by the following means:

{{project.risk_assessment_report.information_gather.text}}
{% if project.risk_assessment_report.information_gather == "other" %}Other:
{{project.risk_assessment_report.information_gather_other}}
{% endif %}

</br>


### Section 8, Vulnerabilities

[[[THIS SECTION NEEDS ATTENTION]]]

Among the [NUMBER OF VULNERABILITIES] vulnerabilities identified, [PERCENTAGE OF VULNERABILITIES CONSIDERED UNACCEPTABLE] are considered unacceptable because serious harm could result and affect the operation of the system. Immediate, mandatory countermeasures need to be implemented to mitigate the risk of these threats. Resources must be made available to reduce the risk to an acceptable level.   

[PERCENTAGE OF VULNERABILITIES CONSIDERED ACCEPTABLE] of the identified vulnerabilities are considered acceptable to the system because only minor problems may result from these risks. Recommended countermeasures have also been provided for implementation to reduce or eliminate the risk. 

[[[THERE NEEDS TO BE A TABLE THAT SHOWS THE LVEL OF ACCEPTABLE VS UNACCEPTABLE VULNERABILITIES ]]]

</br>


### Section 9, List of observations


[[[THIS SECTION NEEDS ATTENTION]]]
[[[NEEDS A TABLE WITH THE FOLLOWING:
Columns: number, vulnerability, threat, likelihood, impact level, indentification source, countermeasures, risk level, recommended remediation or risk acceptance]]]

Based on the observations listed in this assessment, [NUMBER OF LOW RISK VULNERABILITIES] were determined to have a Low risk rating; [NUMBER OF MODERATE RISK VULNERABILITIES] were determined to have a Moderate risk rating; [NUMBER OF HIGH RISK VULNERABILITIES] were determined to have a High risk rating. As a result the overall level of risk of operating the system is High.

</br>

### Section 10, Participants, Personnel, and Location

#### Participants
{{project.risk_assessment_report.participants}}
</br>

#### Personnel Clearance Requirements
{{project.risk_assessment_report.personnel}}
</br>

#### Facilities & Locations
{{project.risk_assessment_report.location}}

