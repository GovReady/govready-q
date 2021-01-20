id: poam_report.md
format: markdown
title: POAM Report
...

<center>
<h1 class="title">{{project.system_info.system_name}}<br/>Plans of Action and Milestones<br/>(POA&M) Report</h1>
<img style="max-width:70%;height:auto;" src="{{static_asset_path_for('app.png')}}">
<br></br>
<h2>Prepared for</br/>{{project.system_info.system_org}}</h2>
<br></br>
{{project.poam_doc.poam_date}}
</center>




* * *

## Table of Contents

*   [1. POA&M](#poa&m)
    *   [1.1 Introduction](#introduction)
    *   [1.2 Plan of Action and Milestone Table](#poamtable)

* * *

## 1. POA&M
### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1.1 Introduction
The Plan of Action and Milestones (POA&M) report lists the significant security issues associated with the system and details the proposed plan and schedule for correcting and/or mitigating them.

The POA&M information is presented as a table in section 1.2. The columns of the table are defined as follows:

* Weakness: The security issue associated with the system
* POC: Name of role of the individual responsible for implementing corrective action
* Resources Required: The resources required to correct/mitigate the security issue
* Schedule Completion Date: The date scheduled to complete the tasks for correcting the security issue 
* Milestones with Completion Dates: Planned tasks required to correct/mitigate the security issue
* Change to Milestones: Any changes made to the original milestones
* Source Identifying Weakness: Indication of how the security issue has been reported
* Status: Current status of corrective actions; Ongoing or Completed (with Completion Date)
* Comments: Any associated notes regarding implementation

<br></br>

### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1.2 Plan of Action and Milestone Table
<br>

{% set count = [ ] %}
{% for poam in project.poam_description %}
{% set __ = count.append(1) %}
<strong>POA&M {{count|length}}</strong>
{{poam.poam_grid_01}}{{poam.poam_grid_02}}
<br></br><br></br>
{% endfor %}






