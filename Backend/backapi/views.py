from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def health_check(request):
    """Container health endpoint used by Docker healthchecks."""
    try:
        connections["default"].cursor()
    except OperationalError:
        return JsonResponse({"status": "unhealthy", "database": "down"}, status=503)

    return JsonResponse({"status": "ok", "database": "up"}, status=200)
