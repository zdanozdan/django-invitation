from django.urls import path, re_path
from django.views.generic import TemplateView

from invitation.views import invite, invited

urlpatterns = [
    path('invite/', invite, name='invitation_invite'),
    re_path(r'^invited/(?P<invitation_key>\w+)/$', invited, name='invitation_invited'),
    path('invite/complete/', TemplateView.as_view(template_name='home.html'), name='invitation_complete'),
]
