import os
import random
import datetime
from django.db import models
from django.conf import settings
from django.utils.http import int_to_base36
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User,Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from registration.models import SHA1_RE

class InvitationManager(models.Manager):
    def get_key(self, invitation_key):
        """
        Return InvitationKey, or None if it doesn't (or shouldn't) exist.
        """
        try:
            key = self.get(key=invitation_key)
        except self.model.DoesNotExist:
            return None
        
        return key
        
    def is_key_valid(self, invitation_key):
        """
        Check if an ``InvitationKey`` is valid or not, returning a boolean,
        ``True`` if the key is valid.
        """
        invitation_key = self.get_key(invitation_key)
        return invitation_key and not invitation_key.key_expired()

    def create_key(self,user):
        """
        The key for the ``Invitation`` will be a SHA1 hash, generated 
        from a combination of the ``User``'s username and a random salt.
        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        key = sha_constructor("%s%s%s" % (datetime.datetime.now(), salt, user.username)).hexdigest()

        return key

    def create_invitation(self, user, receiver):
        """
        Create an ``Invitation`` and returns it.
        """
        key = self.key(user)

        if isinstance(receiver,User) == False:
            return Invitation(sender=user,receiver_email=receiver,key=key)
    
        return Invitation(sender=user,receiver=receiver,key=key)

    def delete_expired_keys(self):
        for key in self.all():
            if key.key_expired():
                key.delete()


class Invitation(models.Model):
    key = models.CharField(_('invitation key'), max_length=40)
    date_invited = models.DateTimeField(_('date invited'),auto_now_add=True)
    sender = models.ForeignKey(User, related_name='invitations_sent')
    receiver = models.ForeignKey(User, null=True, blank=True, related_name='invitations_used')
    receiver_email = models.EmailField(_("Email"),null=True, blank=True)
    
    objects = InvitationManager()

    def __unicode__(self):
        return u"Invitation from %s on %s" % (self.sender.username, self.date_invited)

    def get_receiver_email(self):
        return self.receiver.email if self.receiver else self.receiver_email
    
    def key_expired(self):
        """
        Determine whether this ``InvitationKey`` has expired, returning 
        a boolean -- ``True`` if the key has expired.
        
        The date the key has been created is incremented by the number of days 
        specified in the setting ``ACCOUNT_INVITATION_DAYS`` (which should be 
        the number of days after invite during which a user is allowed to
        create their account); if the result is less than or equal to the 
        current date, the key has expired and this method returns ``True``.
        
        """
        #expiration_date = datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS)
        #expiration_date = datetime.timedelta(days=30)
        #return self.date_invited + expiration_date <= datetime.datetime.now()
        return False
    key_expired.boolean = True
    
    def mark_used(self, registrant):
        """
        Note that this key has been used to register a new user.
        """
        self.registrant = registrant
        self.save()

    def render_templates(self,kwargs={}):
        current_site = Site.objects.get_current()

        z = kwargs.copy()
        z.update({'site': current_site, 'invitation':self})
        
        subject = render_to_string('invitation/invitation_email_subject.txt', z)

        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('invitation/invitation_email.txt', z)

        return (subject,message)
        
    def send_mail(self, kwargs={}):
        """
        Send an invitation email to ``self.receiver``.
        """
        subject,message = self.render_templates(kwargs)
        
        send_mail(subject, message, self.sender.email, [self.get_receiver_email(),])
