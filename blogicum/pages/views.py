from django.views.generic import TemplateView


class RulesView(TemplateView):
    """Generate page with project rules"""

    template_name = 'pages/rules.html'


class AboutView(TemplateView):
    """Generate page with info about us"""

    template_name = 'pages/about.html'
