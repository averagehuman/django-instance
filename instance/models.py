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

class DjangoSiteManager(models.Manager):

    def set_default(self, uid):
        # ensure valid uid
        site = self.get(uid__iexact=uid)
        # there can be only one
        self.get_queryset().exclude(uid__iexact=uid).update(is_default=False)
        if not site.is_default:
            site.is_default = True
            site.save(update_fields=['is_default'])

    def get_default(self):
        try:
            site = self.filter(is_default=True)[0]
        except IndexError:
            try:
                site = self.all()[0]
            except IndexError:
                site = None
            else:
                site.is_default = True
                site.save()
        return site

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
    is_default = models.BooleanField(default=False)
    objects = DjangoSiteManager()

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
            self.uid = slugify(text_type(self.name))
        fqdn = urlparse(self.fqdn)
        if fqdn.scheme == 'https':
            self.is_https = True
        elif fqdn.scheme == 'http':
            self.is_https = False
        self.fqdn = (fqdn.netloc + fqdn.path).strip('./')
        super(DjangoSite, self).save(*args, **kwargs)

