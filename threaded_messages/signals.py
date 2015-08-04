import django.dispatch

message_composed = django.dispatch.Signal(providing_args=["message", "recipients"])
