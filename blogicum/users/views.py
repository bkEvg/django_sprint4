from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model

from .forms import UserRegistration

User = get_user_model()


class Registration(CreateView):
    """Register for User view"""

    model = User
    form_class = UserRegistration
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
