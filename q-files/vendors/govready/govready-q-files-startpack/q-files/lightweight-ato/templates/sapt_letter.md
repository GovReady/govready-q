id: sapt_letter.md
format: markdown
title: Security Authorization Package Transmittal Letter
...

<center>
<h1 class="title">{{project.system_info.system_name}}<br/>Security Authorization Package Transmittal Letter<br/>(SAPT) Letter</h1>
<img style="max-width:70%;height:auto;" src="{{static_asset_path_for('app.png')}}">
<br></br>
<h2>Prepared for</br/>{{project.system_info.system_org}}</h2>
<br></br>
{{project.sapt_letter.sapt_letter_date}}
</center>




* * *

Date: {{project.sapt_letter.sapt_letter_date}}

From: {{project.system_info.system_owner}}, System Owner

Thru: {{project.system_info_poc.system_security_name}}, Information System Security POC

To: {{project.system_info_poc.system_ao_name}}

Subject: Security Authorization Package for {{project.system_info.system_name}}

</br>

A security assessment of {{project.system_info.system_name}} and its constituent subsystem-level components {if applicable} located at {{project.system_info.primary_agency_admin_site}} has been conducted in accordance with Office of Management and Budget Circular A-130, Appendix III, Security of Federal Automated Information Resources , NIST Special Publication 800-37, Guide for Applying the Risk Management Framework to Federal Information Systems, and the Department of Homeland Security Headquarters (DHS HQ) policy on security authorization. The attached security authorization package contains: (i) current Security Plan, (ii) Security Assessment Report, and (iii) Plan of Action and Milestones.   

The security controls listed in the Security Plan have been assessed by {{project.sapt_letter.sapt_letter_assessor}} using the assessment methods and procedures described in the Security Assessment Report to determine the extent to which the controls are implemented correctly, operating as intended, and producing the desired outcome of meeting the security requirements for the system. The Plan of Action and Milestones describes the corrective measures that have been implemented or are planned to address any deficiencies in the security controls for the information system and to reduce or eliminate known vulnerabilities.

</br>

<input type="textfield"/></br>
Signature

{{project.system_info.system_owner}}, System Owner of {{project.system_info.system_name}}




