from django.db import models

# Create your models here.
class Banner(models.Model):
    banner_image = models.TextField(blank=False,null=True)
    title = models.TextField(blank=False,null=True,unique=True)
    sub_title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=False)

class Promotion_Banner(models.Model):
    banner_image = models.TextField(blank=False,null=True)
    title = models.TextField(blank=False,null=True,unique=True)
    from_date = models.DateField(blank=False)
    to_date = models.DateField(blank=False)
    status = models.BooleanField(default=False)