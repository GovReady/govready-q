id: cp_document_new
title: Contingency Plan and Test
format: markdown
...

# Cover Page


# FedRAMP page


| Street Address | Click here to enter text. |
| Suite/Room/Building | Click here to enter text. |
| City, State, ZIP | Click here to enter text. |


Revision History

Complete 15.6        Attachment 6 – Information System Contingency Plan Revision History in the System Security Plan.  Detail specific changes in the table below.

| Date | Version | Page(s) | Description | Author |
| ---  | ---     | ---     | ---         | ---    |
| | Click | Click | Click here to enter text. | Click |
| | Click | Click | Click here to enter text. | Click |

<!-- How to contact us

For questions about FedRAMP, or for technical questions about this document including how to use it, contact [_info@fedramp.gov_](mailto:info@fedramp.gov)

For more information about the FedRAMP project, see [www.fedramp.gov](http://www.fedramp.gov)
 -->

Table of Contents

(TOC commented out)

<!-- 1        Introduction and Purpose        1

1.1        Applicable Laws and Regulations        1

1.2        Applicable Standards and Guidance        1

1.3        FedRAMP Requirements and Guidance        2

1.4        Information System Name and Identifier        2

1.5        Scope        2

1.6        Assumptions        3

2        Concept of Operations        3

2.1        System Description        4

2.2        Three Phases        4

2.3        Data Backup Readiness Information        4

2.4        Site Readiness Information        6

2.5        Roles and Responsibilities        7

2.5.1        Contingency Planning Director (CPD)        7

2.5.2        Contingency Planning Coordinator        7

2.5.3        Outage and Damage Assessment Lead (Odal)        8

2.5.4        Hardware Recovery Team        8

2.5.5        Software Recovery Team        8

2.5.6        Telecommunications Team        9

2.5.7        Procurement and Logistics Coordinator (Plc)        9

2.5.8        Security Coordinator        9

2.5.9        Plan Distribution and Availability        10

2.5.10        Line of Succession/Alternates Roles        10

3        Activation and Notification        10

3.1        Activation Criteria and Procedure        10

3.2        Notification Instructions        11

3.3        Outage Assessment        11

4        Recovery        11

4.1        Sequence of Recovery Operations        12

4.2        Recovery Procedures        12

4.3        Recovery Escalation Notices/Awareness        12

5        Reconstitution        12

5.1        Data Validation Testing        13

5.2        Functional Validation Testing        13

5.3        Recovery Declaration        13

5.4        User Notification        13

5.5        Cleanup        13

5.6        Returning Backup Media        14

5.7        Backing-Up Restored Systems        14

5.8        Event Documentation        14

6        Contingency Plan Testing        15

A. Acronyms and Definitions        17

B. Appendix – Key Personnel and Team Member Contact List        18

C. Appendix – Vendor Contact List        19

D. Appendix Alternate Storage, Processing and Provisions        20

D.1. Appendix – Alternate Storage Site Information        20

D.2. Appendix – Alternate Processing Site Information        20

D.3. Appendix – Alternate Telecommunications Provisions        21

E. Appendix – Alternate Processing Procedures        22

F. Appendix – System Validation Test Plan        23

G. Appendix – Contingency Plan Test Report        24

H. Appendix – Diagrams        25

I. Appendix – Hardware and Software Inventory        27

J. Appendix – System Interconnections        28

K. Appendix – Test and Maintenance Schedule        29

L. Appendix – Associated Plans and Procedures        30

M. Appendix – Business Impact Analysis        31

List of Figures

Figure H‑1 Authorization Boundary Diagram        25

Figure H‑2 Network Diagram        25

Figure H‑3 Data Flow Diagram        26

List of Tables

Table 1‑1 {{project.system_info.system_name}}; Laws and Regulations        1

Table 1‑2 {{project.system_info.system_name}}; Standards and Guidance        2

Table 1‑3 Information System Name and Title        2

Table 1‑4 Plans Outside of ISCP Scope        3

Table 2‑1 Backup Types        5

Table 2‑2 Backup System Components        5

Table 2‑3 Back-Up Storage Location        6

Table 2‑4 Alternative Site Types        6

Table 2‑5 Primary and Alternative Site Locations        6

Table 3‑1 Personnel Authorized to Activate the ISCP        11

Table 5‑1 Cleanup Roles and Responsibilities        14

Table 5‑2 Event Documentation Responsibility        15

Table B‑1 Key Personnel and Team Member Contact List        18

Table C‑2 Vendor Contact List        19

Table D‑3 Alternate Storage Site Information        20

Table D‑4 Alternate Processing Site Information        20

Table D‑5 Alternate Telecommunications Provisions        21

Table F‑6 System Validation Test Plan        23

Table G‑7 Contingency Plan Test Report        24

Table J‑8 System Interconnections        28

Table L‑9 Associated Plans and Procedures        30
 -->


CONTINGENCY PLAN APPROVALS

| Name | Click here to enter text. | Date | s |
| ---  | ------------------------- | ---- | - |
| Name | Click here to enter text. | Date | |
| Title | Click here to enter text. |
| Cloud Service Provider | Click here to enter text. |

| Name | Click here to enter text. | Date | s |
| ---  | ------------------------- | ---- | - |
| Name | Click here to enter text. | Date | |
| Title | Click here to enter text. |
| Cloud Service Provider | Click here to enter text. |


# 1. Introduction and Purpose

Information systems are vital to CSP Name mission/business functions; therefore, it is critical that services provided by {{project.system_info.system_name}}; are able to operate effectively without excessive interruption.  This Information Technology Contingency Plan (ISCP) establishes comprehensive procedures to recover {{project.system_info.system_name}}; quickly and effectively following a service disruption.

One of the goals of an Information System Contingency Plan is to establish procedures and mechanisms that obviate the need to resort to performing IT functions using manual methods.  If manual methods are the only alternative, however, every effort must be made to continue IT functions and processes manually.

The nature of unprecedented disruptions can create confusion, and often predisposes an otherwise competent IT staff towards less efficient practices.  In order to maintain a normal level of efficiency, it is important to decrease real-time process engineering by documenting notification and activation guidelines and procedures, recovery guidelines and procedures, and reconstitution guidelines and procedures prior to the occurrence of a disruption.  During the notification/activation phase, appropriate personnel are apprised of current conditions and damage assessment begins.  During the recovery phase, appropriate personnel take a course of action to recover the {{project.system_info.system_name}}; components a site other than the one that experienced the disruption.  In the final, reconstitution phase, actions are taken to restore IT system processing capabilities to normal operations.

## 1.1 Applicable Laws and Regulations

The FedRAMP Laws and Regulations may be found on: [www.fedramp.gov](http://www.fedramp.gov) Templates.  A summary of FedRAMP Laws and Regulations is included in the System Security Plan (SSP) ATTACHMENT 12 – FedRAMP Laws and Regulations.

Table 1‑1 {{project.system_info.system_name}}; Laws and Regulations includes additional laws and regulations specific to {{project.system_info.system_name}};.  These will include laws and regulations from the Federal Information Security Management Act (FISMA), Office of Management and Budget (OMB) circulars, Public Law (PL), United States Code (USC), and Homeland Security Presidential Directive (HSPD).

Table 1‑1 {{project.system_info.system_name}}; Laws and Regulations

| Identification Number | Title | Date | Lin --- | --- | --- |
| Click here to enter text. | Click here to enter text. | Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. | Click here to enter text. | Click here to enter text. |

## 1.2 Applicable Standards and Guidance

The FedRAMP Standards and Guidance may be found on: [www.fedramp.gov](http://www.fedramp.gov) Templates. The FedRAMP Standards and Guidance is included in the System Security Plan (SSP) ATTACHMENT 12 – FedRAMP Laws and Regulations.  For more information, see the Program Overview Documents section of the FedRAMP website.

Table 1‑2 {{project.system_info.system_name}}; Standards and Guidance includes any additional standards and guidance specific to {{project.system_info.system_name}};. These will include standards and guidance from Federal Information Processing Standard (FIPS) and National Institute of Standards and Technology (NIST) Special Publications (SP).

Table 1‑2 {{project.system_info.system_name}}; Standards and Guidance

| Identification Number | Title | Date | Lin --- | --- | --- |
| Click here to enter text. | Click here to enter text. | Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. | Click here to enter text. | Click here to enter text. |

## 1.3 FedRAMP Requirements and Guidance

All FedRAMP documents are available at [www.fedramp.gov](../../C:%5CUsers%5CValerieDHatzes%5CDesktop%5CSSP%20Launch%202016%5Cwww.fedramp.gov)

- FedRAMP Incident Communications Procedure
- FedRAMP Continuous Monitoring Strategy and Guide
- Guide to Understanding FedRAMP

## 1.4 Information System Name and Identifier

This ISCP applies to the {{project.system_info.system_name}}; (Information System Abbreviation) which has a unique identifier as noted in Table 1‑3 Information System Name and Title.

Table 1‑3 Information System Name and Title

| Unique Identifier | Information System Name | Information System Abbreviatio --- | --- |
| Enter FedRAMP Application Number. | {{project.system_info.system_name}}; | ISA |

## 1.5 Scope

This ISCP has been developed for ISA which is classified as a impact system, in accordance with Federal Information Processing Standards (FIPS) 199.  FIPS 199 provides guidelines on determining potential impact to organizational operations and assets, and individuals through a formula that examines three security objectives: confidentiality, integrity, and availability.  The procedures in this ISCP have been developed for a impact system and are designed to recover the ISA within Recovery Time Objective (RTO) _Enter Number_ hours.  The replacement or purchase of new equipment, short-term disruptions lasting less than _Enter Number_, or loss of data at the primary facility or at the user-desktop levels is outside the scope of this plan.

Instruction: Edit the below list to name other plans and circumstances that are related but are outside the scope of this ISCP.
Delete this instruction from your final version of this document.

Table 1‑4 Plans Outside of ISCP Scope below identifies other plans and circumstances that are related but are outside the scope of this ISCP.

Table 1‑4 Plans Outside of ISCP Scope

| Plan Name | Mission/Purpos --- |
| Business Continuity Plan (BCP) | Overall recovery and continuity of mission/business operations |
| Continuity of Operations Plan (COOP) | Overall recovery and continuity of mission/business operations |
| The Occupant Emergency Plan (OEP) | Emergency evacuation of personnel |
| Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. |

## 1.6 Assumptions

Instruction: A list of default assumptions are listed in the section that follows.  The assumptions must be edited, revised, and added to so that they accurately characterize the information system described in this plan.
Delete this instruction from your final version of this document.

The following assumptions have been made about the {{project.system_info.system_name}};:

- The Uninterruptable Power Supply (UPS) will keep the system up and running for after _Enter Number_ .
- The generators will kick in after _Enter Number_ from time of a power failure.
- Current backups of the application software and data are intact and available at the offsite storage facility in _Enter City_, _Enter State_.
- The backup storage capability is approved and has been accepted by the Authorizing Official (AO).
- The {{project.system_info.system_name}}; is inoperable if it cannot be recovered within _Enter Number_ RTO hours.
- Key personnel have been identified and are trained annually in their roles.
- Key personnel are available to activate the ISCP.
- CSP Name defines circumstances that can inhibit recovery and reconstitution to a known state.

# 2 Concept of Operations

This section provides details about the {{project.system_info.system_name}};, an overview of the three phases of the ISCP (Activation and Notification, Recovery, and Reconstitution), and a description of the roles and responsibilities of key personnel during contingency operations.

## 2.1 System Description

Instruction: Provide a general description of the system architecture and components.  Include a network diagram that indicates interconnections with other systems.  Ensure that this section is consistent with information found in the **System Security Plan**.  Provide a network diagram and any other diagrams in HAppendix – Diagrams.
Delete this instruction from your final version of this document.

## 2.2 Three Phases

This plan has been developed to recover and reconstitute the {{project.system_info.system_name}}; using a three-phased approach.  The approach ensures that system recovery and reconstitution efforts are performed in a methodical sequence to maximize the effectiveness of the recovery and reconstitution efforts and minimize system outage time due to errors and omissions.  The three system recovery phases consist of activation and notification, recovery, and reconstitution.

1. **Activation and Notification Phase**.  Activation of the ISCP occurs after a disruption, outage, or disaster that may reasonably extend beyond the RTO established for a system.  The outage event may result in severe damage to the facility that houses the system, severe damage or loss of equipment, or other damage that typically results in long-term loss.
Once the ISCP is activated, the information system stakeholders are notified of a possible long-term outage, and a thorough outage assessment is performed for the information system.  Information from the outage assessment is analyzed and may be used to modify recovery procedures specific to the cause of the outage.
2. **Recovery Phase.**  The Recovery phase details the activities and procedures for recovery of the affected system.  Activities and procedures are written at a level such that an appropriately skilled technician can recover the system without intimate system knowledge.  This phase includes notification and awareness escalation procedures for communication of recovery status to system stakeholders.
3. **Reconstitution.**  The Reconstitution phase defines the actions taken to test and validate system capability and functionality at the original or new permanent location.  This phase consists of two major activities: validating data and operational functionality followed by deactivation of the plan.

During validation, the system is tested and validated as operational prior to returning operation to its normal state.  Validation procedures include functionality or regression testing, concurrent processing, and/or data validation.  The system is declared recovered and operational by upon successful completion of validation testing.

Deactivation includes activities to notify users of system operational status.  This phase also addresses recovery effort documentation, activity log finalization, incorporation of lessons learned into plan updates, and readying resources for any future events.

## 2.3 Data Backup Readiness Information

A common understanding of data backup definitions is necessary in order to ensure that data restoration is successful.  CSP Name recognizes different types of backups, which have different purposes, and those definitions are found in Table 2‑1 Backup Types.

Table 2‑1 Backup Types

| Backup Type | Descriptio --- |
| Full Backup | A full backup is the starting point for all other types of backup and contains all the data in the folders and files that are selected to be backed up.  Because full backup stores all files and folders, frequent full backups result in faster and simpler restore operations. |
| Differential Backup | Differential backup contains all files that have changed since the last FULL backup.  The advantage of a differential backup is that it shortens restore time compared to a full back up or an incremental backup.  However, if the differential backup is performed too many times, the size of the differential backup might grow to be larger than the baseline full backup. |
| Incremental Backup | Incremental backup stores all files that have changed since the last FULL, DIFFERENTIAL OR INCREMENTAL backup.  The advantage of an incremental backup is that it takes the least time to complete.  However, during a restore operation, each incremental backup must be processed, which may result in a lengthy restore job. |
| Mirror Backup | Mirror backup is identical to a full backup, with the exception that the files are not compressed in zip files and they cannot be protected with a password.  A mirror backup is most frequently used to create an exact copy of the source data. |

The hardware and software components used to create the {{project.system_info.system_name}}; backups are noted in Table 2‑2 Backup System Components.

Table 2‑2 Backup System Components

| System/Component | Descriptio --- |
| Software Used | Click here to enter text. |
| Hardware Used | Click here to enter text. |
| Frequency | Click here to enter text. |
| Backup Type | Click here to enter text. |
| Retention Period | Click here to enter text. |

Table 2‑3 Back-Up Storage Location shows the offsite storage facility location of current backups of the {{project.system_info.system_name}}; system software and data.

Table 2‑3 Back-Up Storage Location

| Back Up Storag
| Site Name | Click here to enter text. |
| Street Address | Click here to enter text. |
| City, State, Zip Code | Click here to enter text. |

Personnel who are authorized to retrieve backups from the offsite storage location, and may authorize the delivery of backups, are noted in D.1Appendix – Alternate Storage Site Information.

CSP Name maintains both an online and offline (portable) set of backup copies of the following types of data on site at their primary location:

- User-level information
- System-level information
- Information system documentation including security information.

## 2.4 Site Readiness Information

CSP Name recognizes different types of alternate sites, which are defined in Table 2‑4 Alternative Site Types.

Table 2‑4 Alternative Site Types

| Type of Site | Descriptio --- |
| Cold Sites | Cold Sites are typically facilities with adequate space and infrastructure (electric power, telecommunications connections, and environmental controls) to support information system recovery activities. |
| Warm Sites | Warm Sites are partially equipped office spaces that contain some or all of the system hardware, software, telecommunications, and power sources. |
| Hot Sites | Hot Sites are facilities appropriately sized to support system requirements and configured with the necessary system hardware, supporting infrastructure, and support personnel. |
| Mirrored Sites | Mirrored Sites are fully redundant facilities with automated real-time information mirroring.  Mirrored sites are identical to the primary site in all technical respects. |

Alternate facilities have been established for the {{project.system_info.system_name}}; as noted in Table 2‑4 Alternative Site Types.

Table 2‑5 Primary and Alternative Site Locations

| Designation | Site Name | Site Type | Addres --- | --- | --- |
| Primary Site |   |   |   |
| Alternate Site |   |   |   |
| Alternate Site |   |   |   |

## 2.5 Roles and Responsibilities

CSP Name establishes multiple roles and responsibilities for responding to outages, disruptions, and disasters for the {{project.system_info.system_name}};.  Individuals who are assigned roles for recovery operations collectively make up the Contingency Plan Team and are trained annually in their duties.  Contingency Plan Team members are chosen based on their skills and knowledge.

Instruction: Describe each team and role responsible for executing or supporting system recovery and reconstitution.  Include responsibilities for each team/role including leadership roles.  FedRAMP has established default roles and a small set of default responsibilities which must be edited and modified to match the actual organizational role names, responsibilities, and associated duties for the organization.
Delete this instruction from your final version of this document.

The Contingency Plan Team consists of personnel who have been selected to perform the roles and responsibilities described in the sections that follow.  All team leads are considered key personnel.

### 2.5.1 Contingency Planning Director (CPD)

The Contingency Planning Director (CPD) is a member of senior management and owns the responsibility for all facets of contingency and disaster recovery planning and execution.

The CPD performs the following duties:

- Makes the decision on whether or not to activate the ISCP
- Provides the initial notification to activate the ISCP
- Reviews and approves the ISCP
- Reviews and approves the Business Impact Analysis (BIA)
- Notifies the Contingency Plan Team leads and members as necessary
- Advises other Contingency Plan Team leads and members as appropriate
- Issues a recovery declaration statement after the system has returned to normal operations
- Designates key personnel

### 2.5.2 Contingency Planning Coordinator (CPC)

The CPC performs the following duties:

- Develops and documents the ISCP under direction of the CPD
- Uses the BIA to prioritize recovery of components
- Updates the ISCP annually
- Ensures that annual ISCP training is conducted
- Facilitates periodic ISCP testing exercises
- Distributes copies of the plan to team members
- Authorizes travel and housing arrangements for team members
- Manages and monitors the overall recovery process
- Leads the contingency response effort once the plan has been activated
- Advises the Procurement and Logistics Coordinator on whether to order new equipment
- Receives updates and status reports from team members
- Sends out communications about the recovery
- Advises the CPD on status as necessary
- Designates key personnel

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

### 2.5.8 Security Coordinator (SC)

The Security Coordinator performs the following duties:

- Provides training for employees in facility emergency procedures and measures
- Provides physical security, access control, and safety measures to support recovery effort
- Cordons off the facility including offices to restrict unauthorized access
- Coordinates with the building management and the CPC for authorized personnel access
- Coordinates and manages additional physical security/guards as needed
- Acts as a liaison with emergency personnel, such as fire and police departments
- Provides assistance to officials in investigating the damaged facility/site
- Ensures that data room/center at alternate site has locks (access controls) on the doors
- Coordinates and secures the transportation of files, reports, and equipment in coordination with the CPC

### 2.5.9 Plan Distribution and Availability

During a disaster situation, the availability of the contingency plan is essential to the success of the restoration efforts.  The Contingency Plan Team has immediate access to the plan upon notification of an emergency.  The Contingency Plan Coordinator ensures that a copy of the most current version of the Contingency Plan is maintained at CSP Name&#39;s facility.  This plan has been distributed to all personnel listed in BAppendix – Key Personnel and Team Member Contact List.

Contingency Plan Team members are obligated to inform the Contingency Planning Coordinator, if and when, they no longer require a copy of the plan.  In addition, each recipient of the plan is obligated to return or destroy any portion of the plan that is no longer needed and upon termination from CSP Name.

### 2.5.10 Line of Succession/Alternates Roles

The CSP Name sets forth an order of succession, in coordination with the order set forth by the organization to ensure that decision-making authority for the {{project.system_info.system_name}}; ISCP is uninterrupted.

In order to preserve the continuity of operations, individuals designated as key personnel have been assigned an individual who can assume the key personnel&#39;s position if the key personnel is not able to perform their duties.  Alternate key personnel are named in a line of succession and are notified and trained to assume their alternate role, should the need arise.  The line of succession for key personnel can be found in BAppendix – Key Personnel and Team Member Contact List.

1. 3Activation and Notification

The activation and notification phase defines initial actions taken once the {{project.system_info.system_name}}; disruption has been detected or appears to be imminent.  This phase includes activities to notify recovery personnel, conduct an outage assessment, and activate the ISCP.

At the completion of the Activation and Notification Phase, key {{project.system_info.system_name}}; ISCP staff will be prepared to perform recovery measures to restore system functions.

## 3.1 Activation Criteria and Procedure

The {{project.system_info.system_name}}; ISCP may be activated if one or more of the following criteria are met:

1. The type of outage indicates {{project.system_info.system_name}}; will be down for more than _Enter Number_ RTO hours.
2. The facility housing {{project.system_info.system_name}}; is damaged and may not be available within _Enter Number_ RTO hours
3. Other criteria, as appropriate.

Personnel/roles listed in Table 3‑1 Personnel Authorized to Activate the ISCP are authorized to activate the ISCP.

Table 3‑1 Personnel Authorized to Activate the ISCP

| Name | Title and ISCP Role | Contact Informatio --- | --- |
| Click here to enter text. | Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. | Click here to enter text. |
| Click here to enter text. | Click here to enter text. | Click here to enter text. |

## 3.2 Notification Instructions

Instruction: Describe established notifications procedures.  Notification procedures must include who makes the initial notifications, the sequence in which personnel are notified and the method of notification (e.g., email blast, call tree, text messaging, automated notification system, etc.). Delete this instruction from your final version of this document.

Contact information for key personnel is located in BAppendix – Key Personnel and Team Member Contact List.

## 3.3 Outage Assessment

Following notification, a thorough outage assessment is necessary to determine the extent of the disruption, any damage, and expected recovery time.  This outage assessment is conducted by _Insert role name_.  Assessment results are provided to the Contingency Planning Coordinator to assist in the coordination of the recovery effort.

Instruction: Outline detailed procedures to include how to determine the cause of the outage; identification of potential for additional disruption or damage; assessment of affected physical area(s); and determination of the physical infrastructure status, IS equipment functionality, and inventory.  Procedures must include notation of items that will be needed to be replaced and estimated time to restore service to normal operations.
Delete this instruction from your final version of this document.

## 4 Recovery

The recovery phase provides formal recovery operations that begin after the ISCP has been activated, outage assessments have been completed (if possible), personnel have been notified, and appropriate teams have been mobilized.  Recovery phase activities focus on implementing recovery strategies to restore system capabilities, repair damage, and resume operational capabilities at the original or an alternate location.  At the completion of the recovery phase, {{project.system_info.system_name}}; will be functional and capable of performing the functions identified in Section 4.1Sequence of Recovery Operations of the plan.

## 4.1 Sequence of Recovery Operations

The following activities occur during recovery of {{project.system_info.system_name}};:

Instruction: Modify the following list as appropriate for the system recovery strategy.
Delete this instruction from your final version of this document.

1. Identification of recovery location (if not at original location)
2. Identification of required resources to perform recovery procedures
3. Retrieval of backup and system installation media
4. Recovery of hardware and operating system (if required)
5. Recovery of system from backup and system installation media
6. Implementation of transaction recovery for systems that are transaction-based

## 4.2 Recovery Procedures

The following procedures are provided for recovery of {{project.system_info.system_name}}; at the original or established alternate location.  Recovery procedures are outlined per team and must be executed in the sequence presented to maintain an efficient recovery effort.

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

Upon successfully completing testing and validation, the _Insert role name_ will formally declare recovery efforts complete, and that {{project.system_info.system_name}}; is in normal operations.  {{project.system_info.system_name}}; business and technical POCs will be notified of the declaration by the Contingency Plan Coordinator.  The recovery declaration statement notifies the Contingency Plan Team and executive management that the {{project.system_info.system_name}}; has returned to normal operations.

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

1. 6Contingency Plan Testing

Contingency Plan operational tests of the {{project.system_info.system_name}}; are performed annually.  A Contingency Plan Test Report is documented after each annual test.  A template for the Contingency Plan Test Report is found in GAppendix – Contingency Plan Test Report.

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

The Integrated Inventory Workbook, also provided as Attachment 13 of the [[_System Name_]]; System Security Plan, provides the complete listing of system components addressed by this Information System Contingency Plan.

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