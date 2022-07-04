from itertools import chain
from typing import Optional

import graphene
from django.contrib.auth import models as auth_models
from i18naddress import get_validation_rules

from ...account import models
from ...core.exceptions import PermissionDenied
from ...core.permissions import AccountPermissions
from ...payment import gateway
from ...payment.utils import fetch_customer_id
from ..utils import format_permissions_for_display, get_user_or_app_from_context, requestor_is_superuser
from ..utils.filters import filter_by_query_param
from .types import AddressValidationData, ChoiceValue
from .utils import (
    get_allowed_fields_camel_case,
    get_required_fields_camel_case,
    get_user_permissions,
)

USER_SEARCH_FIELDS = (
    "email",
    "first_name",
    "last_name",
    "default_shipping_address__first_name",
    "default_shipping_address__last_name",
    "default_shipping_address__city",
    "default_shipping_address__country",
)
from ..all_user_authorization import AdminAuthorization,B2BUserAuthorization
from ..core.utils import from_global_id_strict_type

#B2B sub users
def resolve_b2b_sub_users(info):
    if B2BUserAuthorization(info):
        try:
            all_data = models.User.objects.filter(is_b2buser=True,is_active=True)
            return all_data
        except:
            return None

#Sub User Details
def resolve_sub_user_details(info,uid):
    if B2BUserAuthorization(info):
        try:
            uid = from_global_id_strict_type(uid, only_type="SubUserDetail", field="pk") #onlytype me iska type
            all_data = models.User.objects.filter(id=uid)
            return all_data
        except Exception as e:
            return None


#Business Details
def resolve_business_details(info,uid):
    if B2BUserAuthorization(info):
        try:
            uid = from_global_id_strict_type(uid, only_type="SubUserDetail", field="pk") #onlytype me iska type
            all_data = models.User.objects.filter(id=uid)
            return all_data
        except Exception as e:
            return None


def resolve_profile_setup(info,uid):
    if B2BUserAuthorization(info):
        try:
            user_id = from_global_id_strict_type(uid, only_type="SubUserDetail", field="pk")
            all_data = models.User.objects.filter(id=user_id)
            return all_data
        except Exception as e:
            return None

def resolve_artist_social_media_details(info,id):
    if AdminAuthorization(info):
        try:
            all_data = models.SocialMediaLinks.objects.get(id=id)
            return all_data
        except:
            return None


def resolve_all_b2b_user_package_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Package.objects.all()
            return all_data
        except:
            return None

def resolve_get_login_sumaary(info,email):
    if AdminAuthorization(info):
        try:
            user = models.User.objects.get(email=email)
            all_data = models.LoginSummary.objects.filter(user_id=user.id)
            return all_data
        except:
            return None

def resolve_all_staff_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.User.objects.filter(is_staff=True,is_superuser=False,is_active=True)
            return all_data
        except:
            return None

def resolve_all_b2c_user_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.User.objects.filter(is_buyer=True,is_artist=False,is_superuser=False,is_staff=False,is_active=True)
            return all_data
        except:
            return None

def resolve_all_b2b_user_request_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.User.objects.filter(is_artist=False,is_superuser=False,is_staff=False,is_buyer=False,is_b2buser=False,is_active=True)
            return all_data
        except:
            return None


def resolve_all_b2b_user_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.User.objects.filter(is_artist=False,is_superuser=False,is_staff=False,is_buyer=False,is_b2buser=True,is_active=True)
            return all_data
        except:
            return None

def resolve_all_artists_details(info):
    if AdminAuthorization(info):
        try:
            all_data = models.User.objects.filter(is_artist=True,is_buyer=False,is_active=True)
            return all_data
        except:
            return None

def resolve_user_details(info,email,id):
    if AdminAuthorization(info):
        if email:
            try:
                all_data = models.User.objects.filter(email=email)
                return all_data
            except:
                return None
        if id:
            try:
                all_data = models.User.objects.filter(id=id)
                return all_data
            except:
                return None
    
        

def resolve_customers(info, query, **_kwargs):
    qs = models.User.objects.customers()
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=USER_SEARCH_FIELDS
    )
    return qs.distinct()


def resolve_permission_groups(info, **_kwargs):
    return auth_models.Group.objects.all()


def resolve_staff_users(info, query, **_kwargs):
    qs = models.User.objects.staff()
    qs = filter_by_query_param(
        queryset=qs, query=query, search_fields=USER_SEARCH_FIELDS
    )
    return qs.distinct()


def resolve_user(info, id):
    requester = get_user_or_app_from_context(info.context)
    if requester:
        _model, user_pk = graphene.Node.from_global_id(id)
        if requester.has_perms(
            [AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS]
        ):
            return models.User.objects.filter(pk=user_pk).first()
        if requester.has_perm(AccountPermissions.MANAGE_STAFF):
            return models.User.objects.staff().filter(pk=user_pk).first()
        if requester.has_perm(AccountPermissions.MANAGE_USERS):
            return models.User.objects.customers().filter(pk=user_pk).first()
    return PermissionDenied()


def resolve_address_validation_rules(
    info,
    country_code: str,
    country_area: Optional[str],
    city: Optional[str],
    city_area: Optional[str],
):

    params = {
        "country_code": country_code,
        "country_area": country_area,
        "city": city,
        "city_area": city_area,
    }
    rules = get_validation_rules(params)
    return AddressValidationData(
        country_code=rules.country_code,
        country_name=rules.country_name,
        address_format=rules.address_format,
        address_latin_format=rules.address_latin_format,
        allowed_fields=get_allowed_fields_camel_case(rules.allowed_fields),
        required_fields=get_required_fields_camel_case(rules.required_fields),
        upper_fields=rules.upper_fields,
        country_area_type=rules.country_area_type,
        country_area_choices=[
            ChoiceValue(area[0], area[1]) for area in rules.country_area_choices
        ],
        city_type=rules.city_type,
        city_choices=[ChoiceValue(area[0], area[1]) for area in rules.city_choices],
        city_area_type=rules.city_type,
        city_area_choices=[
            ChoiceValue(area[0], area[1]) for area in rules.city_area_choices
        ],
        postal_code_type=rules.postal_code_type,
        postal_code_matchers=[
            compiled.pattern for compiled in rules.postal_code_matchers
        ],
        postal_code_examples=rules.postal_code_examples,
        postal_code_prefix=rules.postal_code_prefix,
    )


def resolve_payment_sources(user: models.User):
    stored_customer_accounts = (
        (gtw.id, fetch_customer_id(user, gtw.id)) for gtw in gateway.list_gateways()
    )
    return list(
        chain(
            *[
                prepare_graphql_payment_sources_type(
                    gateway.list_payment_sources(gtw, customer_id)
                )
                for gtw, customer_id in stored_customer_accounts
                if customer_id is not None
            ]
        )
    )


def prepare_graphql_payment_sources_type(payment_sources):
    sources = []
    for src in payment_sources:
        sources.append(
            {
                "gateway": src.gateway,
                "credit_card_info": {
                    "last_digits": src.credit_card_info.last_4,
                    "exp_year": src.credit_card_info.exp_year,
                    "exp_month": src.credit_card_info.exp_month,
                    "brand": "",
                    "first_digits": "",
                },
            }
        )
    return sources


def resolve_address(info, id):
    user = info.context.user
    app = info.context.app
    _model, address_pk = graphene.Node.from_global_id(id)
    # if app and app.has_perm(AccountPermissions.MANAGE_USERS):
    return models.Address.objects.filter(pk=address_pk).first()
    # if user and not user.is_anonymous:
    #     return user.addresses.filter(id=address_pk).first()
    # return PermissionDenied()


def resolve_permissions(root: models.User):
    permissions = get_user_permissions(root)
    permissions = permissions.order_by("codename")
    return format_permissions_for_display(permissions)
