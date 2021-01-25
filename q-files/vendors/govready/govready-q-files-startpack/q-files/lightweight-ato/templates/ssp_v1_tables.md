id: ssp_v1_tables
format: markdown
title: SSP v1 Tables
...
<style type="text/css" scoped>
  h2 { border-bottom:1px solid #888; color: red; }
  h3 { border-bottom:0.5px solid #aaa; }
  h4 { font-weight:bold; font-size:0.9em; }
  blockquote { color: #666; font-size:0.8em;}
  .notice {color: red; font-size:3.0em; text-align:center; transform: scaleY(.85);
  font-weight: bold;}
  table, th, td { border: 1px solid #888; }
  th, td { padding: 15px; text-align: left;}

  .soft {
    color: #aaa;
  }
</style>

<!-- Cover page -->
<center>

FOR OFFICIAL USE ONLY


{{ project.system_profile.system_basics.system_name }}
System Security Plan (SSP)

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

<div style="text-align:center;">Table 1 1. Information System Name and Title</div>

<!-- Information System Table goes -->


<h2>2.  INFORMATION SYSTEM CATEGORIZATION</h2>

The overall information system sensitivity categorization is recorded in Table 2 1. Security Categorization that follows.  Directions for attaching the FIPS 199 document may be found in the following section: Attachment 10, FIPS 199.


<div style="text-align:center;">Table 2 1. Security Categorization</div>

<!-- security categorization table goes here -->



<!-- Testing links -->
<a id="controls" name="controls"></a>
<h2>2. Security Controls Testing Loops</h2>

{% set meta = {"current_family": "", "current_control": "", "current_control_part": ""} %}
{% for ctl in ["AC_11_a_1", "AC_11_a_2", "AC_23_1", "AC_23_2", "AC_23_3", "AC_2_a_1", "AC_2_a_2", "AC_2_b", "AC_2_c", "AC_2_d_1", "AC_2_d_2", "AC_2_d_3", "AC_2_d_4", "AC_2_e_1", "AC_2_e_2", "AC_2_f_1_a", "AC_2_f_1_b", "AC_2_f_1_c", "AC_2_f_1_d", "AC_2_f_1_e", "AC_2_f_2_a", "AC_2_f_2_b", "AC_2_f_2_c", "AC_2_f_2_d", "AC_2_f_2_e", "AC_2_g", "AC_2_h_1", "AC_2_h_2", "AC_2_h_3", "AC_2_i_1", "AC_2_i_2", "AC_2_i_3", "AC_2_j_1", "AC_2_j_2", "AC_2_k", "AC_3", "AC_3_my_org_1", "AC_4_1", "AC_4_2", "AC_4_21_1", "AC_4_21_2", "AC_4_21_3", "AC_6", "ac_6_9", "ac_6_9_test", "AU_12_a_1", "au_12_a_2", "au_12_a_2_test", "AU_12_b_1", "au_12_b_2", "au_12_b_2_test", "au_12_c", "au_12_c_test", "au_12_my_org_1", "au_12_my_org_2", "AU_2_a_1", "au_2_a_2", "au_2_a_2_test", "AU_2_b", "AU_2_c", "AU_2_d_1", "AU_2_d_2", "AU_2_d_3", "AU_6_a_1", "AU_6_a_2", "AU_6_a_3", "AU_6_b_1", "AU_6_b_2", "AU_6_my_org_1", "AU_6_my_org_2", "AU_6_my_org_3", "CA_3_a", "CA_3_b_1", "CA_3_b_2", "CA_3_b_3", "CA_3_c_1", "CA_3_c_2", "CA_5_a_1", "CA_5_a_2", "CA_5_b_1", "CA_5_b_2_a", "CA_5_b_2_b", "CA_5_b_2_c", "CA_5_my_org_1", "CA_7_a_1", "CA_7_a_2", "CA_7_a_3", "CA_7_b_1", "CA_7_b_2", "CA_7_b_3", "CA_7_b_4", "CA_7_c_1", "CA_7_c_2", "CA_7_d_1", "CA_7_d_2", "CA_7_e_1", "CA_7_e_2", "CA_7_f_1", "CA_7_f_2", "CA_7_g_1", "CA_7_g_2", "CA_7_g_3", "CA_7_g_4", "CA_8_1", "CA_8_2", "CA_8_3", "CM_2_1", "CM_2_2", "CM_2_my_org_1", "CM_6_1_1_a", "CM_6_1_1_b", "CM_6_1_1_c", "CM_6_1_2_a", "CM_6_1_2_b", "CM_6_1_2_c", "CM_6_a_1", "CM_6_a_2", "CM_6_a_3", "CM_6_b", "CM_6_c_1", "CM_6_c_1_b", "CM_6_c_1_c", "CM_6_c_2_a", "CM_6_c_2_b", "CM_6_c_2_c", "CM_6_c_3", "CM_6_c_4", "CM_6_c_5", "CM_6_d_1", "CM_6_d_2", "CM_6_my_org_1", "CM_6_my_org_2", "CM_6_my_org_3", "CM_6_my_org_4", "CM_6_my_org_5", "CM_6_my_org_6", "CM_6_my_org_7", "CM_6_my_org_8", "CM_7_a", "CM_7_b_1_a", "CM_7_b_1_b", "CM_7_b_1_c", "CM_7_b_1_d", "CM_7_b_2_a", "CM_7_b_2_b", "CM_7_b_2_c", "CM_7_b_2_d", "CM_8_a_1", "CM_8_a_2", "CM_8_a_3", "CM_8_a_4_1", "CM_8_a_4_2", "CM_8_b_1", "CM_8_b_2", "CM_8_my_org_1", "CM_8_my_org_2", "CP_2_a_1", "CP_2_a_2_1", "CP_2_a_2_2", "CP_2_a_2_3", "CP_2_a_3_1", "CP_2_a_3_2", "CP_2_a_3_3", "CP_2_a_4", "CP_2_a_5", "CP_2_a_6_1", "CP_2_a_6_2", "CP_2_b_1", "CP_2_b_2", "CP_2_c", "CP_2_d_1", "CP_2_d_2", "CP_2_e_1", "CP_2_e_2", "CP_2_f_1", "CP_2_f_2", "CP_4_a_1", "CP_4_a_2", "CP_4_a_3", "CP_4_b", "CP_4_C", "CP_4_my_org_1", "IA_2", "IA_2_1", "IA_2_12_1", "IA_2_12_2", "IA_2_2", "IA_2_8", "IA_2_9", "IA_2_my_org_1", "IA_2_my_org_2", "IR_4_a_1", "IR_4_a_2", "IR_4_a_3", "IR_4_a_4", "IR_4_a_5", "IR_4_b", "IR_4_c_1_a", "IR_4_c_1_b", "IR_4_c_1_c", "IR_4_c_2_a", "IR_4_c_2_b", "IR_4_c_2_c", "IR_5_1", "IR_5_2", "IR_6_a_1", "IR_6_a_2", "IR_6_b_1", "IR_6_b_2", "MP_4", "MP_4_a_1", "MP_4_a_2", "MP_4_a_3", "MP_4_a_4", "MP_4_b", "PL_2_a_1", "PL_2_a_2", "PL_2_a_3", "PL_2_a_4", "PL_2_a_5", "PL_2_a_6", "PL_2_a_7", "PL_2_a_8", "PL_2_a_9", "PL_2_b_1", "PL_2_b_2", "PL_2_c_1", "PL_2_c_2", "PL_2_d_1", "PL_2_d_2", "PL_2_d_3", "PL_2_e_1", "PL_2_e_2", "PL_8_a_1", "PL_8_a_2", "PL_8_a_3", "PL_8_b_1", "PL_8_b_2", "PL_8_c_1", "PL_8_c_2", "PL_8_c_3", "RA_2_a", "RA_2_b", "RA_2_c", "RA_3_a_1", "RA_3_a_2", "RA_3_b_1", "RA_3_b_2_a", "RA_3_b_2_b", "RA_3_b_2_c", "RA_3_c_1", "RA_3_c_2", "RA_3_d_1", "RA_3_d_2", "RA_3_e_1", "RA_3_e_2_a", "RA_3_e_2_b", "RA_3_e_2_c", "RA_5_a_1_a", "RA_5_a_1_b", "RA_5_a_2_a", "RA_5_a_2_b", "RA_5_a_3_a", "RA_5_a_3_b", "RA_5_b_1_1", "RA_5_b_1_2", "RA_5_b_1_3", "RA_5_b_2_1", "RA_5_b_2_2", "RA_5_b_3", "RA_5_c_1", "RA_5_c_2", "RA_5_d_1", "RA_5_d_2", "RA_5_e_1", "RA_5_e_2", "RA_5_e_3", "SA_11_1", "SA_22_a", "SA_22_b_1", "SA_22_b_2", "SA_9_a_1", "SA_9_a_2", "SA_9_a_3", "SA_9_b_1", "SA_9_b_2", "SA_9_c_1", "SA_9_c_2", "SC_12_1_a", "SC_12_1_b", "SC_12_1_c", "SC_12_1_d", "SC_12_1_e", "SC_12_2", "SC_12_my_org_1", "SC_12_my_org_2", "SC_12_my_org_3", "SC_12_my_org_4", "SC_12_my_org_5", "SC_13_1", "SC_13_2", "SC_13_3", "SC_13_my_org_1", "SC_13_my_org_2", "SC_13_my_org_3", "SC_13_my_org_4", "SC_13_my_org_5", "SC_18_a", "SC_18_b_1", "SC_18_b_2", "SC_18_c_1", "SC_18_c_2", "SC_18_c_3", "SC_23", "SC_23_3_1", "SC_23_3_2", "SC_23_3_3", "SC_24_1", "SC_24_2", "SC_24_3", "SC_24_4", "SC_24_5", "SC_28_1_1", "SC_28_1_2", "SC_28_1_3", "SC_7_a_1", "SC_7_a_2", "SC_7_a_3", "SC_7_a_4", "SC_7_b_1", "SC_7_b_2", "SC_7_C", "SC_8_1", "SC_8_2", "SI_10_1", "SI_10_2", "SI_13_a_1", "SI_13_a_2", "SI_13_b_1", "SI_13_b_2", "SI_13_b_3", "SI_2_3_a", "SI_2_3_b_1", "SI_2_3_b_2", "SI_2_a_1", "SI_2_a_2", "SI_2_a_3", "SI_2_b_1", "SI_2_b_2", "SI_2_c_1", "SI_2_c_2", "SI_2_c_3", "SI_2_c_4", "SI_2_d", "SI_4_a_1_1", "SI_4_a_1_2_a", "SI_4_a_1_2_b", "SI_4_a_2_1", "SI_4_a_2_2", "SI_4_a_2_3", "SI_4_b_1", "SI_4_b_2", "SI_4_c_1", "SI_4_c_2", "SI_4_d_1", "SI_4_d_2", "SI_4_d_3", "SI_4_e", "SI_4_f", "SI_4_g_1", "SI_4_g_2", "SI_4_g_3", "SI_4_g_4_a", "SI_4_g_4_b"]
   if "test" not in ctl %}
  {# Are we changing families? #}
  {% if ctl.split("_")[0].upper() != meta["current_family"].upper() %}
    {% set var_ignore = meta.update({"current_family": ctl.split("_")[0].upper()}) %}
    <h2 style="margin-bottom: 30px;">{{meta["current_family"]|upper}}</h2>
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
      <h3 style="">{{meta["current_control"]|upper}}</h3>
        <p>CONTROL DESCRIPTION HERE</p>
      <table style="margin-bottom: 1.0em; width: 100%;">
        <tr>
          <td colspan="2" style="color: white; background-color: rgb(31, 58, 105); text-align:center;">
          {{meta["current_control"]|upper}}: What is the solution and how is it implemented?
        </td></tr>
  {% endif %}
  {% set c_name_part = "{}-{}".format(odl[3].upper(), " ".join(odl[4:])) %}
  <tr>
    <td style="width: 125px;background-color: rgb(219, 228, 244);font-weight:bold;">{{c_name_part}}</td>
    <td>
      {% for se in ["se_aws_elk", "se_aws_auditing_splunk_elk", "se_aws_ci_cd_jenkins_gitlab_aqua_sonarqube", "se_ciso_policy_soc_stp", "se_system_level"] %}
        {% if project[se] %}
          {% for od in project[se].output_documents if not "test" in od %}
            {% if ctl_od_title == od %}
              {% set odl = od.split('_') %}
              {% set c_name_part = "{}-{}".format(odl[3].upper(), " ".join(odl[4:])) %}
             <div class="soft" style="font-style: italic;">{{project[se]}}</div>
              <quote>
                {{project[se].output_documents[od]}}
              </quote>
            {% endif %}
          {% endfor %}<!-- /for od in -->
        {% else %}
          <div style="color:#aaa;">&nbsp;{{se}} not completed</div>
        {% endif %}
      {% endfor %}<!-- /for se in -->
      </td>
  </tr>
  {% if not loop.last %}
    {% if loop.nextitem.split("_")[0].upper() != meta["current_family"].upper() %}
      </table>
    {% endif %}
  {% endif %}
{% endfor %}<!-- /for ctl in -->
<!-- /Security Controls -->

