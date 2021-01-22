id: system_info
format: markdown
title: System Information
placement: action-buttons
...

<style>
  table {
    min-width: 450px;
  }

  td {
    padding: 8px;
  }
</style>

<div style="width: 650px; margin: auto; font-family: TimesNewRoman, Times, serif; ">

<div style="font-weight: bold;">
  <p style="text-align: center;">
    SYSTEM INFORMATION
  </p>
</div>

<div>
  <p>{{system_short_name}} is a {% filter lower %}{{system_type.text}}{% endfiletr %} hosted in the {{system_hosting.text}} environment.
  </p>
  <p>
    {{system_description}}
  </p>
</div>

<div style="text-align: center;">
  <table border=1 style="margin:auto; font-family: TimesNewRoman, Times, serif; text-align: center;">
    <tr>
      <td>Organization</td><td>{{system_org}}</td>
    </tr>
    <tr>
      <td>System Owner</td><td>{{system_owner}}</td>
    </tr>
    <tr>
      <td>Program Manager</td><td>{{system_pm}}</td>
    </tr>
  </table>
</div>

</div>