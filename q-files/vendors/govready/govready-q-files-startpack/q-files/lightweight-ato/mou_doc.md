id: mou_doc
format: markdown
title: Memorandum of Understanding
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

<!-- Cover page -->
<center>

<center>
<h1 class="title">MEMORANDUM OF UNDERSTANDING (OR AGREEMENT)<br/>{{project.system_info.system_name}}</h1>
</center>

<div class="page-break">
  <table class="footer">
    <tr>
      <td width="33%"><strong>{{project.system_info.system_short_name}}</strong></td>
      <td width="34%" style="text-align: center;"><strong>LIMITED OFFICIAL USE</strong></td>
      <td width="33%" style="text-align: right;"> <!-- page number --></td>
    </tr><tr>
      <td colspan="3">Security Test Plan</td>
    </tr>
  </table>
</div>

FOR OFFICIAL USE ONLY


**Updated (Date Information)**

**System Name:** 
**{{project.system_info.system_name}} {% if project.system_info.system_short_name %} ({{project.system_info.system_short_name}}){% endif %}**


<table border='3' width="400">
<tr><td>
<p>This document contains Sensitive Material
and is exempted from release under the Freedom of Information Act
by Exemption b(2).</p>
<p>Staff reviewing this document must hold a minimum of Public Trust
Level 1c clearance.</p>
</tr></td>
</table>

<div style="height: 400px;">
  <!-- Spacer for cover page -->
</div>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

</center>
<!-- /Cover page -->

<!-- System Information -->
<h2>1. System Information</h2>

{{project.system_info.output_documents.system_info}}

<!-- /System Information -->

<h2>1.  INFORMATION SYSTEM NAME/TITLE</h2>

This System Security Plan provides an overview of the security requirements for the Information System Name (Enter Information System Abbreviation) and describes the controls in place or planned for implementation to provide a level of security appropriate for the information to be transmitted, processed or stored by the system.  Information security is vital to our critical infrastructure and its effective performance and protection is a key component of our national security program.  Proper management of information technology systems is essential to ensure the confidentiality, integrity and availability of the data transmitted, processed or stored by the Enter Information System Abbreviation information system.

The security safeguards implemented for the Enter Information System Abbreviation system meet the policy and control requirements set forth in this System Security Plan.  All systems are subject to monitoring consistent with applicable laws, regulations, agency policies, procedures and practices.

<div class="table-caption">Table 1-1. Information System Name and Title</div>

<!-- Information System Table goes -->
<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Unique Identifier</th>
      <th class="th-header">Information System Name</th>
      <th class="th-header">Information System Abbreviation</th>
    </tr>
    <tr>
      <td>{{project.fisma_level.application_number}}</td>
      <td>{{project.system_info.system_name}}</td>
      <td>{{project.system_info.system_short_name}}</td>
    </tr>
</table>


<h2>2.  INFORMATION SYSTEM CATEGORIZATION</h2>

The overall information system sensitivity categorization is recorded in Table 2 1. Security Categorization that follows.  Directions for attaching the FIPS 199 document may be found in the following section: Attachment 10, FIPS 199.

<div class="table-caption">Table 2-1. Security Categorization</div>

<!-- security categorization table goes here -->
<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">System Sensitivity Level</th>
      <td>{{project.fisma_level.fisma_level}}</td>
    </tr>
</table>

<h3>2.1 Information Types</h3>

This section describes how the information types used by the information system are categorized for confidentiality, integrity and availability sensitivity levels.

The following tables identify the information types that are input, stored, processed and/or output from Enter Information System Abbreviation.  The selection of the information types is based on guidance provided by Office of Management and Budget (OMB) Federal Enterprise Architecture Program Management Office Business Reference Model 2.0 and FIPS Pub 199, Standards for Security Categorization of Federal Information and Information Systems which is based on NIST Special Publication (SP) 800-60, Guide for Mapping Types of Information and Information Systems to Security Categories. 

The tables also identify the security impact levels for confidentiality, integrity and availability for each of the information types expressed as low, moderate, or high.  The security impact levels are based on the potential impact definitions for each of the security objectives (i.e., confidentiality, integrity and availability) discussed in NIST SP 800-60 and FIPS Pub 199. 
The potential impact is low if—

* The loss of confidentiality, integrity, or availability could be expected to have a limited adverse effect on organizational operations, organizational assets, or individuals.
* A limited adverse effect means that, for example, the loss of confidentiality, integrity, or availability might: (i) cause a degradation in mission capability to an extent and duration that the organization is able to perform its primary functions, but the effectiveness of the functions is noticeably reduced; (ii) result in minor damage to organizational assets; (iii) result in minor financial loss; or (iv) result in minor harm to individuals.

The potential impact is moderate if—

* The loss of confidentiality, integrity, or availability could be expected to have a serious adverse effect on organizational operations, organizational assets, or individuals. 
* A serious adverse effect means that, for example, the loss of confidentiality, integrity, or availability might: (i) cause a significant degradation in mission capability to an extent and duration that the organization is able to perform its primary functions, but the effectiveness of the functions is significantly reduced; (ii) result in significant damage to organizational assets; (iii) result in significant financial loss; or (iv) result in significant harm to individuals that does not involve loss of life or serious life threatening injuries.

The potential impact is high if—

* The loss of confidentiality, integrity, or availability could be expected to have a severe or catastrophic adverse effect on organizational operations, organizational assets, or individuals. 
* A severe or catastrophic adverse effect means that, for example, the loss of confidentiality, integrity, or availability might: (i) cause a severe degradation in or loss of mission capability to an extent and duration that the organization is not able to perform one or more of its primary functions; (ii) result in major damage to organizational assets; (iii) result in major financial loss; or (iv) result in severe or catastrophic harm to individuals involving loss of life or serious life threatening injuries. 