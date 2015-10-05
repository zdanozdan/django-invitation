from django.contrib import admin
from invitation.models import Invitation

class InvitationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'sender', 'receiver', 'receiver_email','date_invited', 'key_expired')

admin.site.register(Invitation, InvitationAdmin)

