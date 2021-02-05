from django.contrib import admin
from .models import OTP, Ticket, Event, Membership, Rewards, Winner

# Register your models here.

admin.site.register(OTP)
admin.site.register(Membership)
admin.site.register(Ticket)
admin.site.register(Event)
admin.site.register(Rewards)
admin.site.register(Winner)


