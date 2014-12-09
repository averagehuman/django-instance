
import sys
from django.conf import settings
from django.conf.urls import *

_slash = "/" if settings.APPEND_SLASH else ""
_siteid = getattr(settings, "SITE_UID", "default")

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
    url(r'^assets/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),
)

if settings.DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls))
        )

urlpatterns += patterns("instance.views",
    url(
        "^$",
        "testpage",
        name="instance-testpage",
    ),
)
