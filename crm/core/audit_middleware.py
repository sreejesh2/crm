import json
from django.utils import timezone
from .models import AuditLogs

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request and get response
        response = self.get_response(request)

        # Only log authenticated requests
        if request.user.is_authenticated:
            # Create audit log entry
            AuditLogs.objects.create(
                request_time=timezone.now(),
                resource=request.path,
                action=request.method,
                user=request.user.full_name,
                body=json.dumps(request.body.decode('utf-8')) if request.body else ''
            )

        return response
