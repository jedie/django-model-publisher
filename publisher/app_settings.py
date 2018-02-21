from django.conf import settings


# Is used to reverse admin urls:
ADMIN_NAMESPACE = getattr(settings, "ADMIN_NAMESPACE", "admin")
