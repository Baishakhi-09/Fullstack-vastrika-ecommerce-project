import threading

_audit_local = threading.local()

def set_current_user(user):
    _audit_local.user = user

def get_current_user():
    return getattr(_audit_local, "user", None)

class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        set_current_user(user)

        try:
            return self.get_response(request)
        finally:
            set_current_user(None)