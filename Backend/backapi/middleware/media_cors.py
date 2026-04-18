from django.conf import settings


class MediaCORSMiddleware:
    """Set permissive CORS/CORP headers for media file responses.

    This middleware only acts on requests whose path starts with
    `settings.MEDIA_URL` (typically '/media/'). It will echo back the
    Origin when the origin is allowed in `CORS_ALLOWED_ORIGINS`, set
    `Access-Control-Allow-Credentials: true`, and add
    `Cross-Origin-Resource-Policy: cross-origin` so browser ORB blocks are avoided.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            media_url = settings.MEDIA_URL or '/media/'
        except Exception:
            media_url = '/media/'

        if request.path.startswith(media_url):
            origin = request.META.get('HTTP_ORIGIN')
            allowed = getattr(settings, 'CORS_ALLOWED_ORIGINS', []) or []
            if origin and origin in allowed:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
            # Allow cross-origin resource usage for media
            response['Cross-Origin-Resource-Policy'] = 'cross-origin'
        return response
