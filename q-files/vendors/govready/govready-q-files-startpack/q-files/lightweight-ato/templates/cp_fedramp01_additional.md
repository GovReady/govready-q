### 2.5.3 Outage and Damage Assessment Lead (ODAL)

The ODAL performs the following duties:

- Determines if there has been loss of life or injuries
- Assesses the extent of damage to the facilities and the information systems
- Estimates the time to recover operations
- Determines accessibility to facility, building, offices, and work areas
- Assesses the need for and adequacy of physical security/guards
- Advises the Security Coordinator that physical security/guards are required
- Identifies salvageable hardware
- Maintains a log/record of all salvageable equipment
- Supports the cleanup of the data center following an incident
- Develops and maintains a Damage Assessment Plan
- Estimates levels of outside assistance required
- Reports updates, status, and recommendations to the CPC
- Designates key personnel

### 2.5.4 Hardware Recovery Team (HRT)

The hardware recovery team performs the following duties:

- Installs hardware and connects power
- Runs cables and wiring as necessary
- Makes arrangements to move salvageable hardware to other locations as necessary
- Ensures electrical panels are operational
- Ensures that fire suppression system is operational
- Communicates with hardware vendors as needed (CAppendix – Vendor Contact List)
- Creates log of missing and required hardware
- Advises the PLC if new hardware should be purchased
- Connects network cables
- Connects wireless access points

### 2.5.5 Software Recovery Team (SRT)

The software recovery team performs the following duties:

- Installs software on all systems at alternate site
- Performs live migrations to alternate site prior to predictable disasters and outages
- Installs servers in the order described in the BIA (MAppendix – Business Impact Analysis)
- Communicate with software vendors as needed (CAppendix – Vendor Contact List)
- Advises the PLC if new software needs to be purchased
- Creates log of software installation problems
- Restore systems from most current backup media
- Maintains current system software configuration information in an off-site storage facility

### 2.5.6 Telecommunications Team (TC)

The Telecomm team performs the following duties:

- Assesses the need for alternative communications
- Communicates Internet connectivity requirements with providers
- Communicates with telephone vendors as needed
- Establishes communications between the alternate site and the users
- Coordinates transportation of salvageable telecomm equipment to the alternative site
- Plans for procuring new hardware and telecommunication equipment
- Advises the PLC if new equipment needs to be purchased
- Retrieves communications configuration from the off-site storage facility
- Plans, coordinates and installs communication equipment as needed at the alternate site
- Maintains plan for installing and configuring VOIP
- Maintains current telecommunications configuration information at off-site storage facility

### 2.5.7 Procurement and Logistics Coordinator (PLC)

The PLC performs the following duties:

- Procures new equipment and supplies as necessary
- Prepares, coordinates, and obtains approval for all procurement requests
- Authorizes purchases up to _Enter $ amount_ for recovery operations
- Ensures that equipment and supplies are delivered to locations
- Coordinates deliveries
- Updates the CPC with status
- Works with the CPC to provide transportation for staff as needed
- Ensures details of administering emergency funds expenditures are known.
- Processes requests for payment of all invoices related to the incident
- Arranging for travel and lodging of staff to the alternate site as needed
- Procures telephone equipment and leased lines as needed
- Procures alternate communications for teams as needed



## 4 Recovery

The recovery phase provides formal recovery operations that begin after the ISCP has been activated, outage assessments have been completed (if possible), personnel have been notified, and appropriate teams have been mobilized.  Recovery phase activities focus on implementing recovery strategies to restore system capabilities, repair damage, and resume operational capabilities at the original or an alternate location.  At the completion of the recovery phase, {{project.system_info.system_name}} will be functional and capable of performing the functions identified in Section 4.1Sequence of Recovery Operations of the plan.

## 4.1 Sequence of Recovery Operations

The following activities occur during recovery of {{project.system_info.system_name}}:

Instruction: Modify the following list as appropriate for the system recovery strategy.
Delete this instruction from your final version of this document.

1. Identification of recovery location (if not at original location)
2. Identification of required resources to perform recovery procedures
3. Retrieval of backup and system installation media
4. Recovery of hardware and operating system (if required)
5. Recovery of system from backup and system installation media
6. Implementation of transaction recovery for systems that are transaction-based

## 4.2 Recovery Procedures

The following procedures are provided for recovery of {{project.system_info.system_name}} at the original or established alternate location.  Recovery procedures are outlined per team and must be executed in the sequence presented to maintain an efficient recovery effort.

Instruction:  Provide general procedures for the recovery of the system from backup media.  Specific keystroke-level procedures may be provided in an appendix.  If specific procedures are provided in an appendix, a reference to that appendix must be included in this section.  Teams or persons responsible for each procedure must be identified.
Delete this instruction from your final version of this document.

## 4.3 Recovery Escalation Notices/Awareness

Notifications during recovery include problem escalation to leadership and status awareness to system owners and users.  This section describes the procedures for handling escalation notices that define and describe the events, thresholds, or other types of triggers that may require additional action.

Instruction: Provide appropriate procedures for escalation notices during the recovery efforts.  Teams or persons responsible for each escalation/awareness procedure must be identified. Delete this instruction from your final version of this document.

# 5 Reconstitution

Reconstitution is the process by which recovery activities are completed and normal system operations are resumed.  If the original facility is unrecoverable, the activities in this phase can also be applied to preparing a new permanent location to support system processing requirements.  A determination must be made whether the system has undergone significant change and will require reassessment and reauthorization.  The phase consists of two major activities: (1) validating successful reconstitution and (2) deactivation of the plan.

Concurrent processing is the process of running a system at two separate locations concurrently until there is a level of assurance that the recovered system is operating correctly and securely.

## 5.1 Data Validation Testing

Validation data testing is the process of testing and validating data to ensure that data files or databases have been recovered completely at the permanent location.

Instruction: Describe procedures for testing and validation of data to ensure that data is correct and up to date as of the last available backup.  Teams or persons responsible for each procedure must be identified.  An example of a validation data test for a moderate-impact system would be to compare a database audit log to the recovered database to make sure all transactions were properly updated.  Detailed data test procedures may be provided in FAppendix – System Validation Test Plan.
Delete this instruction from your final version of this document.

## 5.2 Functional Validation Testing

Functionality testing is a process for verifying that all system functionality has been tested, and the system is ready to return to normal operations.

Instruction: Describe procedures for testing and validation functional and operational aspects of the system.
Delete this instruction from your final version of this document.

## 5.3 Recovery Declaration

Upon successfully completing testing and validation, the _Insert role name_ will formally declare recovery efforts complete, and that {{project.system_info.system_name}} is in normal operations.  {{project.system_info.system_name}} business and technical POCs will be notified of the declaration by the Contingency Plan Coordinator.  The recovery declaration statement notifies the Contingency Plan Team and executive management that the {{project.system_info.system_name}} has returned to normal operations.

## 5.4 User Notification

After the recovery declaration statement is made, notifications are sent to users and customers.  Notifications to customers are made in accordance with predetermined notification procedures.

Instruction: Describe the notification procedures.  Ensure that the procedures described are consistent with Service Level Agreements and contracts.
Delete this instruction from your final version of this document.

## 5.5 Cleanup

Cleanup is the process of cleaning up or dismantling any temporary recovery locations, restocking supplies used, returning manuals or other documentation to their original locations, and readying the system for a possible future contingency event.

Instruction: Describe cleanup procedures and tasks including cleanup roles and responsibilities.  Insert cleanup responsibilities in Table 5‑1 Cleanup Roles and Responsibilities.  Add additional rows as needed.
Delete this instruction from your final version of this document.

Table 5‑1 Cleanup Roles and Responsibilities

| Role | Cleanup Responsibilitie --- |
| Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. |

## 5.6 Returning Backup Media

It is important that all backup and installation media used during recovery be returned to the off-site data storage location.

Instruction: Provide procedures for returning retrieved backup or installation media to its offsite data storage location.  This may include proper logging and packaging of backup and installation media, preparing for transportation, and validating that media is securely stored at the offsite location.
Delete this instruction from your final version of this document.

The following procedures must be followed to return backup and installation media to its offsite data storage location.

## 5.7 Backing-Up Restored Systems

As soon as reasonable following recovery, the system must be fully backed up and a new copy of the current operational system stored for future recovery efforts.  This full backup is then kept with other system backups.

Instruction: Provide appropriate procedures for ensuring that a full system backup is conducted within a reasonable time frame, ideally at the next scheduled backup period.
Delete this instruction from your final version of this document.

The procedures for conducting a full system backup are:

## 5.8 Event Documentation

It is important that all recovery events be well-documented, including actions taken and problems encountered during the recovery and reconstitution effort.  Information on lessons learned must be included in the annual update to the ISCP.  It is the responsibility of each ISCP team or person to document their actions during the recovery event.

Instruction: Provide details about the types of information each ISCP team member is required to provide for the purpose of updating the ISCP.  Types of documentation that must be generated and collected after a recovery operation include: activity logs (including recovery steps performed and by whom, the time the steps were initiated and completed, and any problems or concerns encountered while executing activities); functionality and data testing results; lessons learned documentation; and an After Action Report.
Delete this instruction from your final version of this document.

Table 5‑2 Event Documentation Responsibility lists the responsibility of each ISCP team or person to document their actions during the recovery event.

Table 5‑2 Event Documentation Responsibility

| Role Name | Documentation Responsibilit --- |
| Click here to enter text. | Activity log |
| Click here to enter text. | Functionality and data testing results |
| Click here to enter text. | Lessons learned |
| Click here to enter text. | After Action Report |

# 6 Contingency Plan Testing

Contingency Plan operational tests of the {{project.system_info.system_name}} are performed annually.  A Contingency Plan Test Report is documented after each annual test.  A template for the Contingency Plan Test Report is found in GAppendix – Contingency Plan Test Report.
-->

<!--
# Appendices

Appendix A Acronyms and Definitions

Appendix B Key Personnel and Team Member Contact List

Appendix C Vendor Contact List

Appendix D Alternate Storage, Processing, &amp; Telecommunications Site Information

Appendix E Alternate Processing Procedures

Appendix F System Validation Test Plan

Appendix G Contingency Plan Test Report

Appendix H Diagrams

Appendix I Hardware and Software Inventory

Appendix J System Interconnections

Appendix K Test and Maintenance Schedule

Appendix L Associated Plans and Procedures

Appendix M Business Impact Analysis

1. Acronyms and Definitions

The master list of FedRAMP acronym and glossary definitions for all FedRAMP templates is available on the FedRAMP website [Documents](https://www.fedramp.gov/resources/documents-2016/) page under Program Overview Documents.

Please send suggestions about corrections, additions, or deletions to info@fedramp.gov.

1. Appendix – Key Personnel and Team Member Contact List

Instruction: All key personnel (and alternates) and Contingency Plan Team members designated in section 2.5 must be noted on this contact list.  The ISCP must be distributed to everyone on this list.
Delete this instruction from your final version of this document.

Table B‑1 Key Personnel and Team Member Contact List includes Contingency Plan Team members designated in Section 2.5Roles and Responsibilities and the ISCP has been distributed to everyone in this list.

Table B‑1 Key Personnel and Team Member Contact List

| Role | Name and Home Address | Email | Phon --- | --- | --- |
| Contingency Plan Director | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Alternate Contingency Plan Director | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Contingency Plan Coordinator | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Alternate Contingency Plan Coordinator | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Outage and Damage Assessment Lead | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Alternate Outage and Damage Assessment Lead | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Procurement and Logistics Coordinator | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Alternate Procurement and Logistics Coordinator | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |

1. Appendix – Vendor Contact List

Table C‑2 Vendor Contact List includes the vendors associated with the ISCP.

Table C‑2 Vendor Contact List

| Vendor | Product or Service License #, Contract #, Account #, or SLA | Phon --- | --- |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |
| Click here to enter text. | Click here to enter text. | Primary: Primary Phone.Alternate:Secondary Phone |

1. Appendix Alternate Storage, Processing and Provisions

1. Appendix – Alternate Storage Site Information

Table D‑3 Alternate Storage Site Information lists the alternative site location and details about schedules, data types and contacts.

Table D‑3 Alternate Storage Site Information

| Storage Sit
| Address of alternate storage site | Click here to enter text. |
| Distance from primary facility | Click here to enter text. |
| Is alternate storage facility owned by the organization or is a third-party storage provider? | Click here to enter text. |
| Points of contact at alternate storage location | Click here to enter text. |
| Delivery schedule and procedures for packaging media for delivery to alternate storage facility | Click here to enter text. |
| Procedures for retrieving media from the alternate storage facility | Click here to enter text. |
| Names and contact information for those persons authorized to retrieve media | Click here to enter text. |
| Potential accessibility problems to the alternate storage site in the event of a widespread disruption or disaster (e.g.,  roads that might be closed, anticipate traffic) | Click here to enter text. |
| Mitigation steps to access alternate storage site in the event of a widespread disruption or disaster | Click here to enter text. |
| Types of data located at alternate storage site, including databases, application software, operating systems, and other critical information system software | Click here to enter text. |

1. Appendix – Alternate Processing Site Information

Table D‑4 Alternate Processing Site Information

Table D‑4 Alternate Processing Site Information

| Alternate Processing Sit
| Address | Click here to enter text. |
| Distance from primary facility | Click here to enter text. |
| Alternate processing site is owned by the organization or is a third-party site provider | Click here to enter text. |
| Point of Contact | Click here to enter text. |
| Procedures for accessing and using the alternate processing site, and access security features of alternate processing site | Click here to enter text. |
| Names and contact information for those persons authorized to go to alternate processing site | Click here to enter text. |
| Type of Site (from Table 2‑4 Alternative Site Types) | |
| Mitigation steps to access alternate processing site in the event of a widespread disruption or disaster | Click here to enter text. |

1. Appendix – Alternate Telecommunications Provisions

Table D‑5 Alternate Telecommunications Provisions show the details for the alternate communications vendors, agreements and capacity.

Table D‑5 Alternate Telecommunications Provisions

| Alternate Telecommunication
| Name and contact information of alternate telecommunications vendors by priority | Click here to enter text. |
| Agreements currently in place with alternate communications vendors | Click here to enter text. |
| Contracted capacity of alternate telecommunications | Click here to enter text. |
| Names and contact information of individuals authorized to implement or use alternate telecommunications | Click here to enter text. |

1. Appendix – Alternate Processing Procedures

Instruction: This section must identify any alternate manual or technical processing procedures available that allow the business unit to continue some processing of information that would normally be done by the affected system.  Examples of alternate processes include manual forms processing, input into workstations to store data until it can be uploaded and processed, or queuing of data input.
Delete this instruction from your final version of this document.

1. Appendix – System Validation Test Plan

Instruction: Describe the system acceptance procedures that are performed after the system has been recovered and prior to putting the system into full operation and returned to users.  The System Validation Test Plan may include the regression or functionality testing conducted prior to implementation of a system upgrade or change.  Edit (or replace) the sample validation test plan provided to reflect the actual validation test plan for the system.
Delete this instruction from your final version of this document.

Table F‑6 System Validation Test Plan shows the results of testing after the system has recovered and prior to the system being put into full operation.

Table F‑6 System Validation Test Plan

| Procedure | Expected Results | Actual Results | Successful?   | Performed b --- | --- | --- | --- |
| At the Command Prompt, type in system name | System Log-in Screen appears |   |   |   |
| Log-in as user test user, using password test pass | Initial Screen with Main Menu shows |   |   |   |
| From menu, select                      5-Generate Report | Report Generation Screen shows |   |   |   |
| Select  Current Date Report Select  Weekly Select  To Screen | Report is generated on screen with last successful transaction included |   |   |   |
| Select Close | Report Generation Screen Shows |   |   |   |
| Select Return to Main Menu | Initial Screen with Main Menu shows |   |   |   |
| Select Log-Off | Log-in Screen appears |   |   |   |

1. Appendix – Contingency Plan Test Report

Instruction: This section must include a summary of the last Contingency Plan Test.  The actual procedures used to test the plan must be described in Section 6, not here.
Delete this instruction from your final version of this document.

Table G‑7 Contingency Plan Test Report reflects a summary of the last Contingency Plan Test.  The actual procedures used to test the plan are described in Section 6Contingency Plan Testing.

Table G‑7 Contingency Plan Test Report

| Test Information | Descriptio --- |
| Name of Test | Click here to enter text. |
| System Name | Click here to enter text. |
| Date of Test | Click here to enter text. |
| Team Test Lead and Point of Contact | Click here to enter text. |
| Location Where Conducted | Click here to enter text. |
| Participants | Click here to enter text. |
| Components | Click here to enter text. |
| Assumptions | Click here to enter text. |
| Objectives | ☐ Assess effectiveness of system recovery at alternate site☐ Assess effectiveness of coordination among recovery teams☐ Assess systems functionality using alternate equipment☐ Assess performance of alternate equipment☐ Assess effectiveness of procedures☐ Assess effectiveness of notification procedures |
| Methodology | Click here to enter text. |
| Activities and Results (Action, Expected Results, Actual Results) | Click here to enter text. |
| Post Test Action Items | Click here to enter text. |
| Lessons Learned and Analysis of Test | Click here to enter text. |
| Recommended Changes to Contingency Plan Based on Test Outcomes | Click here to enter text. |

1. Appendix – Diagrams

Instruction: Insert network diagrams, data flow diagrams, and any relevant component diagrams here.  All of the diagrams used must be consistent with those found in the System Security Plan (SSP).
Delete this instruction from your final version of this document.

Figure H‑1 Authorization Boundary Diagram is consistent with Figure 9 1 Authorization Boundary Diagram in the SSP.

[[ IMAGE HERE ]]


Figure H‑1 Authorization Boundary Diagram

Figure H‑2 Network Diagram is consistent with Figure 9-2 Network Diagram in the SSP.

[[ IMAGE HERE ]]



Figure H‑2 Network Diagram

Figure H‑3 Data Flow Diagram is consistent with Figure 10-1 Data Flow Diagram in the SSP.

[[ IMAGE HERE ]]


Figure H‑3 Data Flow Diagram

1. Appendix – Hardware and Software Inventory

Instruction: This section should reference the system&#39;s Integrated Inventory Workbook, which should be maintained and updated monthly by the CSP.

Delete this instruction from your final version of this document.

The Integrated Inventory Workbook, also provided as Attachment 13 of the [[_System Name_]] System Security Plan, provides the complete listing of system components addressed by this Information System Contingency Plan.

The Inventory Template Link can be found on this page: [Templates](https://www.fedramp.gov/resources/templates-3/)



1. Appendix – System Interconnections

Instruction: Provide a system Interconnection Table which must be consistent with the Interconnections Table found in the System Security Plan (SSP).  The Interconnections Table from the System Security Plan can be copied and pasted into this Appendix.
Delete this instruction from your final version of this document.

Table J‑8 System Interconnections below is consistent with SSP Table 11-1 System Interconnections and SSP Table 12 3 CA-3 Authorized Connections.

Table J‑8 System Interconnections

| SP IP Address and Interface | External Organization Name and IP Address of System | External Point of Contact and Phone Number | Connection Security (IPSec VPN, SSL, Certificates, Secure File Transfer etc.) | Data Direction              (incoming, outgoing, or both) | Information Being Transmitted | Ports or Circuit  --- | --- | --- | --- | --- | --- |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |
| Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. | Enter text. |

1. Appendix – Test and Maintenance Schedule

Instruction: All ISCPs must be reviewed and/or tested according to regular schedules.  Provide complete information and a schedule for the testing of the system according to all ISCP security control requirements.
Delete this instruction from your final version of this document.

1. Appendix – Associated Plans and Procedures

Instruction: ISCPs for other systems that either interconnect or support the system must be identified in this Appendix.  The most current version of the ISCP, location of ISCP, and primary point of contact (such as the ISCP Coordinator) must be noted.
Delete this instruction from your final version of this document.

ISCPs for other systems that either interconnect or support the system must be identified in Table L‑9 Associated Plans and Procedures.

Table L‑9 Associated Plans and Procedures

| System Name | Plan Nam --- |
| Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. |

1. Appendix – Business Impact Analysis

Instruction: Insert Business Impact Analysis here.  Please see NIST SP 800-34, Revision 1 for more information on how to conduct a Business Impact Analysis.
Delete this instruction from your final version of this document.

