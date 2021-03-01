id: cp_fedramp01
title: Contingency Plan and Test
format: markdown
source: https://www.fedramp.gov/assets/resources/templates/SSP-A06-FedRAMP-ISCP-Template.docx
...

<style type="text/css" scoped>
    h2 { border-bottom:1px solid #888; }
    h3 { border-bottom: 0.5px solid #aaa; }
    h4 { margin-top: 15px; font-weight: bold; font-size: 1em; }
    blockquote { color: #666; font-size:0.8em; margin: 0 10px; }
    .notice {color: red; font-size:3.0em; text-align:center; transform: scaleY(.85);
    font-weight: bold;}
    table { border: none; border-collapse: collapse; }
    th, td { border: 1px solid #888; padding: 15px; text-align: left;}
    @media all {
        .page-break     { display: none; }
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
<img style="max-width:70%;height:auto;" src="{{static_asset_path_for('app.png')}}">
<h1 class="title">{{project.system_info.system_name}}<br/>Contingency Plan</h1>
</center>

<div class="page-break">
  <table class="footer">
    <tr>
      <td width="33%"><strong>{{project.system_info.system_short_name}}</strong></td>
      <td width="34%" style="text-align: center;"><strong>LIMITED OFFICIAL USE</strong></td>
      <td width="33%" style="text-align: right;"> <!-- page number --></td>
    </tr><tr>
      <td colspan="3">Contingency Plan</td>
    </tr>
  </table>
</div>

* * *

## Table of Contents

*   [Contingency Plan](#cp)
    *   [Section 1: Introduction and Purpose](#intro)
    *   [Section 2: Concept of Operations](#conops)
    *   [Section 3: Activation and Notification](#activationnotification)
    *   [Section 4: Recovery](#recovery)
    *   [Section 5: Reconstitution](#reconstitution)
    *   [Section 6: Contingency Plan Testing](#cptesting)

* * *


CONTINGENCY PLAN APPROVALS

{{project.cp_introduction.approvals}}

# 1. Introduction and Purpose

{{project.cp_introduction.q01}}


## 1.1 Applicable Laws and Regulations

The laws and regulations and regulations are applicable to Contingency planning:

{{project.cp_introduction.q02}}

## 1.2 Applicable Standards and Guidance

The following standards and guidance are useful for understanding Contingency planning:

{{project.cp_introduction.q03}}

## 1.3 Information System Name and Identifier

This ISCP applies to the {{project.system_info.system_name}} (Information System Abbreviation) which has a unique identifier as noted in Table 1‑3 Information System Name and Title.

Table 1‑3 Information System Name and Title

<table border="1">
  <tr><th> Unique Identifier </th><th> Information System Name </th><th> Information System Abbreviation </th></tr>
  <tr><td> {{project.fisma_level.application_number}}     </td><td> {{project.system_info.system_name}} </td><td> {{project.system_info.system_short_name}} </td></tr>
</table>

## 1.4 Scope

This ISCP has been developed for ISA which is classified as a impact system, in accordance with Federal Information Processing Standards (FIPS) 199.  FIPS 199 provides guidelines on determining potential impact to organizational operations and assets, and individuals through a formula that examines three security objectives: confidentiality, integrity, and availability.

* Disruption at the primary work site {{project.system_info.primary_agency_admin_site}}
* Disruption at the vendor site
* Disruption to the organizational network connection that direct circuits that connect users to the vendor site

This ITCP does not apply to the following situations:

* **Overall recovery and continuity of business operations.** The Business Resumption Plan (BRP) and Continuity of Operations (COOP) Plans are appended to this plan.
* **Emergency evacuation of personnel.** The Occumant Emergency Plan (OEP) is appended to this plan. As stated, this appended plan addresses occupant emergencies and is not the information system Contingency Plan.

## 1.5 Assumptions

{{project.cp_introduction.q05}}

<!--
- The Uninterruptable Power Supply (UPS) will keep the system up and running for after _Enter Number_ .
- The generators will kick in after _Enter Number_ from time of a power failure.
- Current backups of the application software and data are intact and available at the offsite storage facility in _Enter City_, _Enter State_.
- The backup storage capability is approved and has been accepted by the Authorizing Official (AO).
- The {{project.system_info.system_name}} is inoperable if it cannot be recovered within _Enter Number_ RTO hours.
- Key personnel have been identified and are trained annually in their roles.
- Key personnel are available to activate the ISCP.
- CSP Name defines circumstances that can inhibit recovery and reconstitution to a known state.
-->

# 2 Concept of Operations

This section provides details about the {{project.system_info.system_name}}, an overview of the three phases of the ISCP (Activation and Notification, Recovery, and Reconstitution), and a description of the roles and responsibilities of key personnel during contingency operations.

## 2.1 System Description

{{project.cp_introduction.q08}}

## 2.2 Three Phases

{{project.cp_questionnaire.q09}}

## 2.3 Data Backup Readiness Information

A common understanding of data backup definitions is necessary in order to ensure that data restoration is successful.  CSP Name recognizes different types of backups, which have different purposes, and those definitions are found in Table 2‑1 Backup Types.

Table 2‑1 Backup System Components

<table border="1">
<tr><td>Backup Type</td><td>Description</td></tr>
<tr><td>Full Backup</td><td>A full backup is the starting point for all other types of backup and contains all the data in the folders and files that are selected to be backed up.  Because full backup stores all files and folders, frequent full backups result in faster and simpler restore operations.</td></tr>
<tr><td>Differential Backup</td><td>Differential backup contains all files that have changed since the last FULL backup.  The advantage of a differential backup is that it shortens restore time compared to a full back up or an incremental backup.  However, if the differential backup is performed too many times, the size of the differential backup might grow to be larger than the baseline full backup.</td></tr>
<tr><td>Incremental Backup</td><td>Incremental backup stores all files that have changed since the last FULL, DIFFERENTIAL OR INCREMENTAL backup.  The advantage of an incremental backup is that it takes the least time to complete.  However, during a restore operation, each incremental backup must be processed, which may result in a lengthy restore job.</td></tr>
<tr><td>Mirror Backup</td><td>Mirror backup is identical to a full backup, with the exception that the files are not compressed in zip files and they cannot be protected with a password.  A mirror backup is most frequently used to create an exact copy of the source data.</td></tr>
</table>

</br>

The hardware and software components used to create the {{project.system_info.system_name}} backups are noted in Table 2‑2 Backup System Components.

</br>

Table 2‑2 Backup System Components

{{project.cp_questionnaire.q10_backup_system_components|safe}}

</br>

Table 2‑3 Back-Up Storage Location shows the offsite storage facility location of current backups of the {{project.system_info.system_name}} system software and data.

</br>

Table 2‑3 Back-Up Storage Location

{{project.cp_questionnaire.q10_backup_storage_location|safe}}

Personnel who are authorized to retrieve backups from the offsite storage location, and may authorize the delivery of backups, are noted in D.1Appendix – Alternate Storage Site Information.


## 2.4 Site Readiness Information

CSP Name recognizes different types of alternate sites, which are defined in Table 2‑4 Alternative Site Types.

Table 2‑4 Alternative Site Types

<table border="1">
  <tr>
    <th class="tg-lboi">Type of Site</th>
    <th class="tg-lboi">Descriptions</th>
  </tr>
  <tr>
    <td class="tg-0lax">Cold Sites</td>
    <td class="tg-0lax">Cold Sites are typically facilities with adequate space and infrastructure (electric power, telecommunications connections, and environmental controls) to support information system recovery activities.</td>
  </tr>
  <tr>
    <td class="tg-0lax">Warm Sites</td>
    <td class="tg-0lax">Warm Sites are partially equipped office spaces that contain some or all of the system hardware, software, telecommunications, and power sources.</td>
  </tr>
  <tr>
    <td class="tg-0lax">Hot Sites</td>
    <td class="tg-0lax">Hot Sites are facilities appropriately sized to support system requirements and configured with the necessary system hardware, supporting infrastructure, and support personnel.</td>
  </tr>
  <tr>
    <td class="tg-0lax">Mirrored Sites</td>
    <td class="tg-0lax">Mirrored Sites are fully redundant facilities with automated real-time information mirroring.  Mirrored sites are identical to the primary site in all technical respects.</td>
  </tr>
</table>

Alternate facilities have been established for the {{project.system_info.system_name}} as noted in Table 2‑4 Alternative Site Types.

</br>

Table 2‑5 Primary and Alternative Site Locations

{{project.cp_questionnaire.q10_primary_alternate_site|safe}}

## 2.5 Roles and Responsibilities

CSP Name establishes multiple roles and responsibilities for responding to outages, disruptions, and disasters for the {{project.system_info.system_name}}.  Individuals who are assigned roles for recovery operations collectively make up the Contingency Plan Team and are trained annually in their duties.  Contingency Plan Team members are chosen based on their skills and knowledge.

The Contingency Plan Team consists of personnel who have been selected to perform the roles and responsibilities described in the sections that follow.  All team leads are considered key personnel.

### 2.5.1 Contingency Planning Director (CPD)

{{project.cp_questionnaire.q12}}

### 2.5.2 Contingency Planning Coordinator (CPC)

{{project.cp_questionnaire.q12cpc}}

### 2.5.3 Security Coordinator (SC)

{{project.cp_questionnaire.q12sc}}

### 2.5.4 Plan Distribution and Availability

{{project.cp_activation.q13}}

### 2.5.10 Line of Succession/Alternates Roles

The CSP Name sets forth an order of succession, in coordination with the order set forth by the organization to ensure that decision-making authority for the {{project.system_info.system_name}} ISCP is uninterrupted.

In order to preserve the continuity of operations, individuals designated as key personnel have been assigned an individual who can assume the key personnel&#39;s position if the key personnel is not able to perform their duties.  Alternate key personnel are named in a line of succession and are notified and trained to assume their alternate role, should the need arise.  The line of succession for key personnel can be found in Appendix B – Key Personnel and Team Member Contact List.

# 3 Activation and Notification

The activation and notification phase defines initial actions taken once the {{project.system_info.system_name}} disruption has been detected or appears to be imminent.  This phase includes activities to notify recovery personnel, conduct an outage assessment, and activate the ISCP.

At the completion of the Activation and Notification Phase, key {{project.system_info.system_name}} ISCP staff will be prepared to perform recovery measures to restore system functions.

## 3.1 Activation Criteria and Procedure

{{project.cp_activation.q16}}

Personnel/roles listed in Table 3‑1 Personnel Authorized to Activate the ISCP are authorized to activate the ISCP.

</br>

Table 3‑1 Personnel Authorized to Activate the ISCP

{{project.cp_activation.q13_activation_personnel}}


## 3.2 Notification Instructions

{{project.cp_activation.q17_notification_instructions}}

Contact information for key personnel is located in BAppendix – Key Personnel and Team Member Contact List.

## 3.3 Outage Assessment

Following notification, a thorough outage assessment is necessary to determine the extent of the disruption, any damage, and expected recovery time.  This outage assessment is conducted by {{project.cp_activation.q17_outage_assessment_role}}.  Assessment results are provided to the Contingency Planning Coordinator to assist in the coordination of the recovery effort.

{{project.cp_activation.q17_outage_assessment}}

# 4 Recovery

The recovery phase provides formal recovery operations that begin after the ISCP has been activated, outage assessments have been completed (if possible), personnel have been notified, and appropriate teams have been mobilized.  Recovery phase activities focus on implementing recovery strategies to restore system capabilities, repair damage, and resume operational capabilities at the original or an alternate location.  At the completion of the recovery phase, {{project.system_info.system_name}} will be functional and capable of performing the functions identified in Section 4.1 Sequence of Recovery Operations of the plan.

## 4.1 Sequence of Recovery Operations

{{project.cp_recovery.q20}}

## 4.2 Recovery Procedures

{{project.cp_recovery.q21_recovery_procedures}}

## 4.3 Recovery Escalation Notices/Awareness

Notifications during recovery include problem escalation to leadership and status awareness to system owners and users. This section describes the procedures for handling escalation notices that define and describe the events, thresholds, or other types of triggers that may require additional action.

{{project.cp_recovery.q22_escalation_notices}}

# 5 Reconstitution

Reconstitution is the process by which recovery
activities are completed and normal system operations are resumed.  If the original
facility is unrecoverable, the activities in this phase can also be applied to
preparing a new permanent location to support system processing requirements.
A determination must be made whether the system has undergone significant change
and will require reassessment and reauthorization.  The phase consists of two
major activities: (1) validating successful reconstitution and (2) deactivation
of the plan.

Concurrent processing is the process of running a system at two
separate locations concurrently until there is a level of assurance that the
recovered system is operating correctly and securely.

## 5.1 Data Validation Testing

Validation data testing is the process of testing and validating data to ensure
that data files or databases have been recovered completely at the permanent location.

{{project.cp_reconstitution.q25_data_validation_testing}}

## 5.2 Functional Validation

Functionality testing is a process for verifying that all system functionality\nhas
been tested, and the system is ready to return to normal operations.

{{project.cp_reconstitution.q26_functional_validation_testing}}

## 5.3 Recovery Declaration

Upon successfully completing testing and validation,
the {{project.cp_reconstitution.role_approve_recovery}} will formally declare recovery efforts complete,
and that {{project.system_info.system_name}} is in normal operations.  {{project.system_info.system_name}}
business and technical POCs will be notified of the declaration by the Contingency
Plan Coordinator.  The recovery declaration statement notifies the Contingency
Plan Team and executive management that the {{project.system_info.system_name}}
has returned to normal operations.

## 5.4 User Notification

After the recovery
declaration statement is made, notifications are sent to userand customers.
Notifications to customers are made in accordance with predeterminenotification
procedures.

{{project.cp_reconstitution.cp_user_notification}}

## 5.5 Cleanup

Cleanup is the process
of cleaning up or dismantling any temporary recovery locations, restocking supplies
used, returning manuals or other documentation to their original locations, and
readying the system for a possible future contingency event.

{{project.cp_reconstitution.cp_cleanup}}

</br>

Table
5‑1 Cleanup Roles and Responsibilities

{{project.cp_reconstitution.cp_cleanup_roles}}

## 5.6 Returning Backup Media

It is important that all backup and installation
media used during recovery be returned to the off-site data storage location.

The following procedures must be followed to return backup and installation media\nto
its offsite data storage location.

{{project.cp_reconstitution.cp_returning_backup}}

## 5.7 Backing-Up
Restored Systems

As soon as reasonable following recovery, the system must
be fully backed up and a new copy of the current operational system stored for
future recovery efforts.  This full backup is then kept with other system backups.

The procedures for conducting a full system backup are:

{{project.cp_reconstitution.cp_backingup_restored_systems}}

## 5.8 Event Documentation

It is important that all recovery events be well-documented,
including actions taken and problems encountered during the recovery and reconstitution
effort.  Information on lessons learned must be included in the annual update
to the ISCP.  It is the responsibility of each ISCP team or person to document
their actions during the recovery event.

Table 5‑2 lists the responsibility of each ISCP team or person to document their actions during the recovery event.

Table 5‑2 Event Documentation Responsibility

<table class="tg">
  <tr>
    <th class="tg-lboi">Role Name</th>
    <th class="tg-lboi">Documentation Responsibility</th>
  </tr>
  <tr>
    <td class="tg-0lax">{{project.cp_reconstitution.cp_role_activity_log}}</td>
    <td class="tg-0lax">Activity Log</td>
  </tr>
  <tr>
    <td class="tg-0lax">{{project.cp_reconstitution.cp_role_testing}}</td>
    <td class="tg-0lax">Functionality and Data Testing Results</td>
  </tr>
  <tr>
    <td class="tg-0lax">{{project.cp_reconstitution.cp_role_lessons_learned}}</td>
    <td class="tg-0lax">Lessons Learned</td>
  </tr>
  <tr>
    <td class="tg-0lax">{{project.cp_reconstitution.cp_role_after_action_report}}</td>
    <td class="tg-0lax">After Action Report</td>
  </tr>
</table>


# 6 Contingency Plan Testing

Contingency Plan operational tests of the {{project.system_info.system_name}} are performed {{project.cp_introduction.q08b_test_frequency}}.

</br>

A Contingency Plan Test Report is documented after each annual test.  A template for the Contingency Plan Test Report is found in Appendix G – Contingency Plan Test Report.
