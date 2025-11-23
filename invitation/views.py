from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from invitation.forms import InvitationForm

#from registration.views import register as registration_register
from invitation.models import Invitation


@login_required
def invited(request, invitation_key=None):
    if Invitation.objects.is_key_valid(invitation_key):
        template_name = 'invitation/invited.html'
    else:
        template_name = 'invitation/wrong_invitation_key.html'

    return render(request, template_name, {})

@login_required
def invite(request):
    form = InvitationForm()
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invited = form.get_invited()
            invitation = Invitation.objects.create_invitation(user=request.user, receiver=invited)
            invitation.save()
            invitation.send_mail('invitation', {})
            return HttpResponseRedirect(request.GET.get('next') or reverse('invitation_complete'))

    return render(request, 'invitation/invitation_form.html', {
        'form' : form,
    })
