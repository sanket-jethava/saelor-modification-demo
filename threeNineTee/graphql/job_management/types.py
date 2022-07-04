from graphene import Boolean, relay

from ...job_management import models
from graphene_django import DjangoObjectType

class JobApplications(DjangoObjectType):
    class Meta:
        model = models.JobApplications
        fields = ('first_name','last_name','email','phone_number','resume_link','company_name','current_ctc','expected_ctc','notice_period','message','status','job_title')

class Jobs(DjangoObjectType):
    class Meta:
        model = models.Jobs
        fields = ('id','job_title','job_description','required_experience','status','post_date')
        interfaces = (relay.Node,)