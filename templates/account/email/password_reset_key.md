{% extends "email/template" %}
{% load account %}
{% block content %}
Hello,

You or someone else has requested a password for your user account at GovReady Q.

Click the link below to reset your password:

[{{password_reset_url}}]({{password_reset_url}})

{% if username %}Your username is {{ username }}.
{% endif %}
You can safely ignore this email if you did not request a password reset.{% endblock %}
