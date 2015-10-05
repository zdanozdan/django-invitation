from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

#from registration.views import register as registration_register

from invitation.models import Invitation
from invitation.forms import InvitationForm

@login_required
def invited(request, invitation_key=None):
    if Invitation.objects.is_key_valid(invitation_key):
        template_name = 'invitation/invited.html'
    else:
        template_name = 'invitation/wrong_invitation_key.html'

    return render_to_response(template_name, {}, context_instance=RequestContext(request))

@login_required
def invite(request):
    form = InvitationForm
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = Invitation.objects.create_invitation(user=request.user,receiver=form.get_invited())
            invitation.save()
            invitation.send_to(form.get_email())
            return HttpResponseRedirect(request.GET.get('next') or reverse('invitation_complete'))

    return render_to_response('invitation/invitation_form.html', {
        'form' : form,
    },context_instance=RequestContext(request))
