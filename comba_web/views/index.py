__author__ = 'michel'
from django.shortcuts import render_to_response, render as render_template
from django.template import RequestContext


def home(request):
   return render_template(request, 'index.html')
