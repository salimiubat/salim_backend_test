from django.db import models

# Create your models here.
class StripePayment(models.Model):
    api_key=models.CharField(max_length=1000)
    def save(self, *args, **kwargs):
        if not self.pk and StripePayment.objects.exists():
            return
        super().save(*args, **kwargs)