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

MySQL connections use PyMySQL, avoiding the native client-library build required by `mysqlclient`. Remote MySQL connections use TLS certificate and host verification. TiDB Cloud Serverless uses the bundled ISRG Root X1 certificate; set `DB_SSL_CA` to another CA bundle path (absolute or relative to the project root) if your provider requires a different CA. Local connections to `localhost`, `127.0.0.1` or `::1` do not enable TLS automatically.

## Vercel deployment

The project is configured for Python 3.12. Vercel detects `manage.py` and the configured `WSGI_APPLICATION` automatically. With `STATIC_ROOT` set, Vercel runs `collectstatic` and serves static assets through its CDN. The committed `media/` directory is included in static collection under the `media/` prefix, and `vercel.json` rewrites `/media/*` requests to those CDN assets.

Set the Vercel project Root Directory to the repository root and Production Branch to `main`. Configure `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` for every environment that builds or runs the application. Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for custom domains; Vercel's `VERCEL_URL` is added automatically. `DEBUG` is always disabled when Vercel environment variables are present. `DB_SSL_CA` is optional and overrides the bundled CA path.

The committed catalogue images are read-only deployment assets served from the Vercel CDN; database image names remain relative paths under `MEDIA_ROOT`. Vercel's function filesystem is not persistent storage, so new product/admin uploads made in production will not persist across deployments and are not included in the CDN until committed and redeployed.

## Admin roles

- Super Admin: Django superuser with full permissions.
- GateXKart Admin: staff users assigned to the `GateXKart Admin` group. The setup command grants catalogue, hero-banner and enquiry permissions, but not user or global-permission management.
- Public visitors: can browse, search, filter and submit enquiries; customer registration is not provided.

## Catalogue and enquiries

Create and manage categories and products in Django Admin. Product records include origin, pack sizes, MOQ, active/featured status, image and display order. Additional product photos can be managed as an inline gallery. Active products with images appear in the home-page product section; products and category pages use responsive image cards with a product-labelled placeholder if a media file is missing.

The prepared catalogue can be imported idempotently from `Product_Image_Analysis/catalogue_candidates.csv`. Back up the database before applying the import:

```powershell
python manage.py import_catalogue_images
python manage.py import_catalogue_images --apply
```

The first command validates and reports the import without changing the database. The `--apply` command adds missing categories and products, stores cleaned photos under `MEDIA_ROOT/products/`, and leaves existing catalogue records intact. In development, Django serves media at `MEDIA_URL`; on Vercel, committed media is exposed through the static asset collection and rewrite.

Quote and contact forms validate submissions and store them for staff follow-up. The chatbot uses the existing Django backend and catalogue data. It can answer basic product/category questions and collect product, quantity, destination, name, email and phone to create a quote request. No external AI API or API key is currently required.

## Static assets

The GateXKart wordmark and global-network illustration are original project assets. Representative food and shipping photographs are bundled under `static/images/`; their Unsplash image source IDs are listed in `static/images/ASSET_SOURCES.txt`. These are not GateXKart's original brand or campaign assets. On Vercel, commit approved product photography under `media/` and redeploy; Django Admin uploads are not persisted by the deployment filesystem.

## Production checklist

Set `DEBUG=False`, use a secret key that is not committed to source control, configure production hosts and HTTPS, enable secure cookies, configure email delivery and backups, and add privacy/terms copy appropriate to your business. Review image licensing and confirm that the GateXKart brand name and supplied business contact information are authorized for your use.
