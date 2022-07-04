from datetime import date

import graphene

from ...blog_management import models
from ..all_user_authorization import AdminAuthorization

class BlogUpdateInput(graphene.InputObjectType):
    blog_cover_image = graphene.String(description="Blog cover image link.",required= True)
    new_title = graphene.String(description="new Title of blog.",required= True)
    old_title = graphene.String(description="old Title of blog.",required= True)
    description = graphene.String(description="Description of blog.",required= True)
    

class BlogUpdate(graphene.Mutation):
    class Arguments:
        input = BlogUpdateInput(
            required=True, description="Fields required to update a blog."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                blog_cover_image = data.get('input')['blog_cover_image']
                new_title = data.get('input')['new_title']
                old_title = data.get('input')['old_title']
                description = data.get('input')['description']
                data=models.Blogs.objects.get(title=old_title)
                data.blog_cover_image = blog_cover_image
                data.title = new_title
                data.description = description
                data.save()
                return BlogUpdate(message=f"{new_title} - Blog updated.")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return BlogUpdate(message=e)


class StatusChangeBlogInput(graphene.InputObjectType):
    title = graphene.String(description="Title of blog.")
    status = graphene.Boolean(description = "blog status")
    
class BlogStatusChange(graphene.Mutation):
    class Arguments:
        input = StatusChangeBlogInput(
            required=True, description="Fields required to change blog status."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']
                status = data.get('input')['status']             
                data=models.Blogs.objects.get(title=title)
                if(status):
                    data.status = status
                    data.save()
                    return BlogStatusChange(message=f"Blog with title - {title} - is now activate.")
                else:
                    data.status = status
                    data.save()
                    return BlogStatusChange(message=f"Blog with title - {title} - is now deactivate.")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return BlogStatusChange(message=e)

class DeleteBlogInput(graphene.InputObjectType):
    title = graphene.String(description="Title of blog.")
    
class DeleteBlog(graphene.Mutation):
    class Arguments:
        input = DeleteBlogInput(
            required=True, description="Fields required to delete a blog."
        )

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']             
                data=models.Blogs.objects.filter(title=title)
                if(len(data)==0):
                    return DeleteBlog(message=f"Blog with title - {title} - is not exists.")
                data.delete()
                return DeleteBlog(message=f"Blog deleted with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return DeleteBlog(message=e)


class BlogCreateInput(graphene.InputObjectType):
    blog_cover_image = graphene.String(description="Blog cover image link.")
    title = graphene.String(description="Title of blog.")
    description = graphene.String(description="Description of blog.")
    

class BlogCreate(graphene.Mutation):
    class Arguments:
        input = BlogCreateInput(
            required=True, description="Fields required to add a blog."
        )
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                blog_cover_image = data.get('input')['blog_cover_image']
                title = data.get('input')['title']
                description = data.get('input')['description']
                data=models.Blogs.objects.filter(title=title)
                if(len(data)>0):
                    return BlogCreate(message=f"Blog with title - {title} - is already exists.") 
                models.Blogs.objects.create(blog_cover_image=blog_cover_image,title=title,description=description)
                return BlogCreate(message=f"Blog created with title - {title}")
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return BlogCreate(message=e)

