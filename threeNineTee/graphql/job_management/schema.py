import graphene

from .mutations import JobCreate, JobsStatusChange, DeleteJob, JobUpdate, JobApplicationCreate, JobsApplicatonAction
from .resolvers import resolve_view_job_details, resolve_all_job_details, resolve_all_job_application_details, resolve_job_application_details,resolve_jobs_details,resolve_job_detail
from .types import Jobs, JobApplications

class JobManagementQueries(graphene.ObjectType):
    job_application_details = graphene.Field(
        JobApplications,
        email = graphene.Argument(graphene.String, required=True),
        description="Fetch all job applications details"
    )

    def resolve_job_application_details(self, info,email):
        return resolve_job_application_details(info,email)
    
    all_job_application_details = graphene.List(
        JobApplications,
        description="Fetch all job applications details"
    )

    def resolve_all_job_application_details(self, info):
        return resolve_all_job_application_details(info)


    view_job_details = graphene.List(
        Jobs,
        title = graphene.Argument(graphene.String, description="job title for filter and fetch data of job.", required=True),
        description="Fetch job details"
    )

    def resolve_view_job_details(self, info,title):
        return resolve_view_job_details(info,title)
    
    all_job_details = graphene.List(
        Jobs,
        description="Fetch all job details"
    )

    def resolve_all_job_details(self, info):
        return resolve_all_job_details(info)
    
    jobs_details = graphene.List(
        Jobs,
        description="Fetch all job details"
    )

    def resolve_jobs_details(self, info):
        return resolve_jobs_details(info)

    job_detail = graphene.List(
        Jobs,
        description="Fetch all job details",
        job_id = graphene.Argument(graphene.ID, description="job ID for filter and fetch data of job.", required=True),
    )

    def resolve_job_detail(self, info,job_id):
        return resolve_job_detail(info,job_id)
    

class JobManagementMutations(graphene.ObjectType):
    Job_Create = JobCreate.Field()
    Jobs_Status_Change = JobsStatusChange.Field()
    Delete_Job = DeleteJob.Field()
    Job_Update = JobUpdate.Field()
    Job_Application_Create = JobApplicationCreate.Field()
    Job_Applicaton_Action = JobsApplicatonAction.Field()