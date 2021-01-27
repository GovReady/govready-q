
        <component uuid="60f92bcf-f353-4236-9803-2a5d417555f4" component-type="system">
           <title>This System</title>
           <description>
              <p>The entire system as depicted in the system authorization boundary</p>
           </description>
           <status state="operational"/>
        </component>
        <component uuid="95beec7e-6f82-4aaa-8211-969cd7c1f1ab" component-type="validation">
           <title>[SAMPLE]Module Name</title>
           <description>
              <p>[SAMPLE]FIPS 140-2 Validated Module</p>
           </description>
           <prop name="cert-no" ns="https://fedramp.gov/ns/oscal">0000</prop>
           <link
              href="https://csrc.nist.gov/projects/cryptographic-module-validation-program/Certificate/0000"/>
           <status state="operational"/>
        </component>
        <component uuid="05ceb8df-52e7-49db-9719-891723f366bd" component-type="software">
           <title>[SAMPLE]Product Name</title>
           <description>
              <p>FUNCTION: Describe typical component function.</p>
           </description>
           <prop name="asset-type">os</prop>
           <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">infrastructure</prop>
           <prop name="vendor-name" ns="https://fedramp.gov/ns/oscal">Vendor Name</prop>
           <prop name="model">Model Number</prop>
           <prop name="version">Version Number</prop>
           <prop name="patch-level">Patch Level</prop>
           <prop name="validation" ns="https://fedramp.gov/ns/oscal">fips-module-1</prop>
           <status state="operational"/>
           <remarks>
              <p>COMMENTS: Provide other comments as needed.</p>
           </remarks>
        </component>
        <component uuid="1541015b-6d19-42cb-a991-624cc082ed4d" component-type="hardware">
           <title>[SAMPLE]Product</title>
           <description>
              <p>FUNCTION: Describe typical component function.</p>
           </description>
           <prop name="asset-type">database</prop>
           <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">infrastructure</prop>
           <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">database</prop>
           <prop name="vendor-name" ns="https://fedramp.gov/ns/oscal">Vendor Name</prop>
           <prop name="model">Model Number</prop>
           <prop name="version">Version Number</prop>
           <status state="operational"/>
           <responsible-role role-id="asset-administrator">
              <party-uuid>b306f5af-b93a-4a7f-a2b2-37a44fc92a79</party-uuid>
           </responsible-role>
           <responsible-role role-id="asset-owner">
              <party-uuid>36b8d6c0-3b25-42cc-b529-cf4066145cdd</party-uuid>
           </responsible-role>
           <remarks>
              <p>COMMENTS: Provide other comments as needed.</p>
           </remarks>
        </component>
        <component uuid="6617f60b-8bac-422d-9939-94f43ddc0f7a" component-type="os">
           <title>OS Sample</title>
           <description>
              <p>None</p>
           </description>
           <prop name="asset-type">os</prop>
           <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">infrastructure</prop>
           <annotation name="baseline-configuration-name" value="Baseline Config. Name"/>
           <annotation name="allows-authenticated-scan" value="yes"/>
           <status state="operational"/>
        </component>
        <component uuid="120f1404-7c9f-4856-a247-63bd89d9e769" component-type="software">
           <title>Database Sample</title>
           <description>
              <p>None</p>
           </description>
           <prop name="asset-type">database</prop>
           <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">database</prop>
           <annotation name="baseline-configuration-name" value="Baseline Config. Name"/>
           <annotation name="allows-authenticated-scan" value="yes"/>
           <status state="operational"/>
        </component>
        <component uuid="8f230d84-2f9b-44a3-acdb-019566ab2554" component-type="software">
           <title>Appliance Sample</title>
           <description>
              <p>None</p>
           </description>
           <prop name="asset-type">appliance</prop>
           <prop name="scan-type" ns="https://fedramp.gov/ns/oscal">web</prop>
           <prop name="login-url">https://admin.offering.com/login</prop>
           <annotation name="baseline-configuration-name" value="Baseline Config. Name"/>
           <annotation name="allows-authenticated-scan" value="no">
              <remarks>
                 <p>Vendor appliance. No admin-level access.</p>
              </remarks>
           </annotation>
           <status state="operational"/>
        </component>
        <!-- ****** SERVICES ARE NOW COMPONENTS WITH type='service' -->
        <component uuid="d5841417-de4c-4d84-ab3c-39dd1fd32a96" component-type="service">
           <title>[SAMPLE]Service Name</title>
           <description><p>Describe the service</p></description>
           <purpose>Describe the reason the service is needed.</purpose>
           <prop name="used-by" ns="https://fedramp.gov/ns/oscal">What uses this service?</prop>
           <prop name="protocol"></prop>
           <status state="operational" />
           <protocol name="http">
              <port-range start="80" end="80" transport="TCP"/>
           </protocol>
           <protocol name="https">
              <port-range start="443" end="443" transport="TCP"/>
           </protocol>
           <remarks>
              <p>Section 10.2, Table 10-1. Ports, Protocols and Services</p>
              <p><b>SERVICES ARE NOW COMPONENTS WITH type='service'</b></p>
           </remarks>
        </component>
        <!-- Section 11 Table 11-1 System Interconnections and  Section 13 Table 13-3 CA-3 Authorized Connections -->
        <component uuid="2812ef51-61e7-4505-afbb-da5a073a2a5b" component-type="interconnection">
           <title>[EXAMPLE]Authorized Connection Information System Name</title>
           <description><p>Briefly describe the interconnection.</p></description>
           <prop name="service-processor" ns="https://fedramp.gov/ns/oscal">[SAMPLE]Telco Name</prop>
           <prop name="ipv4-address" class="local" ns="https://fedramp.gov/ns/oscal">10.1.1.1</prop>
           <prop name="ipv4-address" class="remote" ns="https://fedramp.gov/ns/oscal">10.2.2.2</prop>
           <prop name="direction" ns="https://fedramp.gov/ns/oscal">incoming-outgoing</prop>
           <prop name="information" ns="https://fedramp.gov/ns/oscal">Describe the information being transmitted.</prop>
           <prop name="port" ns="https://fedramp.gov/ns/oscal">80</prop>
           <prop name="circuit" ns="https://fedramp.gov/ns/oscal">1</prop>
           <annotation name="connection-security" ns="https://fedramp.gov/ns/oscal" value="ipsec">
              <remarks>
                 <p>If "other", remarks are required. Optional otherwise.</p>
              </remarks>
           </annotation>
           <link href="#9d6cf2b4-8e88-4040-a33c-7bc206553a1a" rel="agreement"/>
           <status state="operational" />
           <responsible-role role-id="isa-poc-remote">
              <party-uuid>09ad840f-aa79-43aa-9f22-25182c2ab11b</party-uuid>
           </responsible-role>
           <responsible-role role-id="isa-poc-local">
              <party-uuid>09ad840f-aa79-43aa-9f22-25182c2ab11b</party-uuid>
           </responsible-role>
           <responsible-role role-id="isa-authorizing-official-remote">
              <party-uuid>09ad840f-aa79-43aa-9f22-25182c2ab11b</party-uuid>
           </responsible-role>
           <responsible-role role-id="isa-authorizing-official-local">
              <party-uuid>09ad840f-aa79-43aa-9f22-25182c2ab11b</party-uuid>
           </responsible-role>
           <remarks>
              <p>Optional notes about this interconnection</p>
           </remarks>
        </component>




<!--IGNORE -->
        <implemented-requirement control-id="ac-1" uuid="eee8697a-bc39-45aa-accc-d3e534932efb">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ac-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ac-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ac-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ac-1_stmt.a" uuid="fb4d039a-dc4f-46f5-9c1f-f6343eaf69bc">
              <!-- Service Provider Responsibility -->
              <description>
                 <p>Describe how Part a is satisfied.</p>
              </description>
           </statement>
           <statement statement-id="ac-1_stmt.a.1" uuid="0afdccce-b5ed-4127-ae19-cfbdd17d775e">
              <link href="#090ab379-2089-4830-b9fd-26d0729e22e9" rel="policy"/>
              <remarks>
                 <p>This identifies a policy (attached in resources) that satisfies this control.</p>
              </remarks>
           </statement>
           <statement statement-id="ac-1_stmt.a.2" uuid="ffaf5e02-3055-40df-bbeb-3b94e834a43f">
              <link href="#att-process-1" rel="process"/>
              <remarks>
                 <p>This identifies a process (attached in resources) that satisfies this control.</p>
              </remarks>
           </statement>
           <statement statement-id="ac-1_stmt.b.1" uuid="b46f97ec-55c1-4249-a9b9-3a228f1e3791">
              <description>
                 <p>Describe how Part b-1 is satisfied.</p>
              </description>
           </statement>
           <statement statement-id="ac-1_stmt.b.2" uuid="59c67969-3d5c-45f1-8e3e-1e642249633f">
              <description>
                 <p>Describe how Part b-2 is satisfied.</p>
              </description>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ac-2" uuid="7a36cf53-156d-4d1f-9a8b-433f61cc57b7">
           <prop name="leveraged-authorization-id" ns="https://fedramp.gov/ns/oscal">lva-1</prop>
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">Completion Date</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="partial">
              <remarks>
                 <p>Describe the portion of the control that is not satisfied.</p>
              </remarks>
           </annotation>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal"
              value="not-applicable">
              <remarks>
                 <p>Describe the justification for marking this control Not Applicable.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal"
              value="customer-configured">
              <remarks>
                 <p>Describe any customer-configured requirements for satisfying this control.</p>
              </remarks>
           </annotation>
           <responsible-role role-id="admin-unix"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ac-2_prm_1">
              <value>[SAMPLE]privileged, non-privileged</value>
           </set-parameter>
           <set-parameter param-id="ac-2_prm_2">
              <value>[SAMPLE]all</value>
           </set-parameter>
           <set-parameter param-id="ac-2_prm_3">
              <value>[SAMPLE]The Access Control Procedure</value>
           </set-parameter>
           <set-parameter param-id="ac-2_prm_4">
              <value>[SAMPLE]annually</value>
           </set-parameter>
           <statement statement-id="ac-2_stmt.a" uuid="24a85abb-25ad-4686-850c-5c0e8ab69a0c">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="8a72663c-28c7-41c2-8739-f1ee2d5761ac">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
              <!-- Inherited -->
              <by-component component-id="b7364f67-bf65-4df2-b756-4b9c6b1c4a52" uuid="84de735f-ba37-4bb4-b784-79760f986a40">
                 <description>
                    <p>For the portion inherited from an underlying FedRAMP-authorized provider,
                       describe <strong>what</strong> is inherited.</p>
                 </description>
              </by-component>
              <!-- Customer Responsibility -->
              <by-component component-id="cae07d12-8566-443a-95de-7596b9cac953" uuid="13db02bb-1f33-4f79-8711-ed47c2c3d337">
                 <description>
                    <p>For the portion of the control that must be configured by or provided by the
                       customer, describe the customer responsibility here. This is what will appear
                       in the Customer Responsibility Matrix.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="at-1" uuid="c332a6f8-bbe6-4ee9-aaea-d89d251c68df">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="at-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="at-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="at-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="at-1_stmt.a" uuid="ee5a11fb-9bae-4680-8f8c-575c85d47355">
              <description>
                 <p>Component-based Approach</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="d3bdee1c-7d84-4ed4-8950-e13256edb7fa">
                 <description>
                    <p>Describe how Part a is satisfied.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="at-1_stmt.a.1" uuid="2e8ec7ce-c9c6-4f5f-9d50-3a3b9d3acf65">
              <link href="#090ab379-2089-4830-b9fd-26d0729e22e9" rel="policy"/>
              <remarks>
                 <p>This identifies a policy (attached in resources) that satisfies this control.</p>
              </remarks>
           </statement>
           <statement statement-id="at-1_stmt.a.2" uuid="e7f9b618-c092-4b8b-b416-0ee477026726">
              <link href="#att-process-1" rel="process"/>
              <remarks>
                 <p>This identifies a process (attached in resources) that satisfies this control.</p>
              </remarks>
           </statement>
           <statement statement-id="at-1_stmt.b.1" uuid="29192f0b-edb1-4820-b951-65ffdc64bb3e">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="5a5e5c3e-1108-47f1-a83f-05e0394219db">
                 <description>
                    <p>Describe how Part b-1 is satisfied.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="at-1_stmt.b.2" uuid="23a9bfa7-6e3f-4e00-a120-791b26a9157e">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="fcc63699-04ab-4b69-b7b9-a13bee6685b3">
                 <description>
                    <p>Describe how Part b-2 is satisfied.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="au-1" uuid="381c8d0c-e6ec-41a9-9b16-01657226c70f">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="au-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="au-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="au-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="au-1_stmt.a" uuid="9a2bd937-226e-4aaf-8261-2cf0c2e3aa10">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="30042cb9-ff85-472f-b769-68bd7bb5bbd9">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="au-1_stmt.b.1" uuid="d01f186f-a14f-4e22-b069-84a55e48a112">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="f41962c7-b53b-46f8-a84f-4aba25904bb8">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="au-1_stmt.b.2" uuid="ea153acb-2bd0-41d9-8ebd-ba022d31230a">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="9ad59f0d-17a2-4f3f-af6a-a8529d692195">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ca-1" uuid="43e388d9-3854-44f6-8c6f-17a6d51ee6a2">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ca-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ca-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ca-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ca-1_stmt.a" uuid="e7bd0a7e-5f92-4769-8cd3-76ad2f663a5c">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="e5815f1d-ec94-4d98-8896-ec57e339bd7b">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ca-1_stmt.b.1" uuid="b2c3ec86-b976-4e5a-9dc3-4ac2d570765e">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="ca6b2bd5-3ddf-4167-a942-06e1955e49f8">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ca-1_stmt.b.2" uuid="e9474eb8-36d6-4eab-abeb-f9bd17e66b22">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="507b8b9d-2d40-4748-81c9-c5a13c8f8f05">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="cm-1" uuid="c8e45d78-2afe-42ae-80e1-c1e2499a0346">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="cm-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="cm-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="cm-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="cm-1_stmt.a" uuid="52339583-19b6-4774-9213-50b9f42fe51f">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="2916ebd5-c45a-466e-b8e9-00dd15b0c94d">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="cm-1_stmt.b.1" uuid="f9cc6f3f-c64f-4fae-9a32-f964ebdc8e74">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="678db1d2-a538-4986-ac94-63da312fe3f9">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="cm-1_stmt.b.2" uuid="c548a71f-41d6-4e8c-b400-1764379348c4">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="a871cf91-04c7-4e03-9df6-80b3d5afc9bf">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="cp-1" uuid="13af9343-73e7-4d71-b386-9a0844fa7e45">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="cp-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="cp-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="cp-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="cp-1_stmt.a" uuid="8bde1fa5-eb81-4a1b-9e6e-5827e176025a">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="157d7751-938c-441f-9299-02a339d98532">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="cp-1_stmt.b.1" uuid="2fc9eec1-a49f-4cfa-9f7b-c702a1e21619">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="6358db78-bab1-4139-b512-f65d3e48248b">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="cp-1_stmt.b.2" uuid="db5b3977-bd51-4505-b3e2-1597bbd4d930">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="3de33bbe-1a15-4d10-b35d-56fd85e24571">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ia-1" uuid="4050c933-3ecc-4a8d-8da7-391364685cbb">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ia-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ia-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ia-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ia-1_stmt.a" uuid="ba92e479-705f-47a4-a763-dfc098ba239d">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="5add335d-7375-49f0-843c-ac994e4d147b">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ia-1_stmt.b.1" uuid="dba8c469-5758-497e-9856-e472a2e08677">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="b04d86a0-b68c-41f0-9c0b-88a8daa457b7">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ia-1_stmt.b.2" uuid="b56e37b1-1f4c-479b-bfa1-a2773c2eebfd">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="c8fde380-9a41-404a-a88b-c20479a21618">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ir-1" uuid="229846dc-83cc-4ff2-a9ed-210490a343d9">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ir-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ir-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ir-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ir-1_stmt.a" uuid="7284efc2-d953-486c-ab8a-3caef6ce06c3">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="7b385445-5e7b-4656-98f1-0f1353aab59e">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ir-1_stmt.b.1" uuid="75c37e1a-6e8d-4ef0-99f4-c16f7995706c">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="e7ae4685-2e30-4e00-9ada-b00b5eaf5578">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ir-1_stmt.b.2" uuid="900591ec-2006-4622-bc87-59828d884d4f">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="f443c391-479d-492d-b7e9-55c9c2c107be">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ma-1" uuid="f0c6b63f-6b94-448f-bb16-db3d54b91734">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ma-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ma-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ma-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ma-1_stmt.a" uuid="d609e538-3976-418e-a368-58fc75cd03c0">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="93a9b046-63c4-4628-8547-39bc7d8df70c">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ma-1_stmt.b.1" uuid="df1a6dd8-9e18-4408-8783-cb30e0413f22">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="ad14f76a-a3eb-4349-8f6c-54cd99f1c040">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ma-1_stmt.b.2" uuid="f02f759d-7d4c-41f2-b153-f3cc1e157e39">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="32b337f6-eb61-4945-a139-4d2ae7737488">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="mp-1" uuid="fa3a9747-3451-456a-aae9-9896e03a52c8">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="mp-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="mp-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="mp-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="mp-1_stmt.a" uuid="bab45ad3-65ee-43bc-9c3e-c3e4e2db8001">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="6668f521-4d5c-4317-868f-804878675bf2">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="mp-1_stmt.b.1" uuid="ca35d4a5-ca73-4b3a-aa66-6c712c7a4a49">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="57e65240-5b41-40ee-89b1-f75d8fb259ad">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="mp-1_stmt.b.2" uuid="0c5c6eda-9644-46f2-a29c-16fe4e248621">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="ea6c7fa7-ccbf-414c-8c6b-9c928e914b35">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="pe-1" uuid="a85ff28e-517c-4455-8bd4-866103a2c94a">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="pe-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="pe-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="pe-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="pe-1_stmt.a" uuid="11fd3e46-4735-4986-91bc-747345fe608a">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="dceb4401-c1fd-41a7-9e07-8d82a8042e61">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="pe-1_stmt.b.1" uuid="a37f91e2-190d-40f7-829c-39776c14c8b4">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="bbd2b372-b57d-4a3a-90c2-2189dd23664b">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="pe-1_stmt.b.2" uuid="f3d57138-916c-4064-b2fc-aa8dd76849f8">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="f4a94538-220f-4f73-9487-73b72b68813e">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="pl-1" uuid="97ba1f95-92a8-480b-a489-960661e4206b">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="pl-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="pl-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="pl-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="pl-1_stmt.a" uuid="ec7af577-ff22-46bf-ac0a-cf9d75c72ebb">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="679837fb-601e-4517-abe6-11ff6fc551b4">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="pl-1_stmt.b.1" uuid="438f3e29-670a-49f2-8b9f-05d951318294">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="ddce2988-ce9b-4f15-a427-6f18e4ba1817">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="pl-1_stmt.b.2" uuid="96a4d13c-bd2b-4038-96c5-0f923f404bbd">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="18d7c02e-f21b-4cd2-bf33-d27971ced47f">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ps-1" uuid="5e7498de-b540-4a28-b041-4381b023e98a">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ps-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ps-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ps-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ps-1_stmt.a" uuid="afe1703d-5e59-460b-b048-41b49699c5a1">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="7d6cafb2-b613-4807-ad61-4f0f649bd5ee">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ps-1_stmt.b.1" uuid="956c93e2-cf8f-482c-aaf7-91ab44c7cbd6">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="f4fbfbc2-1a94-456d-a713-9d547f18a0c7">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ps-1_stmt.b.2" uuid="6926c688-3fb2-4ab8-9acb-cff0b5acd365">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="2f9c701a-0f3e-4e3d-beae-debb08c406ed">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="ra-1" uuid="789e6c0f-acda-4a94-9b48-7d41dd4c607c">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="ra-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="ra-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="ra-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="ra-1_stmt.a" uuid="8fe541ea-0920-42d0-8561-4e08f04d796c">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="5894d92b-05bf-4fc4-85dc-f5c37e112bc4">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ra-1_stmt.b.1" uuid="b0e9ed47-fe83-485d-8d79-979833543a83">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="c90ad6ee-5a40-4996-8e6c-d85ff3f7559e">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="ra-1_stmt.b.2" uuid="d9a38f95-ded1-4d1d-afe2-242987222ebd">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="d6f6ac98-4f15-45f2-9ecc-4447e96af44f">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="sa-1" uuid="55358f60-db9b-4d75-a313-5fa6c328273c">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="sa-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="sa-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="sa-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="sa-1_stmt.a" uuid="ae3f64be-2e62-4347-b06a-727bc28e4f9b">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="e5864f16-83f2-4faf-b7be-0810c6e58fc4">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="sa-1_stmt.b.1" uuid="959519a9-3e12-47bc-8d76-50d9ab0b6544">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="bed8f51a-1773-493c-8167-c83712e03f01">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="sa-1_stmt.b.2" uuid="9daa3848-9672-469c-9aa0-f363e3339123">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="518d4987-9436-4c1f-9e07-afa6b332f124">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="sc-1" uuid="9e2852c6-f48a-47b2-9ea5-77cbbb42b365">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="sc-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="sc-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="sc-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="sc-1_stmt.a" uuid="5e2e8372-c13b-4cf5-90c5-e8833a9fe241">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="88cfadba-043b-483b-8032-73344aa53c96">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="sc-1_stmt.b.1" uuid="8166980a-86c0-497d-87e4-453adfd0d4bd">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="9abaeb64-56d2-48a1-bd8d-7b55411d31ca">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="sc-1_stmt.b.2" uuid="eeea34ff-18ab-4c35-bf32-c74dbf746e7b">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="ad20ff50-8a7c-4ffc-a918-260960f6fb42">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
        <implemented-requirement control-id="si-1" uuid="81ba4fe8-1649-437b-9ecf-367fd87336e6">
           <prop name="planned-completion-date" ns="https://fedramp.gov/ns/oscal">2020-11-27Z</prop>
           <annotation name="implementation-status" ns="https://fedramp.gov/ns/oscal" value="planned">
              <remarks>
                 <p>Describe the plan to complete the implementation.</p>
              </remarks>
           </annotation>
           <annotation name="control-origination" ns="https://fedramp.gov/ns/oscal" value="sp-system"/>
           <responsible-role role-id="program-director"/>
           <set-parameter param-id="si-1_prm_1">
              <value>[replace with list of personnel or roles]</value>
           </set-parameter>
           <set-parameter param-id="si-1_prm_2">
              <value>[specify frequency]</value>
           </set-parameter>
           <set-parameter param-id="si-1_prm_3">
              <value>[specify frequency]</value>
           </set-parameter>
           <statement statement-id="si-1_stmt.a" uuid="915b10d2-2275-4d86-951a-eec23f9ee77a">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="682311e7-e3f7-4d94-acf9-131149887fda">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="si-1_stmt.b.1" uuid="2a5a6f7f-aeea-4ea4-be1e-859df4bf7521">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="80ee0fe9-7f87-4dfa-887a-ac3bb2131943">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
           <statement statement-id="si-1_stmt.b.2" uuid="c152bbde-57fc-4864-ac51-861bd8bb83b4">
              <description>
                 <p>Ignore.</p>
              </description>
              <!-- Service Provider Responsibility -->
              <by-component component-id="60f92bcf-f353-4236-9803-2a5d417555f4" uuid="78e8f2bb-67d7-49d3-a993-ce4bedcfbc47">
                 <description>
                    <p>For the portion of the control satisfied by the service provider, describe
                          <strong>how</strong> the control is met.</p>
                 </description>
              </by-component>
           </statement>
        </implemented-requirement>
<!-- /IGNORE -->
