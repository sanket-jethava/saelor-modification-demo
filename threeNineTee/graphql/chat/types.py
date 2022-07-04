from graphene import Boolean, relay

from ...blog_management import models
from graphene_django import DjangoObjectType

class Blogs(DjangoObjectType):
    class Meta:
        model = models.Blogs
        fields = ('blog_cover_image','title','description','status','post_date')