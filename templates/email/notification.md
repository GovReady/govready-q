{% extends "email/template" %}
{% load notification_helpers %}
{% block content %}
{% if not notification.description %}Hello,

{{ notification.actor }} {{ notification.verb }}{% if notification.target %} [{{notification.target}}]({{url}}){% endif %}.
{% else %}{{ notification.actor }} {{ notification.verb }}{% if notification.target %} [{{notification.target}}]({{url}}){% endif %}:

---

{% render_markdown_instead_of_escaping notification.description.strip %}

---
{% endif %}
{% endblock %}

{% block after_signature_note %}{% if whatreplydoes %}{{whatreplydoes}}{% endif %}{% endblock %}
