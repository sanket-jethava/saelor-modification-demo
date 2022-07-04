from graphene import Boolean, relay

from ...marketing import models
from graphene_django import DjangoObjectType

class PromotionBanner(DjangoObjectType):
    class Meta:
        model = models.Promotion_Banner
        fields = ('banner_image','title','from_date','to_date','status')


class Banner(DjangoObjectType):
    class Meta:
        model = models.Banner
        fields = ('banner_image','title','sub_title','description','status')