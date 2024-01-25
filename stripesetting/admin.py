from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(StripePayment)
class StripePaymentAdmin(admin.ModelAdmin):
    list_display = ['api_key']