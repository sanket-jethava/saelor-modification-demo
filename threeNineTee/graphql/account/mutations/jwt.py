from typing import Optional

from django.middleware import csrf

import graphene
import jwt
from django.core.exceptions import ValidationError
from django.middleware.csrf import (  # type: ignore
    _compare_masked_tokens,
    _get_new_csrf_token,
)
from django.utils import timezone
from django.utils.crypto import get_random_string
from graphene.types.generic import GenericScalar

from ....account import models
from ....account.error_codes import AccountErrorCode
from ....core.jwt import (
    JWT_REFRESH_TOKEN_COOKIE_NAME,
    JWT_REFRESH_TYPE,
    PERMISSIONS_FIELD,
    create_access_token,
    create_refresh_token,
    get_user_from_payload,
    jwt_decode,
)
from ....core.permissions import get_permissions_from_names
from ...core.mutations import BaseMutation
from ...core.types.common import AccountError
from ..types import User,MobileOTP


def get_payload(token):
    try:
        payload = jwt_decode(token)
    except jwt.ExpiredSignature:
        raise ValidationError(
            "Signature has expired", code=AccountErrorCode.JWT_SIGNATURE_EXPIRED.value
        )
    except jwt.DecodeError:
        raise ValidationError(
            "Error decoding signature", code=AccountErrorCode.JWT_DECODE_ERROR.value
        )
    except jwt.InvalidTokenError:
        raise ValidationError(
            "Invalid token", code=AccountErrorCode.JWT_INVALID_TOKEN.value
        )
    return payload


def get_user(payload):
    try:
        user = get_user_from_payload(payload)
    except Exception:
        user = None
    if not user:
        raise ValidationError(
            "Invalid token", code=AccountErrorCode.JWT_INVALID_TOKEN.value
        )
    permissions = payload.get(PERMISSIONS_FIELD)
    if permissions is not None:
        user.effective_permissions = get_permissions_from_names(permissions)
    return user


class CreateToken(BaseMutation):
    """Mutation that authenticates a user and returns token and user data."""

    class Arguments:
        email = graphene.String(required=True, description="Email of a user.")
        password = graphene.String(required=True, description="Password of a user.")
        deviceType = graphene.String(required=True, description="Device type.")


    class Meta:
        description = "Create JWT token."
        error_type_class = AccountError
        error_type_field = "account_errors"

    token = graphene.String(description="JWT token, required to authenticate.")
    refresh_token = graphene.String(
        description="JWT refresh token, required to re-generate access token."
    )
    csrf_token = graphene.String(
        description="CSRF token required to re-generate access token."
    )
    user = graphene.Field(User, description="A user instance.")

    @classmethod
    def _retrieve_user_from_credentials(cls, email, password) -> Optional[models.User]:
        user = models.User.objects.filter(email=email, is_active=True).first()
        if user and user.check_password(password):
            return user
        return None

    @classmethod
    def get_user(cls, _info, data):
        user = cls._retrieve_user_from_credentials(data["email"], data["password"])
        if not user:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "Please, enter valid credentials",
                        code=AccountErrorCode.INVALID_CREDENTIALS.value,
                    )
                }
            )
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = cls.get_user(info, data)
        access_token = create_access_token(user)
        csrf_token = _get_new_csrf_token()
        refresh_token = create_refresh_token(user, {"csrfToken": csrf_token})
        info.context.refresh_token = refresh_token
        info.context._cached_user = user
        user.last_login = timezone.now()
        import datetime
        loginsummary = models.LoginSummary.objects.create(user_id=user.id,
            date=str(datetime.datetime.now().date()),
            login_time=datetime.datetime.now().time(),
            device_type=data['deviceType'],
            login_token_key=access_token)
        
        user.save(update_fields=["last_login"])
        

        return cls(
            errors=[],
            user=user,
            token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )

class SendOTP(BaseMutation):
    class Arguments:
        mobile = graphene.String(description = "Phone number", required= True)
    
    class Meta:
        description = "Send OTP for Login."
        error_type_class = AccountError
        error_type_field = "account_errors"
    
    otp = graphene.Field(MobileOTP, description="A user instance.")
    status = graphene.String(description="Status of logged out.")

    @classmethod
    def perform_mutation(cls, root, info, **data): 
        otpdata = None   
        try:
            record = models.User.objects.get( phonenumber = data['mobile'])
            if record!=None:
                import random
                import requests
                otp = random.randrange(100000,999999)
                
                link = "https://api.msg91.com/api/v5/otp?authkey=337066Ae96CRHMsaE5f1ebecaP1&template_id=5f23ae07d6fc052b4b688ece&extra_param={%22NAME%22:%22Sanket%22,%20%22OTP%22:%20%22"+str(otp)+"%22}&mobile="+str(data['mobile'])
                res = requests.get(link)
                
                otpdata = models.loginOTP.objects.create(otp = otp,mobile = data['mobile'])
                

        except:
            return cls(
            errors=[],
            status = 'User Not Found!'
            )

        return cls(
            errors=[],
            status = 'OTP sent to '+data['mobile'],
            otp = otpdata
        )

class VerifyOTP(BaseMutation):
    class Arguments:
        mobile = graphene.String(description = "Phone number", required= True)
        otp = graphene.String(description = "One Time Password", required= True)
        deviceType = graphene.String(required=True, description="Device type.")
    
    class Meta:
        description = "OTP Verifiaction and Login."
        error_type_class = AccountError
        error_type_field = "account_errors"
    
    token = graphene.String(description="JWT token, required to authenticate.")
    refresh_token = graphene.String(
        description="JWT refresh token, required to re-generate access token."
    )
    csrf_token = graphene.String(
        description="CSRF token required to re-generate access token."
    )
    user = graphene.Field(User, description="A user instance.")
    status = graphene.String(description="Status")

    @classmethod
    def perform_mutation(cls, root, info, **data): 
        try:
            record = models.loginOTP.objects.get( otp = data['otp'],mobile = data['mobile'])
            if record!=None:
                user = models.User.objects.get( phonenumber = data['mobile'])
                access_token = create_access_token(user)
                csrf_token = _get_new_csrf_token()
                refresh_token = create_refresh_token(user, {"csrfToken": csrf_token})
                user.last_login = timezone.now()
                import datetime
                loginsummary = models.LoginSummary.objects.create(user_id=user.id,
                    date=str(datetime.datetime.now().date()),
                    login_time=datetime.datetime.now().time(),
                    device_type=data['deviceType'],
                    login_token_key=access_token)
                user.save(update_fields=["last_login"])
                record.delete()
                return cls(
                    errors=[],
                    user=user,
                    token=access_token,
                    refresh_token=refresh_token,
                    csrf_token=csrf_token,
                    status = "Logged in Successful."
                )
        except:
            return cls(
                    errors=[],
                    status = "OTP Doesn't Match! Please Try Again."
                )

class DestroyToken(BaseMutation):
    """Mutation that destroy the user login token and user logout. It returns the status either user logged out or user already logged out."""

    class Arguments:
        token = graphene.String(required=True, description="User login token key.")


    class Meta:
        description = "Destroy JWT token."
        error_type_class = AccountError
        error_type_field = "account_errors"

    
    user = graphene.Field(User, description="A user instance.")
    status = graphene.String(description="Status of logged out.")


    @classmethod
    def perform_mutation(cls, root, info, **data):    
        try:
            record = models.LoginSummary.objects.get( login_token_key = data['token'])
        except:
            return cls(
            errors=[],
            status = 'User Already Logged Out.'
            )
        import datetime
        record.logout_time = datetime.datetime.now().time()
        record.login_token_key = None
        record.save()
        return cls(
            errors=[],
            status = 'Logged Out Successfully.'
        )

class RefreshToken(BaseMutation):
    """Mutation that refresh user token and returns token and user data."""

    token = graphene.String(description="JWT token, required to authenticate.")
    user = graphene.Field(User, description="A user instance.")

    class Arguments:
        refresh_token = graphene.String(required=False, description="Refresh token.")
        csrf_token = graphene.String(
            required=False,
            description=(
                "CSRF token required to refresh token. This argument is "
                "required when refreshToken is provided as a cookie."
            ),
        )

    class Meta:
        description = (
            "Refresh JWT token. Mutation tries to take refreshToken from the input."
            "If it fails it will try to take refreshToken from the http-only cookie -"
            f"{JWT_REFRESH_TOKEN_COOKIE_NAME}. csrfToken is required when refreshToken "
            "is provided as a cookie."
        )
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def get_refresh_token_payload(cls, refresh_token):
        try:
            payload = get_payload(refresh_token)
        except ValidationError as e:
            raise ValidationError({"refreshToken": e})
        return payload

    @classmethod
    def get_refresh_token(cls, info, data):
        request = info.context
        refresh_token = request.COOKIES.get(JWT_REFRESH_TOKEN_COOKIE_NAME, None)
        refresh_token = data.get("refresh_token") or refresh_token
        return refresh_token

    @classmethod
    def clean_refresh_token(cls, refresh_token):
        if not refresh_token:
            raise ValidationError(
                {
                    "refreshToken": ValidationError(
                        "Missing refreshToken",
                        code=AccountErrorCode.JWT_MISSING_TOKEN.value,
                    )
                }
            )
        payload = cls.get_refresh_token_payload(refresh_token)
        if payload["type"] != JWT_REFRESH_TYPE:
            raise ValidationError(
                {
                    "refreshToken": ValidationError(
                        "Incorrect refreshToken",
                        code=AccountErrorCode.JWT_INVALID_TOKEN.value,
                    )
                }
            )
        return payload

    @classmethod
    def clean_csrf_token(cls, csrf_token, payload):
        is_valid = _compare_masked_tokens(csrf_token, payload["csrfToken"])
        if not is_valid:
            raise ValidationError(
                {
                    "csrfToken": ValidationError(
                        "Invalid csrf token",
                        code=AccountErrorCode.JWT_INVALID_CSRF_TOKEN.value,
                    )
                }
            )

    @classmethod
    def get_user(cls, payload):
        try:
            user = get_user(payload)
        except ValidationError as e:
            raise ValidationError({"refreshToken": e})
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        refresh_token = cls.get_refresh_token(info, data)
        payload = cls.clean_refresh_token(refresh_token)

        # None when we got refresh_token from cookie.
        if not data.get("refresh_token"):
            csrf_token = data.get("csrf_token")
            cls.clean_csrf_token(csrf_token, payload)

        user = get_user(payload)
        token = create_access_token(user)
        return cls(errors=[], user=user, token=token)


class VerifyToken(BaseMutation):
    """Mutation that confirms if token is valid and also returns user data."""

    user = graphene.Field(User, description="User assigned to token.")
    is_valid = graphene.Boolean(
        required=True,
        default_value=False,
        description="Determine if token is valid or not.",
    )
    payload = GenericScalar(description="JWT payload.")

    class Arguments:
        token = graphene.String(required=True, description="JWT token to validate.")

    class Meta:
        description = "Verify JWT token."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def get_payload(cls, token):
        try:
            payload = get_payload(token)
        except ValidationError as e:
            raise ValidationError({"token": e})
        return payload

    @classmethod
    def get_user(cls, payload):
        try:
            user = get_user(payload)
        except ValidationError as e:
            raise ValidationError({"token": e})
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        token = data["token"]
        payload = cls.get_payload(token)
        user = cls.get_user(payload)
        return cls(errors=[], user=user, is_valid=True, payload=payload)


class DeactivateAllUserTokens(BaseMutation):
    class Meta:
        description = "Deactivate all JWT tokens of the currently authenticated user."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = info.context.user
        user.jwt_token_key = get_random_string()
        user.save(update_fields=["jwt_token_key"])
        return cls()
