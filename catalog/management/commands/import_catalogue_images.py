import csv
import hashlib
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils.text import slugify

from catalog.image_utils import validate_jpeg_image
from catalog.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Import the reviewed product catalogue and cleaned JPEG images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            default=str(settings.BASE_DIR / "Product_Image_Analysis" / "catalogue_candidates.csv"),
            help="Catalogue CSV path.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write categories, products, and images. Without this flag, only validate and report.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv"]).resolve()
        if not csv_path.is_file():
            raise CommandError(f"Catalogue CSV not found: {csv_path}")

        rows = self._read_rows(csv_path)
        if not rows:
            raise CommandError("The catalogue CSV contains no products.")

        self._validate_rows(rows)
        conflicts = self._find_conflicts(rows)
        if conflicts:
            raise CommandError("Resolve product name/slug conflicts before importing:\n" + "\n".join(conflicts))

        category_names = {row["category"] for row in rows}
        existing_categories = {
            category.name.casefold()
            for category in Category.objects.filter(name__in=category_names)
        }
        missing_categories = sum(name.casefold() not in existing_categories for name in category_names)
        existing_product_count = sum(self._matching_product(row) is not None for row in rows)
        image_count = sum(1 + len(self._additional_paths(row)) for row in rows)

        if not options["apply"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {len(rows)} catalogue rows, {missing_categories} new categories, "
                    f"{len(rows) - existing_product_count} new products, "
                    f"{existing_product_count} existing products reused, {image_count} images."
                )
            )
            self.stdout.write("No database or media files were changed. Re-run with --apply to import.")
            return

        created_categories = 0
        created_products = 0
        reused_products = 0
        assigned_primary_images = 0
        created_gallery_images = 0

        with transaction.atomic():
            categories = {}
            for row in rows:
                category = self._get_or_create_category(row["category"])
                categories[row["category"]] = category
            created_categories = len(
                [name for name in category_names if name.casefold() not in existing_categories]
            )

            for row in rows:
                category = categories[row["category"]]
                product = self._matching_product(row)
                primary_path = self._store_image(row["main_product_image_proposed"])

                if product is None:
                    product = Product.objects.create(
                        category=category,
                        name=row["product_name"],
                        slug=row["slug"],
                        short_description=row["short_description"],
                        description=row["full_description"],
                        origin=row.get("origin", ""),
                        grade=row.get("product_grade", ""),
                        pack_sizes=row.get("available_pack_sizes", ""),
                        moq=row.get("minimum_order_quantity", ""),
                        availability="",
                        image=primary_path,
                        is_featured=False,
                        is_active=True,
                        display_order=int(row["display_order"]),
                    )
                    created_products += 1
                    assigned_primary_images += 1
                else:
                    reused_products += 1
                    if not product.image:
                        product.image = primary_path
                        product.save(update_fields=["image"])
                        assigned_primary_images += 1

                for additional_path in self._additional_paths(row):
                    stored_path = self._store_image(additional_path)
                    _, created = ProductImage.objects.get_or_create(
                        product=product,
                        image=stored_path,
                        defaults={
                            "alt_text": product.name,
                            "display_order": ProductImage.objects.filter(product=product).count() + 1,
                        },
                    )
                    created_gallery_images += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created_products} products and {created_categories} categories; "
                f"reused {reused_products} products; assigned {assigned_primary_images} primary images "
                f"and created {created_gallery_images} gallery images."
            )
        )

    def _read_rows(self, csv_path):
        try:
            with csv_path.open(encoding="utf-8-sig", newline="") as file:
                return list(csv.DictReader(file))
        except (OSError, UnicodeError, csv.Error) as exc:
            raise CommandError(f"Unable to read catalogue CSV: {exc}") from exc

    def _validate_rows(self, rows):
        required = {
            "product_name",
            "slug",
            "category",
            "short_description",
            "full_description",
            "main_product_image_proposed",
            "display_order",
        }
        seen_slugs = set()
        for line_number, row in enumerate(rows, start=2):
            missing = sorted(field for field in required if not row.get(field, "").strip())
            if missing:
                raise CommandError(f"CSV line {line_number} is missing: {', '.join(missing)}")
            slug = row["slug"].strip()
            if slug in seen_slugs:
                raise CommandError(f"Duplicate product slug on CSV line {line_number}: {slug}")
            seen_slugs.add(slug)
            try:
                int(row["display_order"])
            except ValueError as exc:
                raise CommandError(f"Invalid display order on CSV line {line_number}.") from exc
            self._validate_image_path(row["main_product_image_proposed"], line_number)
            for path in self._additional_paths(row):
                self._validate_image_path(path, line_number)

    def _validate_image_path(self, relative_path, line_number):
        path = PurePosixPath(relative_path.replace("\\", "/"))
        if path.is_absolute() or not path.parts or path.parts[0] != "Cleaned_Products":
            raise CommandError(f"CSV line {line_number} image is not under Cleaned_Products.")
        if any(part in {"", ".", ".."} for part in path.parts):
            raise CommandError(f"Unsafe image path on CSV line {line_number}.")

        cleaned_root = (settings.BASE_DIR / "Cleaned_Products").resolve()
        source = (settings.BASE_DIR / Path(*path.parts)).resolve()
        if not source.is_relative_to(cleaned_root) or not source.is_file():
            raise CommandError(f"Cleaned product image not found on CSV line {line_number}: {relative_path}")
        if source.suffix.lower() not in {".jpg", ".jpeg"}:
            raise CommandError(f"Only cleaned JPG/JPEG images can be imported: {relative_path}")
        with source.open("rb") as image_file:
            validate_jpeg_image(File(image_file, name=source.name))

    def _additional_paths(self, row):
        return [
            path.strip()
            for path in row.get("additional_product_images", "").split(";")
            if path.strip()
        ]

    def _find_conflicts(self, rows):
        conflicts = []
        for row in rows:
            category_name = row["category"].casefold()
            by_slug = Product.objects.filter(slug=row["slug"]).select_related("category").first()
            by_name = Product.objects.filter(name__iexact=row["product_name"]).select_related("category")
            if by_slug and (
                by_slug.name.casefold() != row["product_name"].casefold()
                or by_slug.category.name.casefold() != category_name
            ):
                conflicts.append(f"{row['product_name']}: slug {row['slug']} is already used by another product.")
            elif by_name.exclude(category__name__iexact=row["category"]).exists():
                conflicts.append(f"{row['product_name']}: the name already exists in another category.")
        return conflicts

    def _matching_product(self, row):
        product = Product.objects.filter(slug=row["slug"]).select_related("category").first()
        if product:
            return product
        return (
            Product.objects.filter(
                name__iexact=row["product_name"],
                category__name__iexact=row["category"],
            )
            .select_related("category")
            .first()
        )

    def _get_or_create_category(self, name):
        category = Category.objects.filter(name__iexact=name).first()
        if category:
            return category

        base_slug = slugify(name)
        slug = base_slug
        suffix = 2
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        return Category.objects.create(name=name, slug=slug, is_active=True)

    def _store_image(self, relative_path):
        path = PurePosixPath(relative_path.replace("\\", "/"))
        source = (settings.BASE_DIR / Path(*path.parts)).resolve()
        stored_name = f"products/catalogue/{source.name}"
        if default_storage.exists(stored_name):
            if self._storage_digest(stored_name) != self._file_digest(source):
                raise CommandError(f"A different media file already exists at {stored_name}.")
            return stored_name

        with source.open("rb") as image_file:
            saved_name = default_storage.save(stored_name, File(image_file, name=source.name))
        if saved_name != stored_name:
            raise CommandError(f"Media storage changed the requested image path: {stored_name}")
        return saved_name

    def _file_digest(self, path):
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _storage_digest(self, name):
        digest = hashlib.sha256()
        with default_storage.open(name, "rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
