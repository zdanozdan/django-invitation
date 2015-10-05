from django.conf.urls import patterns, include, url
from invitation.views import invite, invited
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^invite/$', invite,name='invitation_invite'),
    url(r'^invited/(?P<invitation_key>\w+)/$',invited, name='invitation_invited'),
    url(r'^invite/complete/$',TemplateView.as_view(template_name='home.html'), name='invitation_complete'),
)
