import graphene
import jwt
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError

from ....account import emails, events as account_events, models, utils
from ....account.error_codes import AccountErrorCode
from ....checkout import AddressType
from ....core.jwt import create_token, jwt_decode
from ....core.utils.url import validate_storefront_url
from ....settings import JWT_TTL_REQUEST_EMAIL_CHANGE
from ...account.enums import AddressTypeEnum
from ...account.types import Address, AddressInput, User
from ...core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from ...core.types.common import AccountError
from ...meta.deprecated.mutations import UpdateMetaBaseMutation
from ...meta.deprecated.types import MetaInput
from ..i18n import I18nMixin
from .base import (
    INVALID_TOKEN,
    BaseAddressDelete,
    BaseAddressUpdate,
    BaseCustomerCreate,
)
from ...all_user_authorization import AdminAuthorization, ArtistAuthorization,B2BUserAuthorization
from ....checkout.models import Checkout
from ...core.utils import from_global_id_strict_type

class ArtistStatusChangeInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    status = graphene.Boolean(required=True)

class ArtistStatusChange(graphene.Mutation):
    class Arguments:
        input = ArtistStatusChangeInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                status = data.get('input')['status']
                try:
                    user = models.User.objects.get(email=email,is_artist=True)
                except:
                    return ArtistStatusChange(message="User not found with email - "+email+" as a B2B user.")
                if status:
                    user.is_active = status
                    user.save()
                    message = f"Artist User - {email} is activated successfully."
                    return ArtistStatusChange(message=message)
                else:
                    user.is_active = status
                    user.save()
                    message = f"Artist User - {email} is deactivated successfully."
                    return ArtistStatusChange(message=message)
            else:
                raise Exception("Only admin have right to perform this task")
        except Exception as e:
            return ArtistStatusChange(message=e)


class B2BUserStatusChangeInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    status = graphene.Boolean(required=True)

class B2BUserStatusChange(graphene.Mutation):
    class Arguments:
        input = B2BUserStatusChangeInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                status = data.get('input')['status']
                try:
                    user = models.User.objects.get(email=email,is_b2buser=True)
                except:
                    return B2BUserStatusChange(message="User not found with email - "+email+" as a B2B user.")
                if status:
                    user.is_active = status
                    user.save()
                    message = f"B2B User - {email} is activated successfully."
                    return B2BUserStatusChange(message=message)
                else:
                    user.is_active = status
                    user.save()
                    message = f"B2B User - {email} is deactivated successfully."
                    return B2BUserStatusChange(message=message)
            else:
                raise Exception("Only admin have right to perform this task")
        except Exception as e:
            return B2BUserStatusChange(message=e)


class B2CUserStatusChangeInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    status = graphene.Boolean(required=True)

class B2CUserStatusChange(graphene.Mutation):
    class Arguments:
        input = B2CUserStatusChangeInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                status = data.get('input')['status']
                user = models.User.objects.get(email=email)
                if status:
                    user.is_active = status
                    user.save()
                    message = f"B2C User - {email} is activated successfully."
                    return B2CUserStatusChange(message=message)
                else:
                    user.is_active = status
                    user.save()
                    message = f"B2C User - {email} is deactivated successfully."
                    return B2CUserStatusChange(message=message)
            else:
                raise Exception("Only admin have right to perform this task")
        except Exception as e:
            return B2CUserStatusChange(message=e)

class StaffUserStatusChangeInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    status = graphene.Boolean(required=True)

class StaffUserStatusChange(graphene.Mutation):
    class Arguments:
        input = StaffUserStatusChangeInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                status = data.get('input')['status']
                user = models.User.objects.get(email=email,is_staff=True)
                if status:
                    user.is_active = status
                    user.save()
                    message = f"Staff - {email} is activated successfully."
                    return StaffUserStatusChange(message=message)
                else:
                    user.is_active = status
                    user.save()
                    message = f"Staff - {email} is deactivated successfully."
                    return StaffUserStatusChange(message=message)
            else:
                raise Exception("Only admin have right to perform this task")
        except Exception as e:
            return StaffUserStatusChange(message=e)

class StaffUserDeleteInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    

class StaffUserDelete(graphene.Mutation):
    class Arguments:
        input = StaffUserDeleteInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                user = models.User.objects.get(email=email,is_staff=True)
                
                models.CustomerEvent.objects.filter(user_id=user.id).delete()
                try:
                    models.LoginSummary.objects.filter(user_id=user.id).delete()
                except:
                    pass

                user.delete()
                message = f"Staff - {email} is deleted successfully."
                return StaffUserDelete(message=message)
            else:
                raise Exception("Only admin have right to perform this task")
        except Exception as e:
            return StaffUserDelete(message=e)

class StaffUserUpdateInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    avatar = graphene.String(required=False)
    address = graphene.String(required=False)

class StaffUserUpdate(graphene.Mutation):
    class Arguments:
        input = StaffUserUpdateInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                try:
                    email = data.get('input')['email']            
                    first_name = data.get('input')['first_name']
                    last_name = data.get('input')['last_name']
                    avatar = data.get('input')['avatar']
                    address = data.get('input')['address']
                    user = models.User.objects.get(email=email,is_staff=True)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.avatar = avatar
                    address = models.Address.objects.get_or_create(first_name=first_name, last_name=last_name,street_address_1 = address,phone = user.phonenumber)
                    if type(address)==tuple:
                        address = models.Address.objects.filter(first_name=first_name, last_name=last_name,phone = user.phonenumber).first()
                    user.default_shipping_address_id = address.id
                    user.save()
                    address.save()
                    message = "Profile updated successfully."
                except Exception as e:
                    message = e
                return StaffUserUpdate(message=message)
            else:
                raise Exception("Only admin have right to perform this task")
        except Exception as e:
            return StaffUserUpdate(message=e)


class artistProfileSetupInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    profile_picture = graphene.String(required=False)
    dribble_link = graphene.String(required=False)
    behance_link = graphene.String(required=False)
    facebook_link = graphene.String(required=False)
    twitter_link = graphene.String(required=False)
    instagram_link = graphene.String(required=False)
    bio = graphene.String(required=False)
    upi_id = graphene.String(required=False)

class artistProfileSetup(graphene.Mutation):
    class Arguments:
        input = artistProfileSetupInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if ArtistAuthorization(info):
                email = data.get('input')['email']
                profile_picture = data.get('input')['profile_picture']
                dribble_link = data.get('input')['dribble_link']
                behance_link = data.get('input')['behance_link']
                facebook_link = data.get('input')['facebook_link']
                twitter_link = data.get('input')['twitter_link']
                instagram_link = data.get('input')['instagram_link']
                bio = data.get('input')['bio']
                upi_id = data.get('input')['upi_id']

                user = models.User.objects.get(email=email,is_artist=True)
                sml = models.SocialMediaLinks.objects.filter(user_id=user.id)
                if len(sml)>0:
                    data = models.SocialMediaLinks.objects.get(user_id=user.id)
                    data.dribble_link = dribble_link
                    data.behance_link = behance_link
                    data.facebook_link = facebook_link
                    data.twitter_link = twitter_link
                    data.instagram_link = instagram_link
                    data.save()
                else:
                    social_media = models.SocialMediaLinks.objects.create(dribble_link=dribble_link,behance_link=behance_link,facebook_link=facebook_link,twitter_link=twitter_link,instagram_link=instagram_link,user_id = user.id)
                    user.social_media_id = social_media.id
                user.bio = bio
                user.avatar = profile_picture
                user.upi_id = upi_id
                user.save()
                message = "Profile updated successfully."
                return artistProfileSetup(message=message)

        except Exception as e:
            return deleteArtistUser(message=e)

class deletePackageInput(graphene.InputObjectType):
    product_title = graphene.String(required=True)
    
class deletePackage(graphene.Mutation):
    class Arguments:
        input = deletePackageInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                product_title = data.get('input')['product_title']
                               
                data = models.Package.objects.filter(title=product_title).delete()
                if(data[0]>0):
                    message = f"Package - {product_title} is deleted successfully."
                else:
                    message = f"Package - {product_title} is not exists. Please check package name."
                return deletePackage(message=message)
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return deletePackage(message=e)

class deleteArtistInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    
class deleteArtistUser(graphene.Mutation):
    class Arguments:
        input = deleteArtistInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                user = models.User.objects.get(email=email,is_artist=True)
                
                models.CustomerEvent.objects.filter(user_id=user.id).delete()
                try:
                    models.LoginSummary.objects.filter(user_id=user.id).delete()
                except:
                    pass

                user.delete()
                message = f"Artist - {email} is deleted successfully."
                return deleteArtistUser(message=message)
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return deleteArtistUser(message=e)


class deleteB2CUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    
class deleteB2CUser(graphene.Mutation):
    class Arguments:
        input = deleteB2CUserInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                user = models.User.objects.get(email=email,is_buyer=True)
                
                models.CustomerEvent.objects.filter(user_id=user.id).delete()
                try:
                    models.LoginSummary.objects.filter(user_id=user.id).delete()
                except:
                    pass
                user.delete()
                message = f"User - {email} is deleted successfully."
                return deleteB2CUser(message=message)
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return deleteB2CUser(message=e)
            


class deleteB2BUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    
class deleteB2BUser(graphene.Mutation):
    class Arguments:
        input = deleteB2BUserInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                email = data.get('input')['email']
                user = models.User.objects.get(email=email,is_b2buser=True)
                models.CustomerEvent.objects.filter(user_id=user.id).delete()
                try:
                    models.LoginSummary.objects.filter(user_id=user.id).delete()
                except:
                    pass
                try:
                    models.b2bSubUserRelation.objects.filter(parentb2b_user_id=user.id).delete()
                except:
                    pass
                try:
                    models.SocialMediaLinks.objects.filter(parentb2b_user_id=user.id).delete()
                except:
                    pass
                user.delete()
                message = f"B2B User - {email} is deleted successfully."
                return deleteB2BUser(message=message)
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return deleteB2BUser(message=e)


class createPackageInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String(required=True)
    amount =graphene.Int(required=True)
    document_link =graphene.String(required=True)


class createPackage(graphene.Mutation):
    class Arguments:
        input = createPackageInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                title = data.get('input')['title']
                description = data.get('input')['description']
                amount = data.get('input')['amount']
                document_link = data.get('input')['document_link']
                package = models.Package(title=title,description=description,price=amount,document_link=document_link)
                package.save()
                message = "Package created successfully."
                return createPackage(message=message)
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except:
            return createPackage(message=e)

class manageB2BuserRequestInput(graphene.InputObjectType):
    is_b2buser = graphene.Boolean(description="User is accept or decline.", required=True)
    email = graphene.String(description="The email address of the user.", required=True)

class manageB2BuserRequest(ModelMutation):
    class Arguments:
        input = manageB2BuserRequestInput(
            description="Fields required to manage B2B user request.", required=True
        )
    message = graphene.String()

    class Meta:
        description = "Accept and Decline B2B user request."
        exclude = ["password"]
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                is_b2buser = data.get('input')['is_b2buser']
                email = data.get('input')['email']
                if is_b2buser:
                    user = models.User.objects.get(email=email)
                    user.is_b2buser = True
                    user.save()
                    message = "User with this email "+str(email)+" is approved."
                else:
                    user = models.User.objects.get(email=email)
                    user.is_b2buser = False
                    user.save()
                    message = "User with this email "+str(email)+" is decliend."
                return manageB2BuserRequest(message=message)
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except Exception as e:
            return manageB2BuserRequest(message=e)
    
class AddArtistInput(graphene.InputObjectType):
    phonenumber = graphene.String(description = "Phone number", required= True)
    country_code = graphene.String(description = "Country code", required= True)
    first_name = graphene.String(description = "first name", required= True)
    last_name = graphene.String(description = "last name", required= True)
    date_of_birth = graphene.String(description = "Date of birth", required= True)
    email = graphene.String(description="The email address of the user.", required=True)
    password = graphene.String(description="Password.", required=True)
    redirect_url = graphene.String(
        description=(
            "Base of frontend URL that will be needed to create confirmation URL."
        ),
        required=False,
    )

class AddArtist(ModelMutation):
    class Arguments:
        input = AddArtistInput(
            description="Fields required to create a user.", required=True
        )

    requires_confirmation = graphene.Boolean(
        description="Informs whether users need to confirm their email address."
    )

    class Meta:
        description = "Register a new user."
        exclude = ["password"]
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                response = super().mutate(root, info, **data)
                response.requires_confirmation = settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL
                return response
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except:
            raise Exception("Only admin have rights to perform this task.")

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        if not settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            return super().clean_input(info, instance, data, input_cls=None)
        elif not data.get("redirect_url"):
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        "This field is required.", code=AccountErrorCode.REQUIRED
                    )
                }
            )

        try:
            validate_storefront_url(data["redirect_url"])
        except ValidationError as error:
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        error.message, code=AccountErrorCode.INVALID
                    )
                }
            )

        password = data["password"]
        try:
            password_validation.validate_password(password, instance)
        except ValidationError as error:
            raise ValidationError({"password": error})

        return super().clean_input(info, instance, data, input_cls=None)
    
    @classmethod
    def save(cls, info, user, cleaned_input):
        password = cleaned_input["password"]
        user.set_password(password)
        if settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            user.is_active = False
            user.is_artist = True
            user.save()
            emails.send_account_confirmation_email(user, cleaned_input["redirect_url"])
        else:
            user.save()
        account_events.customer_account_created_event(user=user)
        info.context.plugins.customer_created(customer=user)




class AddB2BUserInput(graphene.InputObjectType):
    phonenumber = graphene.String(description = "Phone number", required= True)
    country_code = graphene.String(description = "Country code", required= True)
    first_name = graphene.String(description = "first name", required= True)
    last_name = graphene.String(description = "last name", required= True)
    date_of_birth = graphene.String(description = "Date of birth", required= True)
    email = graphene.String(description="The email address of the user.", required=True)
    package_id = graphene.Int(description = "package id", required= False)
    password = graphene.String(description="Password.", required=True)
    note = graphene.String(description = "Note", required= False)
    redirect_url = graphene.String(
        description=(
            "Base of frontend URL that will be needed to create confirmation URL."
        ),
        required=False,
    )

class AddB2BUser(ModelMutation):
    class Arguments:
        input = AddB2BUserInput(
            description="Fields required to create a user.", required=True
        )

    requires_confirmation = graphene.Boolean(
        description="Informs whether users need to confirm their email address."
    )

    class Meta:
        description = "Register a new user."
        exclude = ["password"]
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                response = super().mutate(root, info, **data)
                response.requires_confirmation = settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL
                return response
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except:
            raise Exception("Only admin have rights to perform this task.")

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        if not settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            return super().clean_input(info, instance, data, input_cls=None)
        elif not data.get("redirect_url"):
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        "This field is required.", code=AccountErrorCode.REQUIRED
                    )
                }
            )

        try:
            validate_storefront_url(data["redirect_url"])
        except ValidationError as error:
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        error.message, code=AccountErrorCode.INVALID
                    )
                }
            )

        password = data["password"]
        try:
            password_validation.validate_password(password, instance)
        except ValidationError as error:
            raise ValidationError({"password": error})

        return super().clean_input(info, instance, data, input_cls=None)
    
    @classmethod
    def save(cls, info, user, cleaned_input):
        password = cleaned_input["password"]
        user.set_password(password)
        if settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            user.is_active = False
            user.save()
            emails.send_account_confirmation_email(user, cleaned_input["redirect_url"])
        else:
            user.save()
        account_events.customer_account_created_event(user=user)
        info.context.plugins.customer_created(customer=user)


class AddUserInput(graphene.InputObjectType):
    phonenumber = graphene.String(description = "Phone number", required= True)
    country_code = graphene.String(description = "Country code", required= True)
    first_name = graphene.String(description = "first name", required= True)
    last_name = graphene.String(description = "last name", required= True)
    date_of_birth = graphene.String(description = "Date of birth", required= True)
    email = graphene.String(description="The email address of the user.", required=True)
    password = graphene.String(description="Password.", required=True)
    redirect_url = graphene.String(
        description=(
            "Base of frontend URL that will be needed to create confirmation URL."
        ),
        required=False,
    )

class AddUser(ModelMutation):
    class Arguments:
        input = AddUserInput(
            description="Fields required to create a user.", required=True
        )

    requires_confirmation = graphene.Boolean(
        description="Informs whether users need to confirm their email address."
    )

    class Meta:
        description = "Register a new user."
        exclude = ["password"]
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if AdminAuthorization(info):
                response = super().mutate(root, info, **data)
                response.requires_confirmation = settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL
                return response
            else:
                raise Exception("Only admin have rights to perform this task.")    
        except:
            raise Exception("Only admin have rights to perform this task.")

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        if not settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            return super().clean_input(info, instance, data, input_cls=None)
        elif not data.get("redirect_url"):
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        "This field is required.", code=AccountErrorCode.REQUIRED
                    )
                }
            )

        try:
            validate_storefront_url(data["redirect_url"])
        except ValidationError as error:
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        error.message, code=AccountErrorCode.INVALID
                    )
                }
            )

        password = data["password"]
        try:
            password_validation.validate_password(password, instance)
        except ValidationError as error:
            raise ValidationError({"password": error})

        return super().clean_input(info, instance, data, input_cls=None)
    
    @classmethod
    def save(cls, info, user, cleaned_input):
        password = cleaned_input["password"]
        user.set_password(password)
        if settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            user.is_active = False
            user.is_buyer = True
            user.save()
            emails.send_account_confirmation_email(user, cleaned_input["redirect_url"])
        else:
            user.save()
        account_events.customer_account_created_event(user=user)
        info.context.plugins.customer_created(customer=user)

class AccountRegisterInput(graphene.InputObjectType):
    is_artist = graphene.Boolean(description = "Artist", required= False)
    is_buyer = graphene.Boolean(description = "Buyer", required= False)
    is_staff = graphene.Boolean(description = "Staff", required= False)
    available_token = graphene.Int(description = "Available Token", required= False)
    pan_number = graphene.String(description = "Pan number", required= False)
    gst_number = graphene.String(description = "gst number", required= False)
    gender = graphene.String(description = "Gender", required= False)
    package_id = graphene.Int(description = "package id", required= False)
    phonenumber = graphene.String(description = "Phone number", required= False)
    country_code = graphene.String(description = "Country code", required= False)
    is_loginwith_google = graphene.Boolean(description = "Login With Google", required= False)
    is_loginwith_facebook = graphene.Boolean(description = "Login With Facebook", required= False)
    first_name = graphene.String(description = "first name", required= False)
    last_name = graphene.String(description = "last name", required= False)
    date_of_birth = graphene.String(description = "Date of birth", required= False)

    email = graphene.String(description="The email address of the user.", required=True)
    password = graphene.String(description="Password.", required=True)
    redirect_url = graphene.String(
        description=(
            "Base of frontend URL that will be needed to create confirmation URL."
        ),
        required=False,
    )


class AccountRegister(ModelMutation):
    class Arguments:
        input = AccountRegisterInput(
            description="Fields required to create a user.", required=True
        )

    requires_confirmation = graphene.Boolean(
        description="Informs whether users need to confirm their email address."
    )

    class Meta:
        description = "Register a new user."
        exclude = ["password"]
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def mutate(cls, root, info, **data):
        response = super().mutate(root, info, **data)
        response.requires_confirmation = settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL
        return response

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        if not settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            return super().clean_input(info, instance, data, input_cls=None)
        elif not data.get("redirect_url"):
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        "This field is required.", code=AccountErrorCode.REQUIRED
                    )
                }
            )

        try:
            validate_storefront_url(data["redirect_url"])
        except ValidationError as error:
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        error.message, code=AccountErrorCode.INVALID
                    )
                }
            )

        password = data["password"]
        try:
            password_validation.validate_password(password, instance)
        except ValidationError as error:
            raise ValidationError({"password": error})

        return super().clean_input(info, instance, data, input_cls=None)

    @classmethod
    def save(cls, info, user, cleaned_input):
        password = cleaned_input["password"]
        user.set_password(password)
        if settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            user.is_active = False
            user.save()
            emails.send_account_confirmation_email(user, cleaned_input["redirect_url"])
        else:
            user.save()
        account_events.customer_account_created_event(user=user)
        info.context.plugins.customer_created(customer=user)


class AccountInput(graphene.InputObjectType):
    first_name = graphene.String(description="Given name.")
    last_name = graphene.String(description="Family name.")
    default_billing_address = AddressInput(
        description="Billing address of the customer."
    )
    default_shipping_address = AddressInput(
        description="Shipping address of the customer."
    )


class AccountUpdate(BaseCustomerCreate):
    class Arguments:
        input = AccountInput(
            description="Fields required to update the account of the logged-in user.",
            required=True,
        )

    class Meta:
        description = "Updates the account of the logged-in user."
        exclude = ["password"]
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = info.context.user
        data["id"] = graphene.Node.to_global_id("User", user.id)
        return super().perform_mutation(root, info, **data)


class AccountRequestDeletion(BaseMutation):
    class Arguments:
        redirect_url = graphene.String(
            required=True,
            description=(
                "URL of a view where users should be redirected to "
                "delete their account. URL in RFC 1808 format."
            ),
        )

    class Meta:
        description = (
            "Sends an email with the account removal link for the logged-in user."
        )
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = info.context.user
        redirect_url = data["redirect_url"]
        try:
            validate_storefront_url(redirect_url)
        except ValidationError as error:
            raise ValidationError(
                {"redirect_url": error}, code=AccountErrorCode.INVALID
            )
        emails.send_account_delete_confirmation_email_with_url(redirect_url, user)
        return AccountRequestDeletion()


class AccountDelete(ModelDeleteMutation):
    class Arguments:
        token = graphene.String(
            description=(
                "A one-time token required to remove account. "
                "Sent by email using AccountRequestDeletion mutation."
            ),
            required=True,
        )

    class Meta:
        description = "Remove user account."
        model = models.User
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def clean_instance(cls, info, instance):
        super().clean_instance(info, instance)
        if instance.is_staff:
            raise ValidationError(
                "Cannot delete a staff account.",
                code=AccountErrorCode.DELETE_STAFF_ACCOUNT,
            )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        user = info.context.user
        cls.clean_instance(info, user)

        token = data.pop("token")
        if not default_token_generator.check_token(user, token):
            raise ValidationError(
                {"token": ValidationError(INVALID_TOKEN, code=AccountErrorCode.INVALID)}
            )

        db_id = user.id

        user.delete()
        # After the instance is deleted, set its ID to the original database's
        # ID so that the success response contains ID of the deleted object.
        user.id = db_id
        return cls.success_response(user)


class AccountAddressCreate(ModelMutation, I18nMixin):
    user = graphene.Field(
        User, description="A user instance for which the address was created."
    )

    class Arguments:
        input = AddressInput(
            description="Fields required to create address.", required=True
        )
        type = AddressTypeEnum(
            required=False,
            description=(
                "A type of address. If provided, the new address will be "
                "automatically assigned as the customer's default address "
                "of that type."
            ),
        )

    class Meta:
        description = "Create a new address for the customer."
        model = models.Address
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        address_type = data.get("type", None)
        user = info.context.user
        cleaned_input = cls.clean_input(
            info=info, instance=Address(), data=data.get("input")
        )
        address = cls.validate_address(cleaned_input)
        cls.clean_instance(info, address)
        cls.save(info, address, cleaned_input)
        cls._save_m2m(info, address, cleaned_input)
        if address_type:
            utils.change_user_default_address(user, address, address_type)
        return AccountAddressCreate(user=user, address=address)

    @classmethod
    def save(cls, info, instance, cleaned_input):
        super().save(info, instance, cleaned_input)
        user = info.context.user
        instance.user_addresses.add(user)


class AccountAddressUpdate(BaseAddressUpdate):
    class Meta:
        description = "Updates an address of the logged-in user."
        model = models.Address
        error_type_class = AccountError
        error_type_field = "account_errors"


class AccountAddressDelete(BaseAddressDelete):
    class Meta:
        description = "Delete an address of the logged-in user."
        model = models.Address
        error_type_class = AccountError
        error_type_field = "account_errors"


class AccountSetDefaultAddress(BaseMutation):
    user = graphene.Field(User, description="An updated user instance.")

    class Arguments:
        id = graphene.ID(
            required=True, description="ID of the address to set as default."
        )
        type = AddressTypeEnum(required=True, description="The type of address.")

    class Meta:
        description = "Sets a default address for the authenticated user."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        address = cls.get_node_or_error(info, data.get("id"), Address)
        user = info.context.user

        if not user.addresses.filter(pk=address.pk).exists():
            raise ValidationError(
                {
                    "id": ValidationError(
                        "The address doesn't belong to that user.",
                        code=AccountErrorCode.INVALID,
                    )
                }
            )

        if data.get("type") == AddressTypeEnum.BILLING.value:
            address_type = AddressType.BILLING
        else:
            address_type = AddressType.SHIPPING

        utils.change_user_default_address(user, address, address_type)
        return cls(user=user)


class AccountUpdateMeta(UpdateMetaBaseMutation):
    class Meta:
        description = "Updates metadata of the logged-in user."
        model = models.User
        public = True
        error_type_class = AccountError
        error_type_field = "account_errors"

    class Arguments:
        input = MetaInput(
            description="Fields required to update new or stored metadata item.",
            required=True,
        )

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def get_instance(cls, info, **data):
        return info.context.user


class RequestEmailChange(BaseMutation):
    user = graphene.Field(User, description="A user instance.")

    class Arguments:
        password = graphene.String(required=True, description="User password.")
        new_email = graphene.String(required=True, description="New user email.")
        redirect_url = graphene.String(
            required=True,
            description=(
                "URL of a view where users should be redirected to "
                "update the email address. URL in RFC 1808 format."
            ),
        )

    class Meta:
        description = "Request email change of the logged in user."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        user = info.context.user
        password = data["password"]
        new_email = data["new_email"]
        redirect_url = data["redirect_url"]

        if not user.check_password(password):
            raise ValidationError(
                {
                    "password": ValidationError(
                        "Password isn't valid.",
                        code=AccountErrorCode.INVALID_CREDENTIALS,
                    )
                }
            )
        if models.User.objects.filter(email=new_email).exists():
            raise ValidationError(
                {
                    "new_email": ValidationError(
                        "Email is used by other user.", code=AccountErrorCode.UNIQUE
                    )
                }
            )
        try:
            validate_storefront_url(redirect_url)
        except ValidationError as error:
            raise ValidationError(
                {"redirect_url": error}, code=AccountErrorCode.INVALID
            )
        token_payload = {
            "old_email": user.email,
            "new_email": new_email,
            "user_pk": user.pk,
        }
        token = create_token(token_payload, JWT_TTL_REQUEST_EMAIL_CHANGE)
        emails.send_user_change_email_url(redirect_url, user, new_email, token)
        return RequestEmailChange(user=user)


class ConfirmEmailChange(BaseMutation):
    user = graphene.Field(User, description="A user instance with a new email.")

    class Arguments:
        token = graphene.String(
            description="A one-time token required to change the email.", required=True
        )

    class Meta:
        description = "Confirm the email change of the logged-in user."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def get_token_payload(cls, token):
        try:
            payload = jwt_decode(token)
        except jwt.PyJWTError:
            raise ValidationError(
                {
                    "token": ValidationError(
                        "Invalid or expired token.",
                        code=AccountErrorCode.JWT_INVALID_TOKEN,
                    )
                }
            )
        return payload

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        user = info.context.user
        token = data["token"]

        payload = cls.get_token_payload(token)
        new_email = payload["new_email"]
        old_email = payload["old_email"]

        if models.User.objects.filter(email=new_email).exists():
            raise ValidationError(
                {
                    "new_email": ValidationError(
                        "Email is used by other user.", code=AccountErrorCode.UNIQUE
                    )
                }
            )

        user.email = new_email
        user.save(update_fields=["email"])
        emails.send_user_change_email_notification(old_email)
        event_parameters = {"old_email": old_email, "new_email": new_email}

        account_events.customer_email_changed_event(
            user=user, parameters=event_parameters
        )
        return ConfirmEmailChange(user=user)
#B2B (Profile Setup)
class businessProfileSetupInput(graphene.InputObjectType):
    company_name = graphene.String(required=True)
    contact_person = graphene.String(required=True)
    pan_number = graphene.String(required=True)
    gst_number = graphene.String(required=True)
    facebook_link = graphene.String(required=False)
    instagram_link = graphene.String(required=False)
    twitter_link = graphene.String(required=False)

class businessProfileSetup(graphene.Mutation):
    class Arguments:
        input = businessProfileSetupInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                company_name = data.get('input')['company_name']
                contact_person = data.get('input')['contact_person']
                pan_number = data.get('input')['pan_number']
                gst_number = data.get('input')['gst_number']
                facebook_link = data.get('input')['facebook_link']
                instagram_link = data.get('input')['instagram_link']
                twitter_link = data.get('input')['twitter_link']
                
                user = models.User.objects.get(gst_number=gst_number,is_b2buser=True)
                sml = models.SocialMediaLinks.objects.filter(user_id=user.id)

                user.company_name = company_name
                user.contact_person = contact_person
                user.pan_number = pan_number
                user.gst_number = gst_number

                if len(sml)>0:
                    data = models.SocialMediaLinks.objects.get(user_id=user.id)
                    data.facebook_link = facebook_link
                    data.twitter_link = twitter_link
                    data.instagram_link = instagram_link
                    data.save()

                else:
                    social_media = models.SocialMediaLinks.objects.create(facebook_link=facebook_link,twitter_link=twitter_link,instagram_link=instagram_link,user_id = user.id)
                    user.social_media_id = social_media.id

                user.save()
                message = "Profile updated successfully."
                return businessProfileSetup(message=message)

        except Exception as e:
            return businessProfileSetup(message=e)

#B2B (Business Details)
class businessDetailsInput(graphene.InputObjectType):
    company_name = graphene.String(required=True)
    contact_person = graphene.String(required=True)
    pan_number = graphene.String(required=True)
    gst_number = graphene.String(required=True)
    facebook_link = graphene.String(required=False)
    instagram_link = graphene.String(required=False)
    twitter_link = graphene.String(required=False)

class businessDetails(graphene.Mutation):
    class Arguments:
        input = businessDetailsInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                company_name = data.get('input')['company_name']
                contact_person = data.get('input')['contact_person']
                pan_number = data.get('input')['pan_number']
                gst_number = data.get('input')['gst_number']
                facebook_link = data.get('input')['facebook_link']
                instagram_link = data.get('input')['instagram_link']
                twitter_link = data.get('input')['twitter_link']
                
                user = models.User.objects.get(gst_number=gst_number,is_b2buser=True)
                sml = models.SocialMediaLinks.objects.filter(user_id=user.id)

                user.company_name = company_name
                user.contact_person = contact_person
                user.pan_number = pan_number
                user.gst_number = gst_number

                if len(sml)>0:
                    data = models.SocialMediaLinks.objects.get(user_id=user.id)
                    data.facebook_link = facebook_link
                    data.twitter_link = twitter_link
                    data.instagram_link = instagram_link
                    data.save()
                    
                else:
                    social_media = models.SocialMediaLinks.objects.create(facebook_link=facebook_link,twitter_link=twitter_link,instagram_link=instagram_link,user_id = user.id)
                    user.social_media_id = social_media.id
                
                user.save()
                message = "Profile updated successfully."
                return businessDetails(message=message)

        except Exception as e:
            return businessDetails(message=e)

#B2B INTERESTED
class interestB2BInput(graphene.InputObjectType):
    first_name = graphene.String(description = "first name", required= True)
    last_name = graphene.String(description = "last name", required= True)
    country_code = graphene.String(description = "Country code", required= True)
    phonenumber = graphene.String(description = "Phone number", required= True)
    email = graphene.String(description="The email address of the user.", required=True)
    date_of_birth = graphene.String(description = "Date of birth", required= True)
    gender = graphene.String(description = "Gender", required= False)
    facebook_link = graphene.String(required=False)
    twitter_link = graphene.String(required=False)
    instagram_link = graphene.String(required=False)

    company_name = graphene.String(required=True)
    contact_person = graphene.String(required=True)
    company_phone_code = graphene.String(required=True)
    company_phone = graphene.String(required=True)

    company_country = graphene.String(required=True)
    company_state = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_zipcode = graphene.String(required=True)

class interestB2B(graphene.Mutation):
    class Arguments:
        input = interestB2BInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                first_name = data.get('input')['first_name']
                last_name = data.get('input')['last_name']
                country_code = data.get('input')['country_code']
                phonenumber = data.get('input')['phonenumber']
                email = data.get('input')['email']
                date_of_birth = data.get('input')['date_of_birth']
                gender = data.get('input')['gender']
                facebook_link = data.get('input')['facebook_link']
                twitter_link = data.get('input')['twitter_link']
                instagram_link = data.get('input')['instagram_link']

                company_name = data.get('input')['company_name']
                contact_person = data.get('input')['contact_person']
                company_phone_code = data.get('input')['company_phone_code']
                company_phone = data.get('input')['company_phone']

                company_country = data.get('input')['company_country']
                company_state = data.get('input')['company_state']
                company_city = data.get('input')['company_city']
                company_zipcode = data.get('input')['company_zipcode']
                
                
                # client = GraphqlClient('http://localhost:8000/graphql/')
                mutation = """
               mutation accountRegister($first_name: String, $last_name: String, $date_of_birth: String, $email: String!, $gender: String, $phonenumber: String, $country_code: String){
                accountRegister(input:{
                    isStaff:false
                    isBuyer:false
                    isArtist:false
                    firstName: $first_name
                    lastName: $last_name
                    availableToken:0
                    dateOfBirth: $date_of_birth
                    redirectUrl:"http://localhost:3000/account-confirm/"
                    email: $email
                    password:"Sanket@123"
                    panNumber : ""
                    gstNumber : ""
                    gender : $gender
                    packageId : 1
                    isLoginwithGoogle :false
                    isLoginwithFacebook:false
                    phonenumber: $phonenumber
                    countryCode: $country_code
                }){
                user{
                email
                }
            }
            }
            """
                print(mutation)
                variables = {'first_name':first_name, 'last_name':last_name, 'date_of_birth':date_of_birth, 'email':email, 'gender':gender, 'phonenumber':phonenumber,'country_code':country_code}
                
                # client.execute(mutation, variables)
                request = requests.post("http://localhost:8000/graphql/", json={'query': mutation, 'variables': variables})
                print(request.json())
                user = models.User.objects.get(email=email)
                
                user.first_name = first_name
                user.last_name = last_name
                user.country_code = country_code
                user.phonenumber = phonenumber
                user.email = email
                user.date_of_birth = date_of_birth
                user.gender = gender
                user.company_name = company_name
                user.contact_person = contact_person
                user.company_phone_code = company_phone_code
                user.company_phone = company_phone
                user.company_country = company_country
                user.company_state = company_state
                user.company_city = company_city
                user.company_zipcode = company_zipcode

                sml = models.SocialMediaLinks.objects.filter(user_id=user.id)
                
                if len(sml)>0:
                    data = models.SocialMediaLinks.objects.get(user_id=user.id)
                    data.facebook_link = facebook_link
                    data.twitter_link = twitter_link
                    data.instagram_link = instagram_link
                    data.save()
                    
                else:
                    social_media = models.SocialMediaLinks.objects.create(facebook_link=facebook_link,twitter_link=twitter_link,instagram_link=instagram_link,user_id = user.id)
                    user.social_media_id = social_media.id
                
                user.save()                

                # if request.status_code == 200:
                #     print(request.json())
                # else:
                #     raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, mutation))

                message = "Request send successfully."
                return interestB2B(message=message)

        except Exception as e:
            return interestB2B(message=e)


#Add new sub user
class addSubUserInput(graphene.InputObjectType):
    avatar = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    country_code = graphene.String(required=True)
    phonenumber = graphene.String(required=True)
    date_of_birth = graphene.String(required=True)
    email = graphene.String(required=True)

    company_name = graphene.String(required=True)
    contact_person = graphene.String(required=True)
    pan_number = graphene.String(required=True)
    gst_number = graphene.String(required=True)
    facebook_link = graphene.String(required=False)
    instagram_link = graphene.String(required=False)
    twitter_link = graphene.String(required=False)

    default_shipping_address = graphene.String(required=True)
    country = graphene.String(required=True)
    zipcode = graphene.String(required=True)
    city = graphene.String(required=True)
    state = graphene.String(required=True)
    # billing_address_is_same_as_shipping = graphene.Boolean()
    # i_agree_with_terms_and_condition = graphene.Boolean()


class addSubUser(graphene.Mutation):
    class Arguments:
        input = addSubUserInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                avatar = data.get('input')['avatar']
                first_name = data.get('input')['first_name']
                last_name = data.get('input')['last_name']
                country_code = data.get('input')['country_code']
                phonenumber = data.get('input')['phonenumber']
                date_of_birth = data.get('input')['date_of_birth']
                email = data.get('input')['email']
                company_name = data.get('input')['company_name']
                contact_person = data.get('input')['contact_person']
                pan_number = data.get('input')['pan_number']
                gst_number = data.get('input')['gst_number']
                facebook_link = data.get('input')['facebook_link']
                instagram_link = data.get('input')['instagram_link']
                twitter_link = data.get('input')['twitter_link']

                default_shipping_address = data.get('input')['default_shipping_address']
                country = data.get('input')['country']
                zipcode = data.get('input')['zipcode']
                city = data.get('input')['city']
                state = data.get('input')['state']
                # billing_address_is_same_as_shipping = data.get('input')['billing_address_is_same_as_shipping']
                # i_agree_with_terms_and_condition = data.get('input')['i_agree_with_terms_and_condition']

                mutation = """
                mutation accountRegister($first_name: String, $last_name: String, $date_of_birth: String, $email: String!, $phonenumber: String, $country_code: String, $pan_number: String, $gst_number: String){
                accountRegister(input:{
                    isStaff:false
                    isBuyer:false
                    isArtist:false
                    firstName: $first_name
                    lastName: $last_name
                    availableToken:0
                    dateOfBirth: $date_of_birth
                    redirectUrl:"http://localhost:3000/account-confirm/"
                    email: $email
                    password:"yudiz@123"
                    panNumber : $pan_number
                    gstNumber : $gst_number
                    gender : ""
                    packageId : 1
                    isLoginwithGoogle :false
                    isLoginwithFacebook:false
                    phonenumber: $phonenumber
                    countryCode: $country_code
                }){
                user{
                    email
                }
            }
            }
            """
                variables = {'first_name':first_name, 'last_name':last_name, 'date_of_birth':date_of_birth, 'email':email, 'phonenumber':phonenumber,'country_code':country_code, 'pan_number':pan_number, 'gst_number': gst_number}
                
                # client.execute(mutation, variables)
                request = requests.post("http://localhost:8000/graphql/", json={'query': mutation, 'variables': variables})

                adr = models.Address.objects.create(street_address_1=default_shipping_address)

                user = models.User.objects.get(email=email)
                
                user.avatar = avatar
                user.first_name=first_name
                user.last_name=last_name
                user.country_code=country_code
                user.phonenumber=phonenumber
                user.date_of_birth=date_of_birth
                user.email=email
                user.company_name=company_name
                user.contact_person=contact_person
                user.pan_number=pan_number
                user.gst_number=gst_number
                user.default_shipping_address=models.Address.objects.get(id=adr.id)
                
                adr.country = country
                adr.postal_code = zipcode
                adr.city = city
                adr.state = state

                last_row = models.LoginSummary.objects.last()
                parent_id = last_row.user_id
                user.parent_id = parent_id

                sml = models.SocialMediaLinks.objects.filter(user_id=user.id)

                # user.default_shipping_address = default_shipping_address

                # user.billing_address_is_same_as_shipping = billing_address_is_same_as_shipping
                # user.i_agree_with_terms_and_condition = i_agree_with_terms_and_condition

                if len(sml) > 0:
                    data = models.SocialMediaLinks.objects.get(user_id=user.id)
                    data.facebook_link = facebook_link
                    data.twitter_link = twitter_link
                    data.instagram_link = instagram_link
                    data.save()

                else:
                    social_media = models.SocialMediaLinks.objects.create(facebook_link=facebook_link,
                                                                          twitter_link=twitter_link,
                                                                          instagram_link=instagram_link,
                                                                          user_id=user.id)
                    user.social_media_id = social_media.id

                user.save()
                adr.save()

                message = "User added successfully."
                return addSubUser(message=message)

        except Exception as e:
            return addSubUser(message=e)

# B2B SUB USER DETAILS
class subUserDetailInput(graphene.InputObjectType):
    avatar = graphene.String(required=True)
    first_name = graphene.String(description="first_name",required=True)
    last_name = graphene.String(description="last_name",required=True)
    phonenumber = graphene.String(description="phonenumber",required=True)
    date_of_birth = graphene.String(required=True)
    email = graphene.String(required=True)

    company_name = graphene.String(required=True)
    contact_person = graphene.String(required=True)
    pan_number = graphene.String(required=True)
    gst_number = graphene.String(required=True)
    facebook_link = graphene.String(required=False)
    instagram_link = graphene.String(required=False)
    twitter_link = graphene.String(required=False)


class subUserDetail(graphene.Mutation):
    class Arguments:
        input = subUserDetailInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                avatar = data.get('input')['avatar']
                first_name = data.get('input')['first_name']
                last_name = data.get('input')['last_name']
                phonenumber = data.get('input')['phonenumber']
                date_of_birth = data.get('input')['date_of_birth']
                email = data.get('input')['email']
                company_name = data.get('input')['company_name']
                contact_person = data.get('input')['contact_person']
                pan_number = data.get('input')['pan_number']
                gst_number = data.get('input')['gst_number']
                facebook_link = data.get('input')['facebook_link']
                instagram_link = data.get('input')['instagram_link']
                twitter_link = data.get('input')['twitter_link']

                user = models.User.objects.get(email=email)
                user.avatar = avatar
                user.first_name=first_name
                user.last_name=last_name
                user.phonenumber=phonenumber
                user.date_of_birth=date_of_birth
                user.email=email
                user.company_name=company_name
                user.contact_person=contact_person
                user.pan_number=pan_number
                user.gst_number=gst_number

                last_row = models.LoginSummary.objects.last()
                parent_id = last_row.user_id
                
                user.parent_id = parent_id
                
                sml = models.SocialMediaLinks.objects.filter(user_id=user.id)

                if len(sml) > 0:
                    data = models.SocialMediaLinks.objects.get(user_id=user.id)
                    data.facebook_link = facebook_link
                    data.twitter_link = twitter_link
                    data.instagram_link = instagram_link
                    data.save()

                else:
                    social_media = models.SocialMediaLinks.objects.create(facebook_link=facebook_link,
                                                                          twitter_link=twitter_link,
                                                                          instagram_link=instagram_link,
                                                                          user_id=user.id)
                    user.social_media_id = social_media.id

                user.save()
                message = "Profile updated successfully."
                return subUserDetail(message=message)

        except Exception as e:
            return subUserDetail(message=e)

#B2B Sub user checkout
class subUserCheckoutInput(graphene.InputObjectType):
    select_subuser = graphene.Int(required=True)
    quantity = graphene.Int(required=True)
    apply_promo_code = graphene.String(required=True)
    # apply_token = graphene.Boolean(required=False)

class subUserCheckout(graphene.Mutation):
    class Arguments:
        input = subUserCheckoutInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                select_subuser = data.get('input')['select_subuser']
                quantity = data.get('input')['quantity']
                apply_promo_code = data.get('input')['apply_promo_code']
                # apply_token = data.get('input')['apply_token']

                # user_id = from_global_id_strict_type(user_id, only_type="User", field="pk")
                user_id = models.User.objects.get(id=select_subuser) 

                checkout = Checkout.objects.create(
                user_id = user_id.id
                ,quantity = quantity
                ,voucher_code = apply_promo_code
                # ,apply_token = apply_token
                )

                checkout.save()
                message = "Check Out Successful."
                return subUserCheckout(message=message)

        except Exception as e:
            return subUserCheckout(message=e)

#Sub user checkout
class subUserCheckoutInput(graphene.InputObjectType):
    select_subuser = graphene.Int(required=True)
    quantity = graphene.Int(required=True)
    apply_promo_code = graphene.String(required=True)
    apply_token = graphene.String(required=False)

class subUserCheckout(graphene.Mutation):
    class Arguments:
        input = subUserCheckoutInput(required=False)

    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            if B2BUserAuthorization(info):
                select_subuser = data.get('input')['select_subuser']
                quantity = data.get('input')['quantity']
                apply_promo_code = data.get('input')['apply_promo_code']
                apply_token = data.get('input')['apply_token']

                user_id = models.User.objects.get(id=select_subuser)

                checkout = Checkout.objects.create(
                user_id = user_id.id
                ,quantity = quantity
                ,voucher_code = apply_promo_code
                )

                checkout.save()
                token = models.TokenActivity.objects.create(
                    user_id = user_id.id,
                    token_amount = apply_token
                )
                token.save()
                message = "Check Out Successful."
                return subUserCheckout(message=message)

        except Exception as e:
            return subUserCheckout(message=e)