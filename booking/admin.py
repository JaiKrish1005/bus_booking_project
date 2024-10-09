from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Bus, Booking

admin.site.register(User, UserAdmin)
admin.site.register(Bus)
admin.site.register(Booking)