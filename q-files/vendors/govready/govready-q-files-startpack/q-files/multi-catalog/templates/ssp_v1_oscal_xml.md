id: ssp_v1_oscal_xml
format: xml
title: SSP v1 (OSCAL/XML)
...
  <?xml version="1.0" encoding="UTF-8"?>
  <system-security-plan xmlns="http://csrc.nist.gov/ns/oscal/1.0"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="https://raw.githubusercontent.com/usnistgov/OSCAL/master/xml/schema/oscal_ssp_schema.xsd"
     uuid="2fa78e07-74ef-4cd6-8124-bc0050c0c4df">
     <metadata>
        <title>FedRAMP System Security Plan (SSP)</title>
        <published>2020-07-01T00:00:00.00-04:00</published>
        <last-modified>2020-07-01T00:00:00.00-04:00</last-modified>
        <version>0.0</version>
        <oscal-version>1.0-Milestone3</oscal-version>
        <revision-history>
           <revision>
              <published>2019-06-01T00:00:00.00-04:00</published>
              <version>1.0</version>
              <oscal-version>1.0-Milestone3</oscal-version>
              <prop name="party-uuid" ns="https://fedramp.gov/ns/oscal">6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</prop>
              <remarks>
                 <p>Initial publication.</p>
              </remarks>
           </revision>
           <revision>
              <published>2020-06-01T00:00:00.00-04:00</published>
              <version>2.0</version>
              <oscal-version>1.0-Milestone3</oscal-version>
              <prop name="party-id" ns="https://fedramp.gov/ns/oscal">csp</prop>
              <remarks>
                 <p>Updated for annual assessment.</p>
              </remarks>
           </revision>
           <!-- Additional revision assemblies as needed. -->
        </revision-history>
        <prop name="marking">Controlled Unclassified Information</prop>
        <!-- The following role definitions are required by FedRAMP -->
        <!-- Do not change the ID's or titles. -->
        <role id="prepared-by">
           <title>Prepared By</title>
           <desc>The organization that prepared this SSP. If developed in-house, this is the CSP itself.</desc>
        </role>
        <role id="prepared-for">
           <title>Prepared For</title>
           <desc>The organization for which this SSP was prepared. Typically the CSP.</desc>
        </role>
        <role id="content-approver">
           <title>System Security Plan Approval</title>
           <desc>The individual or individuals accountable for the accuracy of this SSP.</desc>
        </role>
        <role id="cloud-service-provider">
           <title>Cloud Service Provider</title>
           <short-name>CSP</short-name>
        </role>
        <role id="system-owner">
           <title>Information System Owner</title>
           <desc>The individual within the CSP who is ultimately accountable for everything related to this system.</desc>
        </role>
        <role id="authorizing-official">
           <title>Authorizing Official</title>
           <desc>The individual or individuals who must grant this system an authorization to operate.</desc>
        </role>
        <role id="authorizing-official-poc">
           <title>Authorizing Official's Point of Contact</title>
           <desc>The individual representing the authorizing official.</desc>
        </role>
        <role id="system-poc-management">
           <title>Information System Management Point of Contact (POC)</title>
           <desc>The highest level manager who responsible for system operation on behalf of the System Owner.</desc>
        </role>
        <role id="system-poc-technical">
           <title>Information System Technical Point of Contact</title>
           <desc>The individual or individuals leading the technical operation of the system.</desc>
        </role>
        <role id="system-poc-other">
           <title>General Point of Contact (POC)</title>
           <desc>A general point of contact for the system, designated by the system owner.</desc>
        </role>
        <role id="information-system-security-officer">
           <title>System Information System Security Officer (or Equivalent)</title>
           <desc>The individual accountable for the security posture of the system on behalf of the system owner.</desc>
        </role>
        <role id="privacy-poc">
           <title>Privacy Official's Point of Contact</title>
           <desc>The individual responsible for the privacy threshold analysis and if necessary the privacy impact assessment.</desc>
        </role>
        <role id="asset-owner">
           <title>Owner of an inventory item within the system.</title>
        </role>
        <role id="asset-administrator">
           <title>Administrative responsibility an inventory item within the system.</title>
        </role>
        <role id="isa-poc-local">
           <title>ICA POC (Local)</title>
           <desc>The point of contact for an interconnection on behalf of this system.</desc>
           <remarks>
              <p>Remove this role if there are no ICAs.</p>
           </remarks>
        </role>
        <role id="isa-poc-remote">
           <title>ICA POC (Remote)</title>
           <desc>The point of contact for an interconnection on behalf of this external system to which this system connects.</desc>
           <remarks>
              <p>Remove this role if there are no ICAs.</p>
           </remarks>
        </role>
        <role id="isa-authorizing-official-local">
           <title>ICA Signatory (Local)</title>
           <desc>Responsible for signing an interconnection security agreement on behalf of this system.</desc>
           <remarks>
              <p>Remove this role if there are no ICAs.</p>
           </remarks>
        </role>
        <role id="isa-authorizing-official-remote">
           <title>ICA Signatory (Remote)</title>
           <desc>Responsible for signing an interconnection security agreement on behalf of the external system to which this system connects.</desc>
           <remarks>
              <p>Remove this role if there are no ICAs.</p>
           </remarks>
        </role>
        <role id="consultant">
           <title>Consultant</title>
           <desc>Any consultants involved with developing or maintaining this content.</desc>
        </role>
        <!-- The following role definitions are samples and may be modified or deleted -->
        <role id="admin-unix">
           <title>[SAMPLE]Unix Administrator</title>
           <desc>This is a sample role.</desc>
        </role>
        <role id="admin-client">
           <title>[SAMPLE]Client Administrator</title>
           <desc>This is a sample role.</desc>
        </role>
        <role id="program-director">
           <title>[SAMPLE]Program Director</title>
           <desc>This is a sample role.</desc>
        </role>
        <role id="fedramp-pmo">
           <title>Federal Risk and Authorization Management Program (FedRAMP) Program Management Office (PMO)</title>
           <short-name>FedRAMP PMO</short-name>
        </role>
        <role id="fedramp-jab">
           <title>Federal Risk and Authorization Management Program (FedRAMP) Joint Authorization Board (JAB)</title>
           <short-name>FedRAMP JAB</short-name>
        </role>
        <location uuid="27b78960-59ef-4619-82b0-ae20b9c709ac">
           <title>CSP HQ</title>
           <address type="work">
              <addr-line>Suite 0000</addr-line>
              <addr-line>1234 Some Street</addr-line>
              <city>Haven</city>
              <state>ME</state>
              <postal-code>00000</postal-code>
           </address>
           <remarks>
              <p>There must be one location identifying the CSP's primary business address, such as the CSP's HQ, or the address of the system owner's primary business location.</p>
           </remarks>
        </location>
        <location uuid="16adcc8d-65d8-4583-80d3-9cf007744fec">
           <title>Primary Data Center</title>
           <address>
              <addr-line>2222 Main Street</addr-line>
              <city>Anywhere</city>
              <state>--</state>
              <postal-code>00000-0000</postal-code>
           </address>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">data-center</prop>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">primary-data-center</prop>
           <remarks>
              <p>There must be one location for each data center.</p>
              <p>There must be at least two data centers.</p>
              <p>For a data center, briefly summarize the components at this location.</p>
              <p>All data centers must have a conformity tag of "data-center".</p>
              <p>A primary data center must also have a conformity tag of "primary-data-center".</p>
           </remarks>
        </location>
        <location uuid="ad321514-7b9f-4374-8409-efb18eea6e5d">
           <title>Secondary Data Center</title>
           <address>
              <addr-line>3333 Small Road</addr-line>
              <city>Anywhere</city>
              <state>--</state>
              <postal-code>00000-0000</postal-code>
           </address>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">data-center</prop>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">alternate-data-center</prop>
           <remarks>
              <p>There must be one location for each data center.</p>
              <p>There must be at least two data centers.</p>
              <p>For a data center, briefly summarize the components at this location.</p>
              <p>All data centers must have a conformity tag of "data-center"</p>
              <p>An alternate or backup data center must also have a conformity tag of "alternate-data-center".</p>
           </remarks>
        </location>
        <!-- The following parties must be present. Preserving the ID is no longer required. -->
        <!-- Change the content as needed. -->
        <party uuid="6b286b5d-8f07-4fa7-8847-1dd0d88f73fb" type="organization">
           <party-name>Cloud Service Provider (CSP) Name</party-name>
           <short-name>CSP Acronym/Short Name</short-name>
           <location-uuid>27b78960-59ef-4619-82b0-ae20b9c709ac</location-uuid>
           <remarks>
              <p>Replace sample CSP information.</p>
           </remarks>
        </party>
        <!-- The following parties must be present. Preserving the ID is no longer required. -->
        <!-- Do not change the FedRAMP PMO and JAB information unless instructed to do so by the FedRAMP PMO. -->
        <party uuid="77e0e2c8-2560-4fe9-ac78-c3ff4ffc9f6d" type="organization">
           <party-name>Federal Risk and Authorization Management Program: Program Management Office</party-name>
           <short-name>FedRAMP PMO</short-name>
           <link href="https://fedramp.gov" />
           <address type="work">
              <addr-line>1800 F St. NW</addr-line>
              <addr-line/>
              <city>Washington</city>
              <state>DC</state>
              <postal-code/>
              <country>US</country>
           </address>
           <email>info@fedramp.gov</email>
           <remarks>
              <p>This party entry must be present in a FedRAMP SSP.</p>
              <p>The uuid may be different; however, the uuid must be associated with the "fedramp-pmo" role in the responsible-party assemblies.</p>
           </remarks>
        </party>
        <party uuid="49017ec3-9f51-4dbd-9253-858c2b1295fd" type="organization">
           <party-name>Federal Risk and Authorization Management Program: Joint Authorization Board</party-name>
           <short-name>FedRAMP JAB</short-name>
           <remarks>
              <p>This party entry must be present in a FedRAMP SSP.</p>
              <p>The uuid may be different; however, the uuid must be associated with the "fedramp-jab" role in the responsible-party assemblies.</p>
           </remarks>
        </party>
        <!-- The following parties are samples, and may be modified or removed -->
        <party uuid="78992555-4a99-4eaa-868c-f2c249679dd3" type="organization">
           <party-name>External Organization</party-name>
           <short-name>External</short-name>
           <remarks>
              <p>Generic placeholder for any external organization.</p>
           </remarks>
        </party>
        <party uuid="f595397b-cbe4-4a87-8c86-9bff91c4e7fd" type="organization">
           <party-name>Agency Name</party-name>
           <short-name>A.N.</short-name>
           <remarks>
              <p>Generic placeholder for an authorizing agency.</p>
           </remarks>
        </party>
        <party uuid="8e3d39da-4851-4d2a-adb5-4b5585ded952" type="organization">
           <party-name>Name of Consulting Org</party-name>
           <short-name>NOCO</short-name>
           <link href="https://consulting.sample" />
           <address type="work">
              <addr-line>3333 Corporate Way</addr-line>
              <city>Washington</city>
              <state>DC</state>
              <postal-code/>
              <country>US</country>
           </address>
           <email>poc@consulting.sample</email>
        </party>
        <party uuid="80361ec4-bfce-4b5c-85c8-313d6ebd220b" type="organization">
           <party-name>[SAMPLE]Remote System Org Name</party-name>
        </party>
        <party uuid="09ad840f-aa79-43aa-9f22-25182c2ab11b" type="person">
           <party-name>[SAMPLE]ICA POC's Name</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <email>person@ica.org.example</email>
           <phone>202-555-1212</phone>
           <member-of-organization>80361ec4-bfce-4b5c-85c8-313d6ebd220b</member-of-organization>
        </party>
        <party uuid="f0bc13a4-3303-47dd-80d3-380e159c8362" type="organization">
           <party-name>[SAMPLE]Example IaaS Provider</party-name>
           <short-name>E.I.P.</short-name>
           <remarks>
              <p>Underlying service provider. Leveraged Authorization.</p>
           </remarks>
        </party>
        <party uuid="3360e343-9860-4bda-9dfc-ff427c3dfab6" type="person">
           <party-name>[SAMPLE]Person Name 1</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address>
              <addr-line>Mailstop A-1</addr-line>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0001</phone>
           <member-of-organization>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</member-of-organization>         
           <location-uuid>27b78960-59ef-4619-82b0-ae20b9c709ac</location-uuid>
        </party>
        <party uuid="36b8d6c0-3b25-42cc-b529-cf4066145cdd" type="person">
           <party-name>[SAMPLE]Person Name 2</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address type="work">
              <addr-line>Address Line</addr-line>
              <city>City</city>
              <state>ST</state>
              <postal-code>00000</postal-code>
              <country>US</country>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0002</phone>
           <member-of-organization>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</member-of-organization>         
        </party>
        <party uuid="0cec09d9-20c6-470b-9ffc-85763375880b" type="person">
           <party-name>[SAMPLE]Person Name 3</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address type="work">
              <addr-line>Address Line</addr-line>
              <city>City</city>
              <state>ST</state>
              <postal-code>00000</postal-code>
              <country>US</country>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0003</phone>
           <member-of-organization>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</member-of-organization>         
        </party>
        <party uuid="f75e21f6-43d8-46ab-890d-7f2eebc5a830" type="person">
           <party-name>[SAMPLE]Person Name 4</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address type="work">
              <addr-line>Address Line</addr-line>
              <city>City</city>
              <state>ST</state>
              <postal-code>00000</postal-code>
              <country>US</country>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0004</phone>
           <member-of-organization>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</member-of-organization>         
        </party>
        <party uuid="132953a9-640c-46f7-9de9-3fa15ec99361" type="person">
           <party-name>[SAMPLE]Person Name 5</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address type="work">
              <addr-line>Address Line</addr-line>
              <city>City</city>
              <state>ST</state>
              <postal-code>00000</postal-code>
              <country>US</country>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0005</phone>
           <member-of-organization>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</member-of-organization>         
        </party>
        <party uuid="4fded5fd-7a65-47ea-bd76-df57c46e27d1" type="person">
           <party-name>[SAMPLE]Person Name 6</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address type="work">
              <addr-line>Address Line</addr-line>
              <city>City</city>
              <state>ST</state>
              <postal-code>00000</postal-code>
              <country>US</country>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0006</phone>
           <member-of-organization>78992555-4a99-4eaa-868c-f2c249679dd3</member-of-organization>         
        </party>
        <party uuid="db234cb7-1776-425c-9ac4-b067c1723011" type="person">
           <party-name>[SAMPLE]Person Name 7</party-name>
           <prop name="title" ns="https://fedramp.gov/ns/oscal">Individual's Title</prop>
           <address type="work">
              <addr-line>Address Line</addr-line>
              <city>City</city>
              <state>ST</state>
              <postal-code>00000</postal-code>
              <country>US</country>
           </address>
           <email>name@org.domain</email>
           <phone>202-000-0007</phone>
           <member-of-organization>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</member-of-organization>         
        </party>
        <party uuid="b306f5af-b93a-4a7f-a2b2-37a44fc92a79" type="organization">
           <party-name>[SAMPLE] IT Department</party-name>
        </party>
        <party uuid="59cdc953-5902-4fa4-a878-f3163854624c" type="organization">
           <party-name>[SAMPLE]Security Team</party-name>
        </party>
        <responsible-party role-id="cloud-service-provider">
           <party-uuid>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <!-- Page ii -->
        <responsible-party role-id="prepared-by">
           <party-uuid>3360e343-9860-4bda-9dfc-ff427c3dfab6</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="prepared-for">
           <!-- Exacty one -->
           <party-uuid>6b286b5d-8f07-4fa7-8847-1dd0d88f73fb</party-uuid>
        </responsible-party>
        <!-- Page vi -->
        <responsible-party role-id="content-approver">
           <party-uuid>3360e343-9860-4bda-9dfc-ff427c3dfab6</party-uuid>
           <party-uuid>36b8d6c0-3b25-42cc-b529-cf4066145cdd</party-uuid>
           <remarks>
              <p>One or more</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="system-owner">
           <party-uuid>3360e343-9860-4bda-9dfc-ff427c3dfab6</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="authorizing-official">
           <party-uuid>49017ec3-9f51-4dbd-9253-858c2b1295fd</party-uuid>
           <party-uuid>4fded5fd-7a65-47ea-bd76-df57c46e27d1</party-uuid>
           <remarks>
              <p>One or more</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="system-poc-management">
           <party-uuid>0cec09d9-20c6-470b-9ffc-85763375880b</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="system-poc-technical">
           <party-uuid>f75e21f6-43d8-46ab-890d-7f2eebc5a830</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="information-system-security-officer">
           <party-uuid>132953a9-640c-46f7-9de9-3fa15ec99361</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="authorizing-official-poc">
           <party-uuid>4fded5fd-7a65-47ea-bd76-df57c46e27d1</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="privacy-poc">
           <party-uuid>db234cb7-1776-425c-9ac4-b067c1723011</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="fedramp-pmo">
           <party-uuid>77e0e2c8-2560-4fe9-ac78-c3ff4ffc9f6d</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <responsible-party role-id="fedramp-jab">
           <party-uuid>49017ec3-9f51-4dbd-9253-858c2b1295fd</party-uuid>
           <remarks>
              <p>Exactly one</p>
           </remarks>
        </responsible-party>
        <remarks>
           <p>This OSCAL-based FedRAMP SSP Template can be used for the FedRAMP Low, Moderate, and
              High baselines.</p>
           <p>Guidance for OSCAL-based FedRAMP Tailored content has not yet been developed.</p>
        </remarks>
     </metadata>
     <!-- ====================================================
        Link this SSP to the appropriate FedRAMP baseline using ONE of the import statements below.
        NOTE: This points to a resource at the end of this file with links to both the XML and JSON
              versions of the baseline. Tools must select the appropriate link 
        FedRAMP HIGH Baseline: 
        <import-profile href="#9f1aae37-7359-411f-86c1-768aaab85e63"/>
        FedRAMP MODERATE Baseline:
        <import-profile href="#890170c3-d4fa-4d25-ab96-8e4bf7cc237c"/>
        FedRAMP LOW Baseline: 
        <import-profile href="#2acaf846-5496-4d36-8565-9a15b48aef2c"/>
     ==================================================== -->
     <import-profile href="#890170c3-d4fa-4d25-ab96-8e4bf7cc237c"/>
     <system-characteristics>
        <!-- Table 1-1 Information System Name and Title -->
        <system-id identifier-type="https://fedramp.gov">F00000000</system-id>
        <system-name>{{project.system_info.system_name}}</system-name>
        <system-name-short>{{project.system_info.system_short_name}}</system-name-short>
        <!-- Section 9.1 (Old SSP Format Section 8.1) -->
        <description>
           <p>{{project.system_info.system_description}}</p>
        </description>
        <!-- FedRAMP Authorizatoin Type: fedramp-jab, fedramp-agency, or fedramp-li-saas -->
        <prop name="authorization-type" ns="https://fedramp.gov/ns/oscal">fedramp-agency</prop>
        <!-- Section 2.3 Digital Identity Determination and Attachment 3, Digital Identity Worksheet -->
        <!-- 1 = low, 2= moderate, 3 = high  -->
        <prop name="security-eauth-level" class="security-eauth" ns="https://fedramp.gov/ns/oscal">2</prop>
        <!-- Attachment 3, Digital Identity Worksheet: Additional Detail - Not Required -->
        <prop name="identity-assurance-level">2</prop>
        <prop name="authenticator-assurance-level">2</prop>
        <prop name="federation-assurance-level">2</prop>
        <!-- Table 8-1 Service Layers Represented in this SSP -->
        <annotation name="cloud-service-model" value="saas">
           <remarks>
              <p>Remarks are required if service model is "other". Optional otherwise.</p>
           </remarks>
        </annotation>
        <!-- Table 8-2 Cloud Deployment Model Represented in this SSP -->
        <annotation name="cloud-deployment-model" value="government-only-cloud">
           <remarks>
              <p>Remarks are required if deployment model is "hybrid-cloud" or "other". Optional
                 otherwise.</p>
           </remarks>
        </annotation>
        <!-- Table 2-1 Security Categorization and 2-4 Baseline Security Configuration -->
        <security-sensitivity-level>low</security-sensitivity-level>
        <!-- Table 2-2, Table 15-9, and Attachment 4 -->
        <system-information>
           <!-- Attachment 4, PTA/PIA Designation -->
           <prop name="privacy-sensitive">yes</prop>
           <!-- Attachment 4, PTA Qualifying Questions -->
           <!--Does the ISA collect, maintain, or share PII in any identifiable form? -->
           <prop name="pta-1" class="pta" ns="https://fedramp.gov/ns/oscal">yes</prop>
           <!--Does the ISA collect, maintain, or share PII information from or about the public? -->
           <prop name="pta-2" class="pta" ns="https://fedramp.gov/ns/oscal">yes</prop>
           <!--Has a Privacy Impact Assessment ever been performed for the ISA? -->
           <prop name="pta-3" class="pta" ns="https://fedramp.gov/ns/oscal">yes</prop>
           <!--Is there a Privacy Act System of Records Notice (SORN) for this ISA system? (If so, please specify the SORN ID.) -->
           <prop name="pta-4" class="pta" ns="https://fedramp.gov/ns/oscal">no</prop>
           <prop name="sorn-id" class="pta" ns="https://fedramp.gov/ns/oscal">[No SORN ID]</prop>
           <information-type id="info-01">
              <title>Information Type Name</title>
              <description>
                 <p>A description of the information.</p>
              </description>
              <information-type-id system="https://doi.org/10.6028/NIST.SP.800-60v2r1">C.2.4.1</information-type-id>
              <confidentiality-impact>
                 <base>fips-199-moderate</base>
                 <selected>fips-199-moderate</selected>
                 <adjustment-justification>
                    <p>Required if the base and selected values do not match.</p>
                 </adjustment-justification>
              </confidentiality-impact>
              <integrity-impact>
                 <base>fips-199-moderate</base>
                 <selected>fips-199-moderate</selected>
                 <adjustment-justification>
                    <p>Required if the base and selected values do not match.</p>
                 </adjustment-justification>
              </integrity-impact>
              <availability-impact>
                 <base>fips-199-moderate</base>
                 <selected>fips-199-moderate</selected>
                 <adjustment-justification>
                    <p>Required if the base and selected values do not match.</p>
                 </adjustment-justification>
              </availability-impact>
           </information-type>
        </system-information>
        <!-- Table 2-3 Security Impact Level -->
        <security-impact-level>
           <security-objective-confidentiality>fips-199-moderate</security-objective-confidentiality>
           <security-objective-integrity>fips-199-moderate</security-objective-integrity>
           <security-objective-availability>fips-199-moderate</security-objective-availability>
        </security-impact-level>
        <!-- Section 2.3 Digital Identity Determination & Table 7-1 System Status -->
        <status state="operational">
           <remarks>
              <p>{{project.system_info_technical.system_status.text}}</p>
           </remarks>
        </status>
        <!-- Table 8-3 Leveraged Authorizations (Typically 0 or 1) -->
        <!-- ***** REWORKING LEVERAGED AUTHORIZATIONS MODEL WITH NIST ****** -->
        <!-- Section 9.2, Figure 9-1. Authorization Boundary Diagram -->
        <authorization-boundary>
           <description>
              <p>A holistic, top-level explanation of the FedRAMP authorization boundary.</p>
           </description>
           <diagram uuid="dbf46c27-52a9-49c4-beb6-b6399cd75497">
              <description>
                 <p>A diagram-specific explanation.</p>
              </description>
              <link href="#d2eb3c18-6754-4e3a-a933-03d289e3fad5" rel="diagram"/>
              <caption>Authorization Boundary Diagram</caption>
           </diagram>
        </authorization-boundary>
        <!-- Section 9.4, Figure 9-2. Network Diagram -->
        <network-architecture>
           <description>
              <p>A holistic, top-level explanation of the network architecture.</p>
           </description>
           <diagram uuid="e97c3395-433a-48c1-8cc7-dd1e1555941c">
              <description>
                 <p>A diagram-specific explanation.</p>
              </description>
              <link href="#61081e81-850b-43c1-bf43-1ecbddcb9e7f" rel="diagram"/>
              <caption>Network Diagram</caption>
           </diagram>
        </network-architecture>
        <!-- Section 10, Figure 10-1. Data Flow Diagram -->
        <data-flow>
           <description>
              <p>A holistic, top-level explanation of the system's data flows.</p>
           </description>
           <diagram uuid="e3b98448-4219-46a5-b229-412423c566f3">
              <description>
                 <p>A diagram-specific explanation.</p>
              </description>
              <link href="#ac5d7535-f3b8-45d3-bf3b-735c82c64547" rel="diagram"/>
              <caption>Data Flow Diagram</caption>
           </diagram>
        </data-flow>
     </system-characteristics>
     <system-implementation>
        <!-- Section 9.3 Types of Users - Internal and External Personnel Counts -->
        <prop name="users-internal" ns="https://fedramp.gov/ns/oscal">0</prop>
        <prop name="users-external" ns="https://fedramp.gov/ns/oscal">0</prop>
        <prop name="users-internal-future" ns="https://fedramp.gov/ns/oscal">0</prop>
        <prop name="users-external-future" ns="https://fedramp.gov/ns/oscal">0</prop>
        <!-- Section 9.3, Table 9-1. Personnel Roles and Privileges -->
        <user uuid="9cb0fab0-78bd-44ba-bcb8-3e9801cc952f">
           <title>[SAMPLE]Unix System Administrator</title>
           <prop name="sensitivity" ns="https://fedramp.gov/ns/oscal">high</prop>
           <annotation name="privilege-level" value="privileged"/>
           <annotation name="type" value="internal"/>
           <role-id>admin-unix</role-id>
           <authorized-privilege>
              <title>Full administrative access (root)</title>
              <function-performed>Add/remove users and hardware</function-performed>
              <function-performed>install and configure software</function-performed>
              <function-performed>OS updates, patches and hotfixes</function-performed>
              <function-performed>perform backups</function-performed>
           </authorized-privilege>
        </user>
        <user uuid="16ec71e7-025c-43e4-9d3f-3acb485fac2e">
           <title>[SAMPLE]Client Administrator</title>
           <prop name="sensitivity" ns="https://fedramp.gov/ns/oscal">moderate</prop>
           <annotation name="privilege-level" value="non-privileged"/>
           <annotation name="type" value="external"/>
           <role-id>external</role-id>
           <authorized-privilege>
              <title>Portal administration</title>
              <function-performed>Add/remove client users</function-performed>
              <function-performed>Create, modify and delete client applications</function-performed>
           </authorized-privilege>
        </user>
        <user uuid="ba7708c1-4041-48ab-9b7b-1ddb5e175fe0">
           <title>[SAMPLE]Program Director</title>
           <prop name="sensitivity" ns="https://fedramp.gov/ns/oscal">limited</prop>
           <annotation name="privilege-level" value="no-logical-access"/>
           <annotation name="type" value="internal"/>
           <role-id>program-director</role-id>
           <authorized-privilege>
              <title>Administrative Access Approver</title>
              <function-performed>Approves access requests for administrative accounts.</function-performed>
           </authorized-privilege>
           <authorized-privilege>
              <title>Access Approver</title>
              <function-performed>Approves access requests for administrative accounts.</function-performed>
           </authorized-privilege>
        </user>

<!-- List components -->
        {% for component in system.producer_elements %}
        <component uuid="{{ component.uuid }}" component-type="{{ component.element_type }} [system, validation, software, os, service, policy, interconnection]">
          <title>{{ component.name }}</title>
          <description>
            {% if component.description %}{{ component.description|safe}}{% else %}<p>None.</p>{% endif %}
          </description>
          <status state="operational"/>
        </component>
        {% endfor %}

        <system-inventory>
           <inventory-item uuid="98e37f90-fbb5-4177-badb-9b55229cc183" asset-id="unique-asset-id">
              <description>
                 <p>Flat-File Example (No implemented-component).</p>
              </description>
              <prop name="ipv4-address">1.1.1.1</prop>
              <prop name="ipv6-address">0000:0000:0000:0000</prop>
              <prop name="virtual">no</prop>
              <prop name="public">no</prop>
              <prop name="fqdn">dns.name</prop>
              <prop name="uri">uniform.resource.identifier</prop>
              <prop name="netbios-name">netbios-name</prop>
              <prop name="mac-address">00:00:00:00:00:00</prop>
              <prop name="software-name">software-name</prop>
              <prop name="version">V 0.0.0</prop>
              <prop name="asset-type">os</prop>
              <prop name="vendor-name" ns="https://fedramp.gov/ns/oscal">Vendor Name</prop>
              <prop name="model">Model Number</prop>
              <prop name="patch-level">Patch-Level</prop>
              <prop name="serial-number">Serial #</prop>
              <prop name="asset-tag">Asset Tag</prop>
              <prop name="vlan-id">VLAN Identifier</prop>
              <prop name="network-id">Network Identifier</prop>
              <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">infrastructure</prop>
              <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">database</prop>
              <prop name="validation" ns="https://fedramp.gov/ns/oscal">component-id</prop>
              <annotation name="allows-authenticated-scan" value="no">
                 <remarks>
                    <p>If no, explain why. If yes, omit remarks field.</p>
                 </remarks>
              </annotation>
              <annotation name="baseline-configuration-name" value="Baseline Config. Name"/>
              <annotation name="physical-location" value="Physical location of Asset"/>
              <annotation name="is-scanned" value="yes">
                 <remarks>
                    <p>If no, explain why. If yes, omit remarks field.</p>
                 </remarks>
              </annotation>
              <annotation name="function" value="Required brief, text-based description.">
                 <remarks>
                    <p>Optional, longer, formatted description.</p>
                 </remarks>
              </annotation>
              <responsible-party role-id="asset-owner">
                 <party-uuid>db234cb7-1776-425c-9ac4-b067c1723011</party-uuid>
              </responsible-party>
              <responsible-party role-id="asset-administrator">
                 <party-uuid>b306f5af-b93a-4a7f-a2b2-37a44fc92a79</party-uuid>
              </responsible-party>
              <remarks>
                 <p>COMMENTS: Additional information about this item.</p>
              </remarks>
           </inventory-item>
           <inventory-item uuid="c916d3c5-229e-4786-bf3f-4d71baa0e7a5" asset-id="unique-asset-ID">
              <description>
                 <p>Component Inventory Example</p>
              </description>
              <prop name="ipv4-address">2.2.2.2</prop>
              <prop name="ipv6-address">0000:0000:0000:0000</prop>
              <prop name="mac-address">00:00:00:00:00:00</prop>
              <prop name="virtual">no</prop>
              <prop name="public">no</prop>
              <prop name="fqdn">dns.name</prop>
              <prop name="uri">uniform.resource.locator</prop>
              <prop name="netbios-name">netbios-name</prop>
              <prop name="patch-level">Patch-Level</prop>
              <annotation name="baseline-configuration-name" value="Baseline Configuration Name"/>
              <annotation name="physical-location" value="Physical location of Asset"/>
              <annotation name="scan-authenticated" ns="https://fedramp.gov/ns/oscal" value="no">
                 <remarks>
                    <p>If no, explain why. If yes, omit remark.</p>
                 </remarks>
              </annotation>
              <annotation name="scan-latest" ns="https://fedramp.gov/ns/oscal" value="yes">
                 <remarks>
                    <p>If no, explain why. If yes, omit remark.</p>
                 </remarks>
              </annotation>
              <responsible-party role-id="asset-owner">
                 <party-uuid>3360e343-9860-4bda-9dfc-ff427c3dfab6</party-uuid>
              </responsible-party>
              <responsible-party role-id="asset-administrator">
                 <party-uuid>b306f5af-b93a-4a7f-a2b2-37a44fc92a79</party-uuid>
              </responsible-party>
              <implemented-component component-id="05ceb8df-52e7-49db-9719-891723f366bd"/>
              <remarks>
                 <p>COMMENTS: If needed, provide additional information about this inventory item.</p>
              </remarks>
           </inventory-item>
           <inventory-item uuid="37c00d5a-ccf2-4112-a0ee-8460be8cff40" asset-id="unique-asset-id">
              <description>
                 <p>None.</p>
              </description>
              <prop name="ipv4-address">3.3.3.3</prop>
              <annotation name="is-scanned" value="yes"/>
              <implemented-component component-id="1541015b-6d19-42cb-a991-624cc082ed4d"/>
           </inventory-item>
           <inventory-item uuid="fb7a84fb-7e30-4f5b-9997-2ecd4d270bdd" asset-id="unique-asset-id">
              <description>
                 <p>None.</p>
              </description>
              <prop name="ipv4-address">4.4.4.4</prop>
              <annotation name="is-scanned" value="yes"/>
              <implemented-component component-id="05ceb8df-52e7-49db-9719-891723f366bd"/>
           </inventory-item>
           <inventory-item uuid="779d4e89-bba6-432c-b50d-d699fe534129" asset-id="unique-asset-id">
              <description>
                 <p>None.</p>
              </description>
              <prop name="ipv4-address">5.5.5.5</prop>
              <annotation name="is-scanned" value="yes"/>
              <implemented-component component-id="8f230d84-2f9b-44a3-acdb-019566ab2554"/>
           </inventory-item>
           <inventory-item uuid="20b207d5-5e77-4501-b02d-5d2a6e88db85" asset-id="unique-asset-id">
              <description>
                 <p>None.</p>
              </description>
              <prop name="ipv4-address">6.6.6.6</prop>
              <annotation name="is-scanned" value="no">
                 <remarks>
                    <p>Asset wasn't running at time of scan.</p>
                 </remarks>
              </annotation>
              <implemented-component component-id="05ceb8df-52e7-49db-9719-891723f366bd"/>
           </inventory-item>
           <inventory-item uuid="79b4f0d1-91ab-49e8-af28-045c12aa9272" asset-id="unique-asset-id">
              <description>
                 <p>None.</p>
              </description>
              <prop name="ipv4-address">7.7.7.7</prop>
              <annotation name="is-scanned" value="yes"/>
              <implemented-component component-id="1541015b-6d19-42cb-a991-624cc082ed4d"/>
           </inventory-item>
           <inventory-item uuid="b31b360d-b58b-4c7c-b344-68e17238d858" asset-id="unique-asset-id">
              <description>
                 <p>None.</p>
              </description>
              <prop name="ipv4-address">8.8.8.8</prop>
              <annotation name="is-scanned" value="no">
                 <remarks>
                    <p>Asset wasn't running at time of scan.</p>
                 </remarks>
              </annotation>
              <implemented-component component-id="05ceb8df-52e7-49db-9719-891723f366bd"/>
           </inventory-item>
           <inventory-item uuid="55b55b3d-3bd9-409a-bc87-3b9a2074bacd" asset-id="10.10.10.0">
              <description>
                 <p>IPv4 Production Subnet.</p>
              </description>
              <prop name="ipv4-subnet">10.10.10.0/24</prop>
              <annotation name="is-scanned" value="yes"/>
           </inventory-item>
           <inventory-item uuid="c0dbefa1-c8e8-4ca8-bd73-67cb7b1fa3f6" asset-id="10.10.20.0">
              <description>
                 <p>IPv4 Management Subnet.</p>
              </description>
              <prop name="ipv4-subnet">10.10.20.0/24</prop>
              <annotation name="is-scanned" value="yes"/>
           </inventory-item>
        </system-inventory>
     </system-implementation>
     <!-- Section 13 -->
     <control-implementation>
        <description>
           <p>FedRAMP SSP Template Section 13</p>
           <p>This description field is required by OSCAL. FedRAMP does not require any specific information here.</p>
        </description>

      <!-- Loop through controls -->
      {% set meta = {"current_family_title": "", "current_control": "", "current_control_part": "", "control_count": 0, "current_parts": []} %}
      {% for control in system.root_element.selected_controls_oscal_ctl_ids %}{% set var_ignore = meta.update({"control_count": meta['control_count'] + 1}) %}
        {% if control.lower() in control_catalog %}
        <implemented-requirement control-id="{{ control.lower() }}" uuid="{{ system.control_implementation_as_dict[control]['elementcontrol_uuid'] }}" control-title="{{ control_catalog[control.lower()]['title'] }}">
           <statement statement-id="{{ control.lower() }}_stmt" uuid="{{ system.control_implementation_as_dict[control]['combined_smt_uuid'] }}">
              <description>
                 <p>{{ control_catalog[control.lower()]['title'] }}</p>
                 {{control_catalog[control.lower()]['description']|safe}}
              </description>
              {% if control in system.control_implementation_as_dict %}{% for smt in system.control_implementation_as_dict[control]['control_impl_smts'] %}
              <by-component component-name="{{ smt.producer_element.name }}" component-id="{{ smt.producer_element.uuid }}" uuid="{{ smt.uuid }}" status="{{ smt.status }}">
                <description>
                  {{ smt.body|safe }}
                </description>
              </by-component>{% endfor %}{% else %}{% endif %}
           </statement>
        </implemented-requirement>
        {% endif %}{% endfor %}
     </control-implementation>

     <!-- Table 15-1 Names of Provided Attachments -->
     <back-matter>
        <!-- Section 12, Table 12-1, Table 12-2 -->
        <resource uuid="3a5ca2de-0f66-47e6-844d-6ccdf214b767">
           <title>FedRAMP Applicable Laws and Regulations</title>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">fedramp-citations</prop>
           <rlink href="https://www.fedramp.gov/assets/resources/templates/SSP-A12-FedRAMP-Laws-and-Regulations-Template.xlsx" />
        </resource>
        <resource uuid="12da89ef-51dd-4404-948d-e9f0e25b961e">
           <title>FedRAMP Master Acronym and Glossary</title>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">fedramp-acronyms</prop>
           <rlink href="https://www.fedramp.gov/assets/resources/documents/FedRAMP_Master_Acronym_and_Glossary.pdf" />
        </resource>
        <resource uuid="d45612a9-cf25-4ef6-b2dd-69e38ba2967a">
           <title>[SAMPLE]Name or Title of Document</title>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">law</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Publication Date</prop>
           <doc-id type="doi">Identification Number</doc-id>
           <rlink href="https://domain.example/path/to/document.pdf"/>
        </resource>
        <resource uuid="a8a0cc81-800f-479f-93d3-8b8743d9b98d">
           <title>[SAMPLE]Privacy-Related Law Citation</title>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">law</prop>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">pii</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Publication Date</prop>
           <doc-id type="doi">Identification Number</doc-id>
           <rlink href="https://domain.example/path/to/document.pdf"/>
        </resource>
        <resource uuid="545e75c3-537f-48fe-9630-95337916d982">
           <title>[SAMPLE]Regulation Citation</title>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">regulation</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Publication Date</prop>
           <doc-id type="doi">Identification Number</doc-id>
           <rlink href="https://domain.example/path/to/document.pdf"/>
        </resource>
        <resource uuid="9d6cf2b4-8e88-4040-a33c-7bc206553a1a">
           <title>[SAMPLE]Interconnection Security Agreement Title</title>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
        </resource>
        <resource uuid="31a46c4f-2959-4287-bc1c-67297d7da60b">
           <desc>CSP Logo</desc>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">prepared-for-logo</prop>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">csp-logo</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./logo.png" media-type="image/png"/>
           <base64>00000000</base64>
        </resource>
        <resource uuid="c5866ad8-8ed7-49b4-844a-0276fa9f8f51">
           <desc>Preparer Logo</desc>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">prepared-by-logo</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./party-1-logo.png" media-type="image/png"/>
           <base64>00000000</base64>
        </resource>
        <resource uuid="0846b6ef-cfa4-4bb3-8280-717f7e7b04d4  ">
           <desc>FedRAMP Logo</desc>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">fedramp-logo</prop>
           <rlink href="https://github.com/GSA/fedramp-automation/raw/master/assets/FedRAMP_LOGO.png"
           />
        </resource>
        <resource uuid="2c1747d6-874a-49a2-8488-2fd9735416bf">
           <desc>3PAO Logo</desc>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">3pao-logo</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./logo.png" media-type="image/png"/>
           <base64>00000000</base64>
        </resource>
        <resource uuid="d2eb3c18-6754-4e3a-a933-03d289e3fad5">
           <desc>The primary authorization boundary diagram.</desc>
           <!-- Use rlink and/or base64 -->
           <rlink href="./diagrams/boundary.png"/>
           <base64>00000000</base64>
           <remarks>
              <p>Section 9.2, Figure 9-1 Authorization Boundary Diagram (graphic)</p>
              <p>This should be referenced in the
                 system-characteristics/authorization-boundary/diagram/link/@href flag using a value
                 of "#d2eb3c18-6754-4e3a-a933-03d289e3fad5"</p>
           </remarks>
        </resource>
        <resource uuid="61081e81-850b-43c1-bf43-1ecbddcb9e7f">
           <desc>The primary network diagram.</desc>
           <!-- Use rlink and/or base64 -->
           <rlink href="./diagrams/network.png"/>
           <base64>00000000</base64>
           <remarks>
              <p>Section 9.4, Figure 9-2 Network Diagram (graphic)</p>
              <p>This should be referenced in the
                 system-characteristics/network-architecture/diagram/link/@href flag using a value
                 of "#61081e81-850b-43c1-bf43-1ecbddcb9e7f"</p>
           </remarks>
        </resource>
        <resource uuid="ac5d7535-f3b8-45d3-bf3b-735c82c64547">
           <desc>The primary data flow diagram.</desc>
           <!-- Use rlink and/or base64 -->
           <rlink href="./diagrams/dataflow.png"/>
           <base64>00000000</base64>
           <remarks>
              <p>Section 10, Figure 10-1 Data Flow Diagram (graphic)</p>
              <p>This should be referenced in the
                 system-characteristics/data-flow/diagram/link/@href flag using a value
                 of "#ac5d7535-f3b8-45d3-bf3b-735c82c64547"</p>
           </remarks>
        </resource>
        <resource uuid="090ab379-2089-4830-b9fd-26d0729e22e9">
           <title>Policy Title</title>
           <desc>Policy document</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">policy</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./sample_policy.pdf"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Policy Attachment</p>
           </remarks>
        </resource>
        <resource uuid="ab300133-d749-4abb-b858-1cd6ffd8af9e">
           <title>Policy Title</title>
           <desc>Policy document</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">policy</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./sample_policy.pdf"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Policy Attachment</p>
           </remarks>
        </resource>
        <resource uuid="1002a58e-9e11-4aa6-9ab4-2bde52995952">
           <title>Procedure Title</title>
           <desc>Procedure document</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">procedure</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./sample_procedure.pdf"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Procedure Attachment</p>
           </remarks>
        </resource>
        <resource uuid="4bb1e2e5-261c-4b5c-b22c-e1627c2e8be6">
           <title>Procedure Title</title>
           <desc>Procedure document</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">procedure</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./sample_procedure.pdf"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Procedure Attachment</p>
           </remarks>
        </resource>
        <resource uuid="90a128ac-c850-48f6-8fff-a55692f80b41">
           <title>User's Guide</title>
           <desc>User's Guide</desc>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">user-guide</prop>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">guide</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./sample_guide.pdf"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: User's Guide Attachment</p>
           </remarks>
        </resource>
        <resource uuid="fab59751-b855-40cb-93c1-492562e20e18">
           <title>Privacy Impact Assessment</title>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">privacy-impact-assessment</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="./pia.docx"/>
           <base64 filename="pia.docx">00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Privacy Impact Assessment</p>
           </remarks>
        </resource>
        <resource uuid="489112e1-57f2-4c29-8dd0-95b1442fbf3b">
           <title>Document Title</title>
           <desc>Rules of Behavior</desc>
           <prop name="conformity" ns="https://fedramp.gov/ns/oscal">rules-of-behavior</prop>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">rob</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="https://sample"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Rules of Behavior (ROB)</p>
           </remarks>
        </resource>
        <resource uuid="c7860916-f2f4-43aa-b578-d48cf8e6d381">
           <title>Document Title</title>
           <desc>Contingency Plan (CP)</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">plan</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="https://sample"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Contingency Plan (CP) Attachment</p>
           </remarks>
        </resource>
        <resource uuid="ab56cf27-0dae-40d6-89b7-d750137309af">
           <title>Document Title</title>
           <desc>Configuration Management (CM) Plan</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">plan</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="https://sample"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Configuration Management (CM) Plan Attachment</p>
           </remarks>
        </resource>
        <resource uuid="3f771ab5-8016-4571-98d1-f0fb962e15e2">
           <title>Document Title</title>
           <desc>Incident Response (IR) Plan</desc>
           <prop name="type" ns="https://fedramp.gov/ns/oscal">plan</prop>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="https://sample"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Incident Response (IR) Plan Attachment</p>
           </remarks>
        </resource>
        <resource uuid="49fb4631-1da2-41ca-b0b3-e1b1006d4025">
           <title>Separation of Duties Matrix</title>
           <desc>Separation of Duties Matrix</desc>
           <prop name="publication" ns="https://fedramp.gov/ns/oscal">Document Date</prop>
           <prop name="version" ns="https://fedramp.gov/ns/oscal">Document Version</prop>
           <!-- Use rlink and/or base64 -->
           <rlink href="https://sample"/>
           <base64>00000000</base64>
           <remarks>
              <p>Table 15-1 Attachments: Separation of Duties Matrix Attachment</p>
           </remarks>
        </resource>
        <resource uuid="9f1aae37-7359-411f-86c1-768aaab85e63">
           <title>FedRAMP High Baseline</title>
           <rlink media-type="application/xml" href="https://raw.githubusercontent.com/usnistgov/OSCAL/v1.0.0-milestone3/content/fedramp.gov/xml/FedRAMP_HIGH-baseline_profile.xml" />
           <remarks>
              <p>Pointer to High baseline content in OSCAL.</p>
           </remarks>
        </resource>
        <resource uuid="890170c3-d4fa-4d25-ab96-8e4bf7cc237c">
           <title>FedRAMP Moderate Baseline</title>
           <rlink media-type="application/xml" href="https://raw.githubusercontent.com/usnistgov/OSCAL/v1.0.0-milestone3/content/fedramp.gov/xml/FedRAMP_MODERATE-baseline_profile.xml" />
           <remarks>
              <p>Pointer to Moderate baseline content in OSCAL.</p>
           </remarks>
        </resource>
        <resource uuid="2acaf846-5496-4d36-8565-9a15b48aef2c">
           <title>FedRAMP Low Baseline</title>
           <rlink media-type="application/xml" href="https://raw.githubusercontent.com/usnistgov/OSCAL/v1.0.0-milestone3/content/fedramp.gov/xml/FedRAMP_LOW-baseline_profile.xml" />
           <remarks>
              <p>Pointer to Low baseline content in OSCAL.</p>
           </remarks>
        </resource>
     </back-matter>
  </system-security-plan>
