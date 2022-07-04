import graphene

from .mutations import BannerCreate, DeleteBanner, BannerStatusChange, PromotionBannerCreate,DeletePromotionBanner,PromotionBannerStatusChange
from .resolvers import resolve_all_banner_details, resolve_all_promotion_banner_details
from .types import Banner, PromotionBanner


class MarketingQueries(graphene.ObjectType):
    all_promotion_banner_details = graphene.List(
        PromotionBanner,
        description="Fetch all banner details"
    )

    def resolve_all_promotion_banner_details(self, info):
        return resolve_all_promotion_banner_details(info)

    all_banner_details = graphene.List(
        Banner,
        description="Fetch all banner details"
    )

    def resolve_all_banner_details(self, info):
        return resolve_all_banner_details(info)

class MarketingMutations(graphene.ObjectType):
    Banner_Create = BannerCreate.Field()
    Delete_Banner = DeleteBanner.Field()
    Change_Banner_Status = BannerStatusChange.Field()
    Promotion_Banner_Create = PromotionBannerCreate.Field()
    Delete_Promotion_Banner = DeletePromotionBanner.Field()
    Promotion_Banner_Status_Change = PromotionBannerStatusChange.Field()