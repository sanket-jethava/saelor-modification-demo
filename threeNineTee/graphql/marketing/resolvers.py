import graphene
from ...marketing import models
from ..all_user_authorization import AdminAuthorization


def resolve_all_promotion_banner_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Promotion_Banner.objects.all()
            return all_data
        except:
            return None

def resolve_all_banner_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Banner.objects.all()
            return all_data
        except:
            return None
