from django import forms
from django.contrib.auth.models import User,Group
from django.core.validators import EmailValidator
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from invitation.models import Invitation

class UserOrEmailField(forms.EmailField):

    def clean(self, value):
        value = self.to_python(value).strip()
        try:
            return User.objects.get(Q(username=value) | Q(email=value))
        except:
            pass

        return super(UserOrEmailField, self).clean(value)

class InvitationForm(forms.ModelForm):
    invited = UserOrEmailField(error_messages={'invalid':_('User does not exists or this email address is invalid')},label=_("Invite now"))

    def get_invited(self):
        return self.cleaned_data['invited']

    def get_email(self):
        u = self.get_invited()
        return u.email if isinstance(u,User) else u

    def set_receiver(self):
        u = self.get_invited()

        if isinstance(u,User):
            self.instance.receiver = u
        else:
           self.instance.receiver_email = u

    class Meta:
        model = Invitation
        fields = ['invited',]
