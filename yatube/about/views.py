# from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.


class AboutAuthorView(TemplateView):
    template_name = 'about_template/author.html'


class AboutTechView(TemplateView):
    template_name = 'about_template/tech.html'
