{% extends "email/template" %}
{% block content %}
Hello,

{{ notification.actor }} {{ notification.verb }}{% if notification.target %} [{{notification.target}}]({{url}}){% endif %}.
{% if notification.description %}
~~~~
{{notification.description.strip}}
~~~~
{% endif %}
Go to [{{notification.target}}]({{url}})

Good luck!{% endblock %}

{% block after_signature_note %}{% if whatreplydoes %}{{whatreplydoes}}{% endif %}{% endblock %}
