import os
from decimal import Decimal
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from prices import Money

from ...account import events as account_events
from .. import models
from ..filters import filter_products_by_attributes_values
from ..models import DigitalContentUrl
from ..thumbnails import create_product_thumbnails
from ..utils.attributes import associate_attribute_values_to_instance
from ..utils.costs import get_margin_for_variant
from ..utils.digital_products import increment_download_count


def test_filtering_by_attributes(
    db, color_attribute, size_attribute, category, settings
):
    product_type_a = models.ProductType.objects.create(
        name="New class", slug="new-class1", has_variants=True
    )
    product_type_a.product_attributes.add(color_attribute)
    product_type_b = models.ProductType.objects.create(
        name="New class", slug="new-class2", has_variants=True
    )
    product_type_b.variant_attributes.add(color_attribute)
    product_a = models.Product.objects.create(
        name="Test product a",
        slug="test-product-a",
        product_type=product_type_a,
        category=category,
    )
    models.ProductVariant.objects.create(
        product=product_a, sku="1234", price_amount=Decimal(10)
    )
    product_b = models.Product.objects.create(
        name="Test product b",
        slug="test-product-b",
        product_type=product_type_b,
        category=category,
    )
    variant_b = models.ProductVariant.objects.create(
        product=product_b, sku="12345", price_amount=Decimal(10)
    )
    color = color_attribute.values.first()
    color_2 = color_attribute.values.last()

    # Associate color to a product and a variant
    associate_attribute_values_to_instance(product_a, color_attribute, color)
    associate_attribute_values_to_instance(variant_b, color_attribute, color)

    product_qs = models.Product.objects.all().values_list("pk", flat=True)

    filters = {color_attribute.pk: [color.pk]}
    filtered = filter_products_by_attributes_values(product_qs, filters)
    assert product_a.pk in list(filtered)
    assert product_b.pk in list(filtered)

    associate_attribute_values_to_instance(product_a, color_attribute, color_2)

    filters = {color_attribute.pk: [color.pk]}
    filtered = filter_products_by_attributes_values(product_qs, filters)

    assert product_a.pk not in list(filtered)
    assert product_b.pk in list(filtered)

    filters = {color_attribute.pk: [color_2.pk]}
    filtered = filter_products_by_attributes_values(product_qs, filters)
    assert product_a.pk in list(filtered)
    assert product_b.pk not in list(filtered)

    # Filter by multiple values, should trigger a OR condition
    filters = {color_attribute.pk: [color.pk, color_2.pk]}
    filtered = filter_products_by_attributes_values(product_qs, filters)
    assert product_a.pk in list(filtered)
    assert product_b.pk in list(filtered)

    # Associate additional attribute to a product
    size = size_attribute.values.first()
    product_type_a.product_attributes.add(size_attribute)
    associate_attribute_values_to_instance(product_a, size_attribute, size)

    # Filter by multiple attributes
    filters = {color_attribute.pk: [color_2.pk], size_attribute.pk: [size.pk]}
    filtered = filter_products_by_attributes_values(product_qs, filters)
    assert product_a.pk in list(filtered)


@pytest.mark.parametrize(
    "expected_price, include_discounts",
    [(Decimal("10.00"), True), (Decimal("15.0"), False)],
)
def test_get_price(
    product_type,
    category,
    sale,
    expected_price,
    include_discounts,
    site_settings,
    discount_info,
):
    product = models.Product.objects.create(
        product_type=product_type, category=category,
    )
    variant = product.variants.create(price_amount=15)

    price = variant.get_price(discounts=[discount_info] if include_discounts else [])

    assert price.amount == expected_price


def test_product_get_price_do_not_charge_taxes(product_type, category, discount_info):
    product = models.Product.objects.create(
        product_type=product_type, category=category, charge_taxes=False,
    )
    variant = product.variants.create(price_amount=Decimal(10))

    price = variant.get_price(discounts=[discount_info])

    assert price == Money("5.00", "USD")


def test_digital_product_view(client, digital_content_url):
    """Ensure a user (anonymous or not) can download a non-expired digital good
    using its associated token and that all associated events
    are correctly generated."""

    url = digital_content_url.get_absolute_url()
    response = client.get(url)
    filename = os.path.basename(digital_content_url.content.content_file.name)

    assert response.status_code == 200
    assert response["content-type"] == "image/jpeg"
    assert response["content-disposition"] == 'attachment; filename="%s"' % filename

    # Ensure an event was generated from downloading a digital good.
    # The validity of this event is checked in test_digital_product_increment_download
    assert account_events.CustomerEvent.objects.exists()


@pytest.mark.parametrize(
    "is_user_null, is_line_null", ((False, False), (False, True), (True, True))
)
def test_digital_product_increment_download(
    client,
    customer_user,
    digital_content_url: DigitalContentUrl,
    is_user_null,
    is_line_null,
):
    """Ensure downloading a digital good is possible without it
    being associated to an order line/user."""

    expected_user = customer_user

    if is_line_null:
        expected_user = None
        digital_content_url.line = None
        digital_content_url.save(update_fields=["line"])
    elif is_user_null:
        expected_user = None
        digital_content_url.line.user = None
        digital_content_url.line.save(update_fields=["user"])

    expected_new_download_count = digital_content_url.download_num + 1
    increment_download_count(digital_content_url)
    assert digital_content_url.download_num == expected_new_download_count

    if expected_user is None:
        # Ensure an event was not generated from downloading a digital good
        # as no user could be found
        assert not account_events.CustomerEvent.objects.exists()
        return

    download_event = account_events.CustomerEvent.objects.get()
    assert download_event.type == account_events.CustomerEvents.DIGITAL_LINK_DOWNLOADED
    assert download_event.user == expected_user
    assert download_event.order == digital_content_url.line.order
    assert download_event.parameters == {"order_line_pk": digital_content_url.line.pk}


def test_digital_product_view_url_downloaded_max_times(client, digital_content):
    digital_content.use_default_settings = False
    digital_content.max_downloads = 1
    digital_content.save()
    digital_content_url = DigitalContentUrl.objects.create(content=digital_content)

    url = digital_content_url.get_absolute_url()
    response = client.get(url)

    # first download
    assert response.status_code == 200

    # second download
    response = client.get(url)
    assert response.status_code == 404


def test_digital_product_view_url_expired(client, digital_content):
    digital_content.use_default_settings = False
    digital_content.url_valid_days = 10
    digital_content.save()

    with freeze_time("2018-05-31 12:00:01"):
        digital_content_url = DigitalContentUrl.objects.create(content=digital_content)

    url = digital_content_url.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "price, cost", [(Money("0", "USD"), Money("1", "USD")), (Money("2", "USD"), None)]
)
def test_costs_get_margin_for_variant(variant, price, cost):
    variant.cost_price = cost
    variant.price = price
    assert not get_margin_for_variant(variant)


@patch("threeNineTee.product.thumbnails.create_thumbnails")
def test_create_product_thumbnails(mock_create_thumbnails, product_with_image):
    product_image = product_with_image.images.first()
    create_product_thumbnails(product_image.pk)
    assert mock_create_thumbnails.called_once_with(
        product_image.pk, models.ProductImage, "products"
    )
