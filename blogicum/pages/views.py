from django.views.generic import TemplateView
from django.shortcuts import render


class RulesView(TemplateView):
    """Generate page with project rules"""

    template_name = 'pages/rules.html'


class AboutView(TemplateView):
    """Generate page with info about us"""

    template_name = 'pages/about.html'


def handle_404page(request, exception):
    template_name = "pages/404.html"
    return render(request, template_name, status=404)


def handle_403page(request, exception):
    template_name = "pages/403csrf.html"
    return render(request, template_name, status=403)


def handle_500page(request):
    template_name = "pages/500.html"
    return render(request, template_name, status=500)
