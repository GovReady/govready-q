id: info_storage
title: Information Storage
format: html
...

<style>
  .dos-pta-form {
    font-family: TimesNewRoman, Times, serif;
    width: 650px;
    margin: auto;
  }

  .dos-pta-form h2 {
    font-size: 12pt;
    font-family: TimesNewRoman, Times, serif;
    background-color: rgb(89, 129, 187);
    padding: 4px 30px 4px 30px;
    color: white;
    font-weight: bold;
    margin: 0px 0px 0px 0px;
    margin-top: 2em;
  }

  .dos-pta-form .cell-full {
    border-left: 1px solid rgb(89, 129, 187);
    border-right: 1px solid rgb(89, 129, 187);
    border-bottom: 1px solid rgb(89, 129, 187);padding: 4px 30px 4px 30px;
    font-family: TimesNewRoman, Times, serif;
  }

  .dos-pta-form .cell-left {
    border-left: 1px solid rgb(89, 129, 187);
    border-bottom: 1px solid rgb(89, 129, 187);
    padding: 4px 30px 4px 30px;
    width: 49.5%;
    display: table-cell;
    height: 100%;
  }

  .dos-pta-form .cell-right {
    border-left: 1px solid rgb(89, 129, 187);
    border-right: 1px solid rgb(89, 129, 187);
    border-bottom: 1px solid rgb(89, 129, 187);
    padding: 4px 30px 4px 30px;
    width: 49.5%;
    display: table-cell;
    height: 100%;
    vertical-align: top;
  }

  .footer {
    font-size: .75em; 
    text-align: left;
    margin:auto;
    margin-top: 2em;
  }
</style>
<!-- Parameters
- id: info_storage_intro
- id: storage_system_type
- id: storage_system
- id: electronic_storage_input_type
- id: electronic_storage_input
- id: retrieve
- id: retrieve_unique_id_description
- id: retrieve_non_personal_description
- id: records_retention_schedule
- id: records_disposal_verification
- id: information_shared_agency
- id: information_shared_agency_description
- id: information_shared_external
- id: information_shared_external_description
-->

<div class="dos-pta-form">

  <h2>3. How will DOS store the IC/form responses?</h2>
  <div class="cell-left">
   a. How will DOS store the original, completed IC/forms?
  </div>
  <div class="cell-right">
    {{ storage_system_type.text }}
    <div>
      {% if storage_system_type == 'paper' %}. Please describe.
      {% elif storage_system_type == 'electronic' %}. Please describe the IT system that will store the data from the form.
      {% elif storage_system_type == 'scanned_forms' %} (completed forms are scanned into an electronic repository). Please describe the electronic repository.
      {% endif %}
    </div>
    {{ storage_system }}
  </div>
  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
    b. If electronic, how does DOS input the responses into the IT system?
  </div>
  <div class="cell-right">
    {{ electronic_storage_input_type.text }}
    {% if electronic_storage_input_type == 'manually' %} (data elements manually entered). Please describe.
    {% elif electronic_storage_input_type == 'automatically' %} Please describe.
    {% endif %}
    {{ electronic_storage_input }}
  </div>
  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
   c. How would a user search the information submitted on the forms, <i>i.e.,</i> how is the information retrieved?
  </div>
  <div class="cell-right">
    {{ retrieve.text }}
    <div>
      {% if retrieve == 'retrieve_unique_id' %}. <i>Please describe.</i> If information is retrieved by personal identifier, please submit a Privacy Act Statement with this PTA.

      {% elif retrieve == 'retrieve_non_personal' %}. Please describe the IT system that will store the data from the form.
      {% endif %}
    </div>
    {{ storage_system }}
  </div>
  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
   d. What is the records retention schedule(s)?  <i>Include the records schedule number.</i>
  </div>
  <div class="cell-right">
    {{ records_retention_schedule }}
  </div>
  <div class="cell-full" style="height:0px; border-top: 0px black solid;"></div>

  <div class="cell-left">
   e. How do you ensure that records are disposed of or deleted in accordance with the retention schedule?
  </div>
  <div class="cell-right">
    {{ records_disposal_verification }}
  </div>

  <div class="cell-full">
    f. Is any of this information shared outside of the original program/office? <i>If yes, describe where (other offices or DOS components or external entities) and why. What are the authorities of the receiving party?</i>
  </div>
  <div class="cell-full">
    {% if information_shared_agency == 'yes' %}Yes, information is shared with other DOS components or offices. Please describe.
    <div>{{ information_shared_agency_description }}</div>
    {% endif %}
    {% if information_shared_external == 'yes' %}Yes, information is shared external to DOS with other federal agencies, state/local partners, international partners, or non-governmental entities. Please describe.
    <div>{{ information_shared_external_description }}</div>
    {% endif %}
    {% if information_shared_agency == 'yes' and information_shared_external == 'no' %}No. Information on this form is not shared outside of the collecting office.
    {% endif %}
  </div>

  {% if privacy_act_statement %}
  <h2>Submitted Privacy Act Statement</h2>
  <div class="cell-full">
    <p>The following Privact Act Statement has been submitted with this PTA.</p>
    <p><a href="{{ privacy_act_statement.url }}">View Privacy Act Statement</a></p>
  </div>

  {% endif %}


  <div class="footer">
    <span>Privacy Threshold Analysis – IC/Form</span>
    <span style="margin-left: 200px;">Version number: 04-2016</span>
  </div>

</div>
