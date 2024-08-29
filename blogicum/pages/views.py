from django.shortcuts import render


def rules(request):
    """Rules page view"""
    template_name = 'pages/rules.html'
    return render(request, template_name)


def about(request):
    """About page view"""
    template_name = 'pages/about.html'
    return render(request, template_name)
