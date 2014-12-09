# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import string

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.text import slugify

from logbook import Logger

from .conf import settings
from .utils import urlparse, pathjoin, text_type

log = Logger(__name__)

# copied from django.contrib.sites
def _simple_domain_name_validator(value):
    """
    Validates that the given value contains no whitespaces to prevent common
    typos.
    """
    if not value:
        return
    checks = ((s in value) for s in string.whitespace)
    if any(checks):
        raise ValidationError(
            _("The domain name cannot contain any spaces or tabs."),
            code='invalid',
        )

@python_2_unicode_compatible
class DjangoSite(models.Model):

    name = models.CharField(max_length=120)
    uid = models.SlugField(blank=False, unique=True, db_index=True)
    fqdn = models.CharField(
        _('domain name'), max_length=100, default='127.0.0.1:8000',
        validators=[_simple_domain_name_validator]
    )
    is_https = models.BooleanField(default=False)
    title = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=250, blank=True)
    info = models.TextField(blank=True)
    settings_module = models.CharField(
        max_length=100, default="instance.settings"
    )

    class Meta:
        db_table = 'django_site'
        verbose_name = _('Django Site')
        verbose_name_plural = _('Django Sites')
        ordering = ('name',)

    def __str__(self):
        return self.uid

    @property
    def netloc(self):
        # fqdn without port number
        parsed = urlparse(self.fqdn)
        return (parsed.netloc + parsed.path).strip('/').partition(':')[0]

    @property
    def url(self):
        scheme = 'http'
        if self.is_https:
            scheme += 's'
        return '%s://%s' % (scheme, self.fqdn)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'uid') or not self.uid:
            uid = slugify(text_type(self.name))
#            suffix = ''
#            i = 0
#            while True:
#                key = uid+suffix
#                try:
#                    DjangoSite.objects.get(uid__iexact=key)
#                except DjangoSite.DoesNotExist:
#                    break
#                i += 1
#                suffix = '-%s' % i
#            self.uid = key
            self.uid = uid
        fqdn = urlparse(self.fqdn)
        if fqdn.scheme == 'https':
            self.is_https = True
        elif fqdn.scheme == 'http':
            self.is_https = False
        self.fqdn = (fqdn.netloc + fqdn.path).strip('./')
        super(DjangoSite, self).save(*args, **kwargs)

