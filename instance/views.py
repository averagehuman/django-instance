
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

def testpage(request, **kwargs):
    """Test Page"""
    context = {
        'DEBUG': 'True' if settings.DEBUG else 'False',
    }
    template = kwargs.get('template', 'instance/testpage.html')
    return render(request, template, context)

