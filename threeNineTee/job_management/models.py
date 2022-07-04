from django.db import models
import datetime

# Create your models here.
class Jobs(models.Model):
    job_title = models.TextField(blank=False,null=True,unique=True)
    required_experience = models.TextField(blank=True)
    job_description = models.TextField(blank=True)
    post_date = models.DateField(blank=False,default=datetime.date.today)
    status = models.BooleanField(default=True)

class JobApplications(models.Model):
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    email = models.TextField(blank=False,null=True,unique=True)
    phone_number = models.TextField(blank=False)
    resume_link = models.TextField(blank=False)
    company_name = models.TextField(blank=True,null=True)
    current_ctc = models.TextField(blank=True,null=True)
    expected_ctc = models.TextField(blank=True,null=True)
    notice_period = models.TextField(blank=True,null=True)
    message = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=True)
    job_title = models.TextField(blank=False,null=True)
    is_accept = models.BooleanField(default=False)