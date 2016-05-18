{% extends "email/template" %}
{% block content %}
Hello,

{{invitation.from_user}} is inviting you {{invitation.purpose}} in {{invitation.from_project.title}} at GovReady Q.

> {{invitation.text}}

To accept the invitation and help {{invitation.from_user}}, please follow the following link:

[{{invitation.get_acceptance_url}}]({{invitation.get_acceptance_url}})

{{invitation.from_user}} will appreciate it!

Thank you,
{% endblock %}
