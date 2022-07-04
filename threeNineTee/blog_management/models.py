from django.db import models
from django.utils import timezone

# Create your models here.
class Blogs(models.Model):
    blog_cover_image = models.TextField(blank=False,null=True)
    title = models.TextField(blank=False,null=True,unique=True)
    description = models.TextField(blank=True)
    post_date = models.DateTimeField(default=timezone.now,editable=False,blank=True,null=True)
    status = models.BooleanField(default=True)