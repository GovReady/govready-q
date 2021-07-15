id: ssp_v1
format: markdown
title: SSP v1
...

<style type="text/css" scoped>

    body { max-width: 950px; margin: auto; }
    h2 { border-bottom:1px solid #888; margin-top: 3em; color: red;}
    h3 { border-bottom: 0.5px solid #aaa; color: #777; font-size: 14pt; font-weight: bold;}
    h4 { margin-top: 15px; font-weight: normal; font-size: 1em; }
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

    td.td-header, th.th-header, th {
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

    .warning {
      color: red;
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
<img style="max-width:70%;height:auto;" src="{{static_asset_path_for('app.png')}}">
<h1 class="title">{{project.speedy_ssp_basic_info.system_name}}<br/>System Security Plan</h1>
</center>

<div class="page-break">
  <table class="footer">
    <tr>
      <td width="33%"><strong>{{project.speedy_ssp_basic_info.system_name}}</strong></td>
      <td width="34%" style="text-align: center;"><strong>LIMITED OFFICIAL USE</strong></td>
      <td width="33%" style="text-align: right;"> </td>
    </tr><tr>
      <td colspan="3">Security Test Plan</td>
    </tr>
  </table>
</div>

FOR OFFICIAL USE ONLY


**Updated (Date Information)**

**System Name:**
**{{project.speedy_ssp_basic_info.system_name}}**


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

<!-- System Information -->
<h2>Executive Summary</h2>

{{project.speedy_ssp_additional_info.system_description}}

<!-- /System Information -->

<h2>1.  INFORMATION SYSTEM NAME/TITLE</h2>

This System Security Plan provides an overview of the security requirements for the Information System Name (Enter Information System Abbreviation) and describes the controls in place or planned for implementation to provide a level of security appropriate for the information to be transmitted, processed or stored by the system.  Information security is vital to our critical infrastructure and its effective performance and protection is a key component of our national security program.  Proper management of information technology systems is essential to ensure the confidentiality, integrity and availability of the data transmitted, processed or stored by the Enter Information System Abbreviation information system.

The security safeguards implemented for the Enter Information System Abbreviation system meet the policy and control requirements set forth in this System Security Plan.  All systems are subject to monitoring consistent with applicable laws, regulations, agency policies, procedures and practices.

**Table 1-1. Information System Name and Title**

<!-- Information System Table goes -->
<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Unique Identifier</th>
      <th class="th-header">Information System Name</th>
    </tr>
    <tr>
      <td>{{project.speedy_ssp_additional_info.unique_identifier}}</td>
      <td>{{project.speedy_ssp_basic_info.system_name}}</td>
    </tr>
</table>


<h2>2.  INFORMATION SYSTEM CATEGORIZATION</h2>

The overall information system sensitivity categorization is recorded in Table 2 1. Security Categorization that follows.  Directions for attaching the FIPS 199 document may be found in the following section: Attachment 10, FIPS 199.

**Table 2-1. Security Categorization**

<!-- security categorization table goes here -->
<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">System Sensitivity Level</th>
    </tr>
    <tr>
      <td>{{project.speedy_ssp_basic_info.fisma_level}}</td>
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

**Table 2-2. Sensitivity Categorization of Information Types**
<!-- Sensitivity Categorization of Information Types Table goes -->
<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Information Types</th>
    </tr>
    <tr>
      <td>N/A</td>
    </tr>
</table>


<h2>2.2 Security Objectives Categorization</h2>
Based on the information provided in Table 2 2. Sensitivity Categorization of Information Types, for the Enter Information System Abbreviation, default to the high-water mark for the Information Types as identified in Table 2 3. Security Impact Level below.

**Table 2-3. Security Impact Level**

<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Security Impact Review</th>
    </tr>
    <tr>
      <td>Your system's FISMA Level is {{project.speedy_ssp_basic_info.fisma_level}}.</td>
    </tr>
    <tr>
      <td>Information Types: N/A /td>
    </tr>
    <tr>
      <td>Impact Level based on Information Types: {{project.speedy_ssp_basic_info.fisma_level}}</td>
    </tr>
</table>

Through review and analysis, it has been determined that the baseline security categorization for the Enter Information System Abbreviation system is listed in the Table 2 4. Baseline Security Configuration that follows.

**Table 2-4. Baseline Security Configuration**

<!-- Security Impact Level Table goes here -->
<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Security Impact Level</th>
    </tr>
    <tr>
      <td>{{project.speedy_ssp_basic_info.fisma_level}}</td>
    </tr>
</table>


Using this categorization, in conjunction with the risk assessment and any unique security requirements, we have established the security controls for this system, as detailed in this SSP.


<h2>3.  INFORMATION SYSTEM OWNER</h2>

The following individual is identified as the system owner or functional proponent/advocate for this system.


**Table 3-1. Information System Owner**

{{project.speedy_ssp_additional_info.system_owner}}

<h2>4.  AUTHORIZING OFFICIAL</h2>

The Authorizing Official (AO) or Designated Approving Authority (DAA) for this information system is:

**Table 4-1. Information System Authorizing Official**

{{project.speedy_ssp_additional_info.authorizing_official}}

<h2>5.  OTHER DESIGNATED CONTACTS</h2>

**Table 5-1. Information System Management Point of Contact**

{{project.speedy_ssp_additional_info.information_system_manager}}

**Table 5-2. Information System Technical Point of Contact**

{{project.speedy_ssp_additional_info.information_system_tech}}

<h2>6.  ASSIGNMENT OF SECURITY RESPONSIBILITY</h2>

**Table 6-1. CSP name Internal ISSO (or Equivalent) Point of Contact**

{{project.speedy_ssp_additional_info.information_system_security}}

**Table 6-2. AO Point of Contact**

{{project.speedy_ssp_additional_info.information_system_ao_poc}}

<h2>7.  INFORMATION SYSTEM OPERATIONAL STATUS</h2>

The system is currently in the life-cycle phase shown in Table 7 1. System Status that follows.  (Only operational systems can be granted an ATO).

**Table 7-1. System Status**

<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">System Status</th>
    </tr>
    <tr>
      <td>{{project.speedy_ssp_additional_info.system_status.text}}</td>
    </tr>
</table>

<h2>8.  INFORMATION SYSTEM TYPE</h2>

Information systems, particularly those based on cloud architecture models, are made up of different service layers.  Below are some questions that help the system owner determine if their system is a cloud followed by specific questions to help the system owner determine the type of cloud.

**Table 8-1. Service Layers Represented in this SSP**

<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Cloud Service Model</th>
    </tr>
    <tr>
      <td>{{project.speedy_ssp_additional_info.cloud_service_model.text}}</td>
    </tr>
</table>

Note: Refer to NIST SP 800-145 for information on cloud computing architecture models.

<h3>8.2.  Cloud Deployment Models</h3>

Information systems are made up of different deployment models.  The deployment models of the Enter Information System Abbreviation that are defined in this SSP and are not leveraged by any other FedRAMP Authorizations, are indicated in Table 8 2. Cloud Deployment Model Represented in this SSP that follows.

**Table 8-2. Cloud Deployment Model Represented in this SSP**

<table class="table-ssp" border="1">
    <tr>
      <th class="th-header">Cloud Deployment Model</th>
    </tr>
    <tr>
      <td>{{project.speedy_ssp_additional_info.cloud_model.text}}</td>
    </tr>
</table>

<h3>8.3. Leveraged Authorizations</h3>

{{project.speedy_ssp_basic_info.system_name}}leverages a pre-existing FedRAMP Authorization.  FedRAMP Authorizations leveraged by this Enter Information System Abbreviation are listed in Table 8 3. Leveraged Authorizations that follows.

**Table 8-3. Leveraged Authorizations**

{{project.speedy_ssp_additional_info.leveraged_authorizations}}

<h2>9.  GENERAL SYSTEM DESCRIPTION</h2>

<h3>9.1.  System Function or Purpose</h3>

{{project.speedy_ssp_additional_info.system_description}}

<h3>9.2.  Information System Components and Boundaries</h3>

A detailed and explicit definition of the system authorization boundary diagram is represented in Figure 9-1. Authorization Boundary Diagram below.

**Figure 9-1. Authorization Boundary Diagram**
{{project.speedy_ssp_additional_info.system_auth_diagram}}

<h3>9.3.  Types of Users</h3>

All personnel have their status categorized with a sensitivity level in accordance with PS-2.  Personnel (employees or contractors) of service providers are considered Internal Users.  All other users are considered External Users.  User privileges (authorization permission after authentication takes place) are described in Table 9 1. Personnel Roles and Privileges that follows.

**Table 9-1. Personnel Roles and Privileges**

{{project.speedy_ssp_additional_info.security_impact_users}}

<h3>9.4.  Network Architecture</h3>

The logical network topology is shown in Figure 9 2. Network Diagram mapping the data flow between components.

The following Figure 9 2. Network Diagram(s) provides a visual depiction of the system network components that constitute Enter Information System Abbreviation.

**Figure 9-2. Architecture Diagram**
{{project.speedy_ssp_additional_info.system_network_diagram}}

<h2>10. SYSTEM ENVIRONMENT AND INVENTORY</h2>
Directions for attaching the FedRAMP Inventory Workbook may be found in the following section: Attachment 13, FedRAMP Inventory Workbook.

<h3>10.1. Data Flow</h3>
The data flow in and out of the system boundaries is represented in Figure 10 1. Data Flow Diagram below.

**Figure 10-1. Data Flow Diagram**
{{project.speedy_ssp_additional_info.system_data_diagram}}


<h3>10.2. Ports, Protocols and Services</h3>

The Table 10 1. Ports, Protocols and Services below lists the ports, protocols and services enabled in this information system.

**Table 10-1. Ports, Protocols and Services**

{{project.speedy_ssp_additional_info.ports_protocols_services}}

<h3>11. SYSTEM INTERCONNECTIONS</h3>

**Table 11-1. System Interconnections**

{{project.speedy_ssp_additional_info.system_interconnections}}


<h2>12. LAWS, REGULATIONS, STANDARDS AND GUIDANCE</h2>
A summary of FedRAMP Laws and Regulations is included in Attachment 12, FedRAMP Laws and Regulations.

<h3>12.1. Applicable Laws and Regulations</h3>
The FedRAMP Laws and Regulations can be found on this web page: Templates.
Table 12 1. Information System Name Laws and Regulations includes additional laws and regulations specific to Information System Name.

**Table 12-1. Information System Name Laws and Regulations**

{{project.speedy_ssp_additional_info.laws_regulations}}

<h3>12.2. Applicable Standards and Guidance</h3>
The FedRAMP Standards and Guidance be found on this web page: Templates
Table 12 2. Information System Name Standards and Guidance includes in this section any additional standards and guidance specific to Information System Name.

**Table 12-2. Information System Name Standards and Guidance**

{{project.speedy_ssp_additional_info.standards_guidance}}



<!-- Testing links -->
<a id="controls" name="controls"></a>
<h2>13. MINIMUM SECURITY CONTROLS</h2>

Security controls must meet minimum security control baseline requirements.  Upon categorizing a system as Low, Moderate, or High sensitivity in accordance with FIPS 199, the corresponding security control baseline standards apply.  Some of the control baselines have enhanced controls which are indicated in parentheses.

Security controls that are representative of the sensitivity of Enter Information System Abbreviation are described in the sections that follow.  Security controls that are designated as “Not Selected” or “Withdrawn by NIST” are not described unless they have additional FedRAMP controls.  Guidance on how to describe the implemented standard can be found in NIST 800-53, Rev 4.  Control enhancements are marked in parentheses in the sensitivity columns.

Systems that are categorized as FIPS 199 Low use the controls designated as Low, systems categorized as FIPS 199 Moderate use the controls designated as Moderate and systems categorized as FIPS 199 High use the controls designated as High.

<!--Control catalog here-->

{% if control_catalog|length > system.root_element.selected_controls_oscal_ctl_ids|length %}
{% set meta = {"current_family_title": "", "current_control": "", "current_control_part": "", "control_count": 0, "current_parts": []} %}

{% for control in system.root_element.selected_controls_oscal_ctl_ids %}
  {% set var_ignore = meta.update({"control_count": meta['control_count'] + 1}) %}

  {% if meta['current_family_title'] != control_catalog[control.lower()]['family_title'] %}
    {# When current current control family changes print the new control family and update the current control family #}
    <h2>{{control_catalog[control.lower()]['family_id']|upper}} - {{control_catalog[control.lower()]['family_title']}}</h2>
    {% set var_ignore = meta.update({"current_family_title": control_catalog[control.lower()]['family_title']}) %}
  {% endif %}
  <div>
    {% if control.lower() in control_catalog %}
    <div>{{control|upper}} - {{control_catalog[control.lower()]['title']}}</div>
    <div style="white-space: pre-wrap;">{{control_catalog[control.lower()]['description']}}</div>
    <div>
      <h4>What is the solution and how is it implemented?</h4>
        {% if control in system.control_implementation_as_dict %}
          <div style="white-space: pre-line; word-break: keep-all;">{{ system.control_implementation_as_dict[control]['combined_smt']|safe }}</div>
        {% else %}
          <div style="white-space: pre-line; word-break: keep-all;">No statement available.</div>
        {% endif %}
    </div>
    {% endif %}
  </div>
{% endfor %}

{% else %}

{% for catalog_list in control_catalog %}
{% set meta = {"current_family_title": "", "current_control": "", "current_control_part": "", "current_catalog": "", "control_count": 0, "current_parts": []} %}
{% for catalog_dict in catalog_list %}
  {% set var_ignore = meta.update({"control_count": meta['control_count'] + 1}) %}

  {% if meta['current_catalog'] != catalog_dict['catalog_key'] %}
    {# When current catalog changes print the new control family and update the current control family #}
    <h1>{{catalog_dict['catalog_key']}}</h1>
    {% set var_ignore = meta.update({"current_catalog": catalog_dict['catalog_key']}) %}
  {% endif %}

  {% if meta['current_family_title'] != catalog_dict['family_title'] %}
    {# When current control family changes print the new control family and update the current control family #}
    <h2>{{catalog_dict['family_id']|upper}} - {{catalog_dict['family_title']}}</h2>
    {% set var_ignore = meta.update({"current_family_title": catalog_dict['family_title']}) %}
  {% endif %}
  <div>
  {% if catalog_dict['id'] in system.root_element.selected_controls_oscal_ctl_ids %}
<div>{{catalog_dict['id']|upper}} - {{catalog_dict['title']}}</div>
<div style="white-space: pre-wrap;">{{catalog_dict['description']}}</div>
<div>
  <h4>What is the solution and how is it implemented?</h4>
    {% if catalog_dict['id'] in system.control_implementation_as_dict %}
      <div style="white-space: pre-line; word-break: keep-all;">{{ system.control_implementation_as_dict[catalog_dict['id']]['combined_smt']|safe }}</div>
    {% else %}
      <div style="white-space: pre-line; word-break: keep-all;">No statement available.</div>
    {% endif %}
</div>
    {% endif %}
  </div>
{% endfor %}
{% endfor %}

{% endif %}

{% if system.root_element.selected_controls_oscal_ctl_ids|length == 0 %}
<i>Control requirements have not yet been assigned to this system.</i>
{% endif %}

<!-- /13. MINIMUM SECURITY CONTROLS -->

