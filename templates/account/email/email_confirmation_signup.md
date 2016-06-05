{% extends "email/template" %}
{% load account %}
{% block content %}
{% user_display user as user_display %}
Hello,

Please confirm your email address at GovReady Q by following this link:

[{{activate_url}}]({{activate_url}})

This message was sent by user {{ user_display }}. If this wasn't you, please ignore this email.{% endblock %}
