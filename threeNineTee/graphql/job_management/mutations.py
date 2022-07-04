from datetime import date

import graphene

from ...job_management import models
from ..all_user_authorization import AdminAuthorization

class JobsApplicatonActionInput(graphene.InputObjectType):
    email = graphene.String(description="Email of job applicant.")
    status = graphene.Boolean(description = "Status of application. Either accept or decline. True or False.")
    
class JobsApplicatonAction(graphene.Mutation):
    class Arguments:
        input = JobsApplicatonActionInput(
            required=True, description="Fields required to Action Job application."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                status = data.get('input')['status']
                try:
                    data=models.JobApplications.objects.get(email=email,status=True)
                except:
                    return JobsApplicatonAction(message=f"Jobs application with email - {email} - is already rejected by admin.")

                if(status):
                    data.is_accept = status
                    data.save()
                    return JobsApplicatonAction(message=f"Jobs application with email - {email} - is now accepted.")
                else:
                    data.is_accept = status
                    data.status = status
                    data.save()
                    return JobsApplicatonAction(message=f"Jobs application with email - {email} - is now rejected.")
                
                    
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return JobsApplicatonAction(message=e)



class JobApplicationCreateInput(graphene.InputObjectType):
    first_name = graphene.String(description="first name of job applicant.")
    last_name = graphene.String(description="last name of job applicant.")
    email = graphene.String(description="email of applicant.")
    phone_number = graphene.String(description="phone number of applicant.")
    resume_link = graphene.String(description="resume link of applicant.")
    company_name = graphene.String(description="company name of applicant.")
    current_ctc = graphene.String(description="Current CTC of applicant.")
    expected_ctc = graphene.String(description="Expected CTC of applicant.")
    notice_period = graphene.String(description="Notice period of applicant.")
    message = graphene.String(description="Message of applicant.")
    job_title = graphene.String(description="Job title.")
    

class JobApplicationCreate(graphene.Mutation):
    class Arguments:
        input = JobApplicationCreateInput(
            required=True, description="Fields required to add a job."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                first_name = data.get('input')['first_name']
                last_name = data.get('input')['last_name']
                email = data.get('input')['email']
                phone_number = data.get('input')['phone_number']
                resume_link = data.get('input')['resume_link']
                company_name = data.get('input')['company_name']
                current_ctc = data.get('input')['current_ctc']
                expected_ctc = data.get('input')['expected_ctc']
                notice_period = data.get('input')['notice_period']
                message = data.get('input')['message']
                job_title = data.get('input')['job_title']
                data=models.JobApplications.objects.filter(email=email)
                if(len(data)>0):
                    return JobApplicationCreate(message=f"Job application with email - {email} - is already exists.") 
                models.JobApplications.objects.create(first_name=first_name,last_name=last_name,email=email,phone_number=phone_number,resume_link=resume_link,company_name=company_name,current_ctc=current_ctc,expected_ctc=expected_ctc,notice_period=notice_period,message=message,job_title=job_title)
                return JobApplicationCreate(message=f"Job application sent to admin with email - {email}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return JobApplicationCreate(message=e)


class JobUpdateInput(graphene.InputObjectType):
    required_experience = graphene.String(description="Job experience.")
    new_title = graphene.String(description="new Title of Job.",required= True)
    old_title = graphene.String(description="old Title of Job.",required= True)
    description = graphene.String(description="Description of Job.",required= True)
    
class JobUpdate(graphene.Mutation):
    class Arguments:
        input = JobUpdateInput(
            required=True, description="Fields required to update a Job."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                required_experience = data.get('input')['required_experience']
                new_title = data.get('input')['new_title']
                old_title = data.get('input')['old_title']
                description = data.get('input')['description']
                data=models.Jobs.objects.get(job_title=old_title)
                data.required_experience = required_experience
                data.job_title = new_title
                data.job_description = description
                data.save()
                return JobUpdate(message=f"{new_title} - Job updated.")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return JobUpdate(message=e)


class StatusChangeJobsInput(graphene.InputObjectType):
    job_title = graphene.String(description="Title of Jobs.")
    status = graphene.Boolean(description = "Jobs status")
    
class JobsStatusChange(graphene.Mutation):
    class Arguments:
        input = StatusChangeJobsInput(
            required=True, description="Fields required to change Jobs status."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                job_title = data.get('input')['job_title']
                status = data.get('input')['status']             
                data=models.Jobs.objects.get(job_title=job_title)
                if(status):
                    data.status = status
                    data.save()
                    return JobsStatusChange(message=f"Jobs with title - {job_title} - is now activate.")
                else:
                    data.status = status
                    data.save()
                    return JobsStatusChange(message=f"Jobs with title - {job_title} - is now deactivate.")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return JobsStatusChange(message=e)

class DeleteJobInput(graphene.InputObjectType):
    title = graphene.String(description="Title of Job.")
    
class DeleteJob(graphene.Mutation):
    class Arguments:
        input = DeleteJobInput(
            required=True, description="Fields required to delete a Job."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']             
                data=models.Jobs.objects.filter(job_title=title)
                if(len(data)==0):
                    return DeleteJob(message=f"Job with title - {title} - is not exists.")
                data.delete()
                return DeleteJob(message=f"Job deleted with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return DeleteJob(message=e)


class JobCreateInput(graphene.InputObjectType):
    required_experience = graphene.String(description="Job experience.")
    job_title = graphene.String(description="Job title.")
    job_description = graphene.String(description="Job description.")
    

class JobCreate(graphene.Mutation):
    class Arguments:
        input = JobCreateInput(
            required=True, description="Fields required to add a job."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                required_experience = data.get('input')['required_experience']
                job_title = data.get('input')['job_title']
                job_description = data.get('input')['job_description']
                data=models.Jobs.objects.filter(job_title=job_title)
                if(len(data)>0):
                    return JobCreate(message=f"Job with title - {job_title} - is already exists.") 
                models.Jobs.objects.create(job_title = job_title, required_experience = required_experience, job_description = job_description)
                return JobCreate(message=f"Job created with title - {job_title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return JobCreate(message=e)

