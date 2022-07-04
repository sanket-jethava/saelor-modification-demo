import graphene
from ...blog_management import models
from ..all_user_authorization import AdminAuthorization

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
