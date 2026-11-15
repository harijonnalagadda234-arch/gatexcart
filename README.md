# GateXKart B2B Marketplace

Django and MySQL storefront for sourcing Indian food products for international business buyers. Public visitors can browse the catalogue and submit quote or contact requests without creating an account.

## Local setup

1. Create a MySQL database with `utf8mb4` support.
2. Activate the existing virtual environment, or create one and install `requirements.txt`.
3. Configure `.env` with a strong `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and the MySQL `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` values.
4. Apply the committed migrations and create the first superuser:

   ```powershell
   python manage.py check
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py setup_gatexkart_roles
   python manage.py runserver
   ```

5. Visit `/` for the storefront and `/django-admin/` for the administration site.

The catalogue migration creates the requested product categories and a small set of editable example products only when matching records do not already exist. Product, category, banner, quote and contact content is stored in MySQL. Uploaded product and category images use Django media storage.

Remote MySQL connections use PyMySQL with TLS certificate and host verification. TiDB Cloud Serverless uses the bundled ISRG Root X1 certificate; set `DB_SSL_CA` to another CA bundle path (absolute or relative to the project root) if your provider requires a different CA. Local connections to `localhost`, `127.0.0.1` or `::1` continue using `mysqlclient` without TLS.

## Admin roles

- Super Admin: Django superuser with full permissions.
- GateXKart Admin: staff users assigned to the `GateXKart Admin` group. The setup command grants catalogue, hero-banner and enquiry permissions, but not user or global-permission management.
- Public visitors: can browse, search, filter and submit enquiries; customer registration is not provided.

## Catalogue and enquiries

Create and manage categories and products in Django Admin. Product records include origin, pack sizes, MOQ, active/featured status, image and display order. Additional product photos can be managed as an inline gallery. Active products with images appear in the home-page product section; products and category pages use responsive image cards with a fallback if a media file is missing.

The prepared catalogue can be imported idempotently from `Product_Image_Analysis/catalogue_candidates.csv`. Back up the database before applying the import:

```powershell
python manage.py import_catalogue_images
python manage.py import_catalogue_images --apply
```

The first command validates and reports the import without changing the database. The `--apply` command adds missing categories and products, stores cleaned photos under `MEDIA_ROOT/products/`, and leaves existing catalogue records intact. In development, Django serves uploads at `MEDIA_URL`; production deployments must configure their web server or object storage to serve media.

Quote and contact forms validate submissions and store them for staff follow-up. The chatbot uses the existing Django backend and catalogue data. It can answer basic product/category questions and collect product, quantity, destination, name, email and phone to create a quote request. No external AI API or API key is currently required.

## Static assets

The GateXKart wordmark and global-network illustration are original project assets. Representative food and shipping photographs are bundled under `static/images/`; their Unsplash image source IDs are listed in `static/images/ASSET_SOURCES.txt`. These are not GateXKart's original brand or campaign assets. Upload approved product photography, category photos and hero banners through Django Admin to replace the representative imagery.

## Production checklist

Set `DEBUG=False`, use a secret key that is not committed to source control, configure production hosts and HTTPS, enable secure cookies, configure email delivery and backups, and add privacy/terms copy appropriate to your business. Review image licensing and confirm that the GateXKart brand name and supplied business contact information are authorized for your use.
