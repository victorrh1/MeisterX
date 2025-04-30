from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog

class AuditLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.audit_log_data = {
            'ip': self.get_client_ip(request)
        }
    
    def process_response(self, request, response):
        if hasattr(request, 'user') and hasattr(request, '_audit_log'):
            AuditLog.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                acao=request._audit_log.get('acao'),
                descricao=request._audit_log.get('descricao', ''),
                ip=request.audit_log_data.get('ip')
            )
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 