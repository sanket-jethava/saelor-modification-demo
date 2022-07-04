from datetime import date

import graphene

from ...marketing import models
from ..all_user_authorization import AdminAuthorization

class StatusChangePromotionBannerInput(graphene.InputObjectType):
    title = graphene.String(description="Title of promotion banner.")
    status = graphene.Boolean(description = "Promotion banner status")
    
class PromotionBannerStatusChange(graphene.Mutation):
    class Arguments:
        input = StatusChangePromotionBannerInput(
            required=True, description="Fields required to delete a banner."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']
                status = data.get('input')['status']             
                data=models.Promotion_Banner.objects.get(title=title)
                if(status):
                    data.status = status
                    data.save()
                    return PromotionBannerStatusChange(message=f"Promotion Banner with title - {title} - is now activate.")
                else:
                    data.status = status
                    data.save()
                    return PromotionBannerStatusChange(message=f"Promotion Banner with title - {title} - is now deactivate.")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return PromotionBannerStatusChange(message=e)

class DeletePromotionBannerInput(graphene.InputObjectType):
    title = graphene.String(description="Title of promotion banner.")
    
class DeletePromotionBanner(graphene.Mutation):
    class Arguments:
        input = DeletePromotionBannerInput(
            required=True, description="Fields required to delete a promotion banner."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']             
                data=models.Promotion_Banner.objects.filter(title=title)
                if(len(data)==0):
                    return DeletePromotionBanner(message=f"Promotion Banner with title - {title} - is not exists.")
                data.delete()
                return DeletePromotionBanner(message=f"Promotion Banner deleted with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return DeletePromotionBanner(message=e)


class PromotionBannerInput(graphene.InputObjectType):
    banner_image = graphene.String(description="promotion Banner image link.")
    title = graphene.String(description="Title of promotion banner.")
    from_date = graphene.String(description="From date.")
    to_date = graphene.String(description="To date.")

class PromotionBannerCreate(graphene.Mutation):
    class Arguments:
        input = PromotionBannerInput(
            required=True, description="Fields required to add a promotion banner."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                banner_image = data.get('input')['banner_image']
                title = data.get('input')['title']
                from_date = data.get('input')['from_date']
                to_date = data.get('input')['to_date']
                from datetime import datetime
                from_date = datetime.strptime(from_date, '%Y-%m-%d')
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
                data=models.Promotion_Banner.objects.filter(title=title)
                if(len(data)>0):
                    return PromotionBannerCreate(message=f"Promotion Banner with title - {title} - is already exists.") 
                models.Promotion_Banner.objects.create(banner_image=banner_image,title=title,from_date=from_date,to_date=to_date)
                return PromotionBannerCreate(message=f"Promotion Banner created with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return PromotionBannerCreate(message=e)


class StatusChangeBannerInput(graphene.InputObjectType):
    title = graphene.String(description="Title of banner.")
    status = graphene.Boolean(description = " banner status")
    
class BannerStatusChange(graphene.Mutation):
    class Arguments:
        input = StatusChangeBannerInput(
            required=True, description="Fields required to delete a banner."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']
                status = data.get('input')['status']             
                data=models.Banner.objects.get(title=title)
                if(status):
                    data.status = status
                    data.save()
                    return BannerStatusChange(message=f"Banner with title - {title} - is now activate.")
                else:
                    data.status = status
                    data.save()
                    return BannerStatusChange(message=f"Banner with title - {title} - is now deactivate.")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return BannerStatusChange(message=e)

class DeleteBannerInput(graphene.InputObjectType):
    title = graphene.String(description="Title of banner.")
    
class DeleteBanner(graphene.Mutation):
    class Arguments:
        input = DeleteBannerInput(
            required=True, description="Fields required to delete a banner."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']             
                data=models.Banner.objects.filter(title=title)
                if(len(data)==0):
                    return DeleteBanner(message=f"Banner with title - {title} - is not exists.")
                data.delete()
                return DeleteBanner(message=f"Banner deleted with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return DeleteBanner(message=e)
        
    
class BannerInput(graphene.InputObjectType):
    banner_image = graphene.String(description="Banner image link.")
    title = graphene.String(description="Title of banner.")
    sub_title = graphene.String(description="Sub title of banner.")
    description = graphene.String(description="Description of banner.")

class BannerCreate(graphene.Mutation):
    class Arguments:
        input = BannerInput(
            required=True, description="Fields required to add a banner."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                banner_image = data.get('input')['banner_image']
                title = data.get('input')['title']
                sub_title = data.get('input')['sub_title']
                description = data.get('input')['description']
                data=models.Banner.objects.filter(title=title)
                if(len(data)>0):
                    return BannerCreate(message=f"Banner with title - {title} - is already exists.")
                models.Banner.objects.create(banner_image=banner_image,title=title,sub_title=sub_title,description=description)
                return BannerCreate(message=f"Banner created with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return BannerCreate(message=e)
        
    