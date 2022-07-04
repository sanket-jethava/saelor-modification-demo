import graphene

from .mutations import BlogCreate,BlogStatusChange,DeleteBlog, BlogUpdate
from .resolvers import resolve_all_blog_details, resolve_view_blog_details
from .types import Blogs


class BlogManagementQueries(graphene.ObjectType):
    view_blog_details = graphene.List(
        Blogs,
        title = graphene.Argument(graphene.String, description="Blog title for filter and fetch data of blog.", required=True),
        description="Fetch blog details"
    )

    def resolve_view_blog_details(self, info,title):
        return resolve_view_blog_details(info,title)
    
    all_blog_details = graphene.List(
        Blogs,
        description="Fetch all blog details"
    )

    def resolve_all_blog_details(self, info):
        return resolve_all_blog_details(info)
    

class BlogManagementMutations(graphene.ObjectType):
    Blog_Create = BlogCreate.Field()
    Blog_Status_Change = BlogStatusChange.Field()
    Delete_Blog = DeleteBlog.Field()
    Blog_Update = BlogUpdate.Field()  
  