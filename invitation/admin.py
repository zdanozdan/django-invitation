from django.contrib import admin
from .models import Invitation

class InvitationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'sender', 'receiver', 'receiver_email','date_invited', 'key_expired')

admin.site.register(Invitation, InvitationAdmin)

