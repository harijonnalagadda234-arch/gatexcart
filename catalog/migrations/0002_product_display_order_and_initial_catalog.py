from django.db import migrations, models
from django.utils.text import slugify


CATEGORIES = [
    "Rice & Grains",
    "Pulses & Dals",
    "Spices & Masalas",
    "Seeds & Nuts",
    "Tamarind",
    "Oil Seeds",
    "Dry Fruits",
    "Flours & Powders",
    "Jaggery & Sweeteners",
    "Herbs & Leaves",
    "Pickles & Pastes",
    "Edible Oils",
    "Tea & Coffee",
    "Other Food Products",
]

PRODUCTS = [
    {
        "name": "Premium Basmati Rice",
        "category": "Rice & Grains",
        "short_description": "Aromatic long-grain rice for international food businesses.",
        "description": "Carefully sourced Indian basmati rice for wholesale and foodservice buyers.",
        "pack_sizes": "5 kg / 10 kg / 25 kg",
        "moq": "As per requirement",
        "display_order": 1,
    },
    {
        "name": "Toor Dal",
        "category": "Pulses & Dals",
        "short_description": "Quality Indian pigeon peas for bulk supply.",
        "description": "A versatile staple sourced for retailers, distributors and foodservice businesses.",
        "pack_sizes": "5 kg / 10 kg / 25 kg",
        "moq": "As per requirement",
        "display_order": 2,
    },
    {
        "name": "Whole Red Chilli",
        "category": "Spices & Masalas",
        "short_description": "Vibrant Indian chillies for trade and food manufacturing.",
        "description": "Whole dried red chillies available in export-ready bulk packaging.",
        "pack_sizes": "1 kg / 5 kg / 25 kg",
        "moq": "As per requirement",
        "display_order": 3,
    },
    {
        "name": "Green Cardamom",
        "category": "Spices & Masalas",
        "short_description": "Fragrant green cardamom for wholesale buyers.",
        "description": "Aromatic Indian green cardamom, with grade and packing options shared on request.",
        "pack_sizes": "1 kg / 5 kg / 25 kg",
        "moq": "As per requirement",
        "display_order": 4,
    },
]


def seed_catalog(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")
    database = schema_editor.connection.alias

    categories = {}
    for order, name in enumerate(CATEGORIES, start=1):
        slug = slugify(name)
        category, _ = Category.objects.using(database).get_or_create(
            name=name,
            defaults={"slug": slug, "sort_order": order, "is_active": True},
        )
        if not category.slug:
            candidate = slug
            suffix = 2
            while Category.objects.using(database).filter(slug=candidate).exclude(pk=category.pk).exists():
                candidate = f"{slug}-{suffix}"
                suffix += 1
            category.slug = candidate
            category.save(using=database, update_fields=["slug"])
        categories[name] = category

    for item in PRODUCTS:
        if not Product.objects.using(database).filter(name=item["name"]).exists():
            slug = slugify(item["name"])
            suffix = 2
            while Product.objects.using(database).filter(slug=slug).exists():
                slug = f"{slugify(item['name'])}-{suffix}"
                suffix += 1
            Product.objects.using(database).create(
                slug=slug,
                name=item["name"],
                category_id=categories[item["category"]].pk,
                short_description=item["short_description"],
                description=item["description"],
                origin="India",
                pack_sizes=item["pack_sizes"],
                moq=item["moq"],
                is_featured=True,
                is_active=True,
                display_order=item["display_order"],
            )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="display_order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="product",
            options={"ordering": ["-is_featured", "display_order", "name"]},
        ),
        migrations.RunPython(seed_catalog, migrations.RunPython.noop),
    ]
