from ...job_management import models
from ..all_user_authorization import AdminAuthorization, UserAuthorization
from ..core.utils import from_global_id_strict_type

def resolve_job_detail(info,id):
    if UserAuthorization(info):
        try:
            id = from_global_id_strict_type(id, only_type="Jobs", field="pk")
            all_data = models.Jobs.objects.filter(status = True,id = id )
            return all_data
        except:
            return None

def resolve_jobs_details(info):
    if UserAuthorization(info):
        try:
            all_data = models.Jobs.objects.filter(status=True)
            return all_data
        except:
            return None


def resolve_job_application_details(info,email):
    if AdminAuthorization(info):
        try:
            all_data = models.JobApplications.objects.get(email=email,status=True)
            return all_data
        except:
            return None
def resolve_all_job_application_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.JobApplications.objects.all(status=True)
            return all_data
        except:
            return None

def resolve_view_job_details(info,title):
    if AdminAuthorization(info):
        try:
            all_data = models.Jobs.objects.filter(job_title=title)
            return all_data
        except:
            return None

def resolve_all_job_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Jobs.objects.all()
            return all_data
        except:
            return None
