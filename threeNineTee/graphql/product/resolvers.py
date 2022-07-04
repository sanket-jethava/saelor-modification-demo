from django.db.models import Sum

from ...order import OrderStatus
from ...product import models
from ..utils import get_database_id, get_user_or_app_from_context
from ..utils.filters import filter_by_period
from .filters import filter_products_by_stock_availability
from ..all_user_authorization import AdminAuthorization

def resolve_all_categories(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Category.objects.all()
            return all_data
        except:
            return None

def resolve_all_categories_name(info):
    if AdminAuthorization(info):
        try:
            all_data = models.Category.objects.filter(level__lt=2)
            return all_data
        except:
            return None

def resolve_attributes(info, qs=None, **_kwargs):
    if AdminAuthorization(info):
        try:
            requestor = get_user_or_app_from_context(info.context)
            qs = qs or models.Attribute.objects.get_visible_to_user(requestor)
            return qs.distinct()
        except:
            return None

def resolve_attribute_values(info, qs=None, **_kwargs):
    if AdminAuthorization(info):
        try:
            requestor = get_user_or_app_from_context(info.context)
            qs = qs or models.AttributeValue.objects.get_visible_to_user(requestor)
            return qs.distinct()
        except:
            return None

def resolve_category_by_slug(slug):
    return models.Category.objects.filter(slug=slug).first()


def resolve_categories(info, level=None, **_kwargs):
    if AdminAuthorization(info):
        qs = models.Category.objects.prefetch_related("children")
        if level is not None:
            qs = qs.filter(level=level)
        return qs.distinct()


def resolve_collection_by_slug(info, slug):
    if AdminAuthorization(info):
        requestor = get_user_or_app_from_context(info.context)
        return (
            models.Collection.objects.visible_to_user(requestor).filter(slug=slug).first()
        )


def resolve_collections(info, **_kwargs):
    if AdminAuthorization(info):
        user = info.context.user
        return models.Collection.objects.visible_to_user(user)


def resolve_digital_contents(info):
    if AdminAuthorization(info):
        return models.DigitalContent.objects.all()


def resolve_product_by_slug(info, slug):
    if AdminAuthorization(info):
        requestor = get_user_or_app_from_context(info.context)
        return models.Product.objects.visible_to_user(requestor).filter(slug=slug).first()


def resolve_products(info, stock_availability=None, **_kwargs):
    if AdminAuthorization(info):
        user = get_user_or_app_from_context(info.context)
        qs = models.Product.objects.visible_to_user(user)

        if stock_availability:
            qs = filter_products_by_stock_availability(qs, stock_availability)

        if not qs.user_has_access_to_all(user):
            qs = qs.exclude(visible_in_listings=False)

        return qs.distinct()


def resolve_product_types(info, **_kwargs):
    if AdminAuthorization(info):
        return models.ProductType.objects.all()


def resolve_product_variant_by_sku(info, sku):
    if AdminAuthorization(info):
        requestor = get_user_or_app_from_context(info.context)
        visible_products = models.Product.objects.visible_to_user(requestor).values_list(
            "pk", flat=True
        )
        return (
            models.ProductVariant.objects.filter(product__id__in=visible_products)
            .filter(sku=sku)
            .first()
        )


def resolve_product_variants(info, ids=None):
    if AdminAuthorization(info):
        user = get_user_or_app_from_context(info.context)

        visible_products = models.Product.objects.visible_to_user(user).values_list(
            "pk", flat=True
        )
        if not visible_products.user_has_access_to_all(user):
            visible_products = visible_products.exclude(visible_in_listings=False)

        qs = models.ProductVariant.objects.filter(product__id__in=visible_products)
        if ids:
            db_ids = [get_database_id(info, node_id, "ProductVariant") for node_id in ids]
            qs = qs.filter(pk__in=db_ids)

        return qs


def resolve_report_product_sales(period):
        qs = models.ProductVariant.objects.all()

        # exclude draft and canceled orders
        exclude_status = [OrderStatus.DRAFT, OrderStatus.CANCELED]
        qs = qs.exclude(order_lines__order__status__in=exclude_status)

        # filter by period
        qs = filter_by_period(qs, period, "order_lines__order__created")

        qs = qs.annotate(quantity_ordered=Sum("order_lines__quantity"))
        qs = qs.filter(quantity_ordered__isnull=False)
        return qs.order_by("-quantity_ordered")
