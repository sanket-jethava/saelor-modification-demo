import graphene
from ...blog_management import models
from ..all_user_authorization import AdminAuthorization,UserAuthorization
from ..core.utils import from_global_id_strict_type

def resolve_blog_detail(info,id):
    if UserAuthorization(info):
        try:
            id = from_global_id_strict_type(id, only_type="Blogs", field="pk")
            all_data = models.Blogs.objects.filter(status = True,id = id)
            return all_data
        except:
            return None

def resolve_blogs_details(info):
    if UserAuthorization(info):
        try:
            all_data = models.Blogs.objects.filter(status = True)
            return all_data
        except:
            return None

def resolve_view_blog_details(info,title):
    if AdminAuthorization(info):
        try:
            all_data = models.Blogs.objects.filter(title=title)
            return all_data
        except:
            return None

def resolve_all_blog_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Blogs.objects.all()
            return all_data
        except:
            return None
