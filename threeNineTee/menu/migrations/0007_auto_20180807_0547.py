# Generated by Django 2.0.3 on 2018-08-07 10:47
import json

from django.contrib.postgres import fields
from django.db import migrations

from threeNineTee.page.models import Page
from threeNineTee.product.models import Category, Collection


def get_linked_object_kwargs(object):
    return {"pk": object.pk, "slug": object.slug}


def get_linked_object_url(menu_item):
    if menu_item.category:
        return Category(
            **get_linked_object_kwargs(menu_item.category)
        ).get_absolute_url()
    elif menu_item.collection:
        return Collection(
            **get_linked_object_kwargs(menu_item.collection)
        ).get_absolute_url()
    elif menu_item.page:
        return Page(**get_linked_object_kwargs(menu_item.page)).get_absolute_url()
    return None


def get_menu_item_as_dict(menu_item):
    data = {}
    object_url = get_linked_object_url(menu_item) or menu_item.url

    data["url"] = object_url
    data["name"] = menu_item.name
    data["translations"] = {
        translated.language_code: {"name": translated.name}
        for translated in menu_item.translations.all()
    }
    return data


def get_menu_as_json(menu):
    """Build Tree-like JSON structure from the top menu.

    From the top menu items, its children and its grandchildren.
    """
    top_items = menu.items.filter(parent=None)
    menu_data = []
    for item in top_items:
        top_item_data = get_menu_item_as_dict(item)
        top_item_data["child_items"] = []
        children = item.children.all()
        for child in children:
            child_data = get_menu_item_as_dict(child)
            grand_children = child.children.all()
            grand_children_data = [
                get_menu_item_as_dict(grand_child) for grand_child in grand_children
            ]
            child_data["child_items"] = grand_children_data
            top_item_data["child_items"].append(child_data)
        menu_data.append(top_item_data)
    return json.dumps(menu_data)


def update_menus(apps, schema_editor):
    Menu = apps.get_model("menu", "Menu")
    menus = Menu.objects.all()
    for menu in menus:
        menu.json_content = get_menu_as_json(menu)
        menu.save(update_fields=["json_content"])


class Migration(migrations.Migration):

    dependencies = [("menu", "0006_auto_20180803_0528")]

    operations = [
        migrations.AlterField(
            model_name="menu",
            name="json_content",
            field=fields.JSONField(blank=True, default=dict),
        ),
        migrations.RunPython(update_menus, migrations.RunPython.noop),
    ]
