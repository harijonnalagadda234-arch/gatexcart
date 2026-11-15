import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/".env")
SECRET_KEY=os.getenv("SECRET_KEY","dev-only-change-me")
DEBUG=os.getenv("DEBUG","True").lower()=="true"
ALLOWED_HOSTS=[x.strip() for x in os.getenv("ALLOWED_HOSTS","127.0.0.1,localhost").split(",")]
INSTALLED_APPS=["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","core","catalog","chatbot"]
MIDDLEWARE=["django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF="config.urls"
TEMPLATES=[{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages","core.context_processors.site_settings"]}}]
WSGI_APPLICATION="config.wsgi.application"
DATABASES={"default":{"ENGINE":"django.db.backends.mysql","NAME":os.getenv("DB_NAME","gatexkart"),"USER":os.getenv("DB_USER","root"),"PASSWORD":os.getenv("DB_PASSWORD",""),"HOST":os.getenv("DB_HOST","127.0.0.1"),"PORT":os.getenv("DB_PORT","3306"),"OPTIONS":{"charset":"utf8mb4"}}}
AUTH_PASSWORD_VALIDATORS=[{"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE="en-us"; TIME_ZONE="Asia/Kolkata"; USE_I18N=True; USE_TZ=True
STATIC_URL="static/"; STATICFILES_DIRS=[BASE_DIR/"static"]; STATIC_ROOT=BASE_DIR/"staticfiles"
MEDIA_URL="media/"; MEDIA_ROOT=BASE_DIR/"media"
SITE_FOOTER_PHONE=os.getenv("SITE_FOOTER_PHONE","0096566852921")
SITE_FOOTER_EMAIL=os.getenv("SITE_FOOTER_EMAIL","gatexkartprivatelimited@gmail.com")
SITE_FOOTER_ADDRESS=os.getenv("SITE_FOOTER_ADDRESS","6/64, Near Z P High School Penagalur, Tirupati, Andhra Pradesh, PIN 516127")
SITE_DESIGNER=os.getenv("SITE_DESIGNER","").strip()
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
