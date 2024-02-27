DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),  # noqa: F821
        "USER": os.environ.get("POSTGRES_USER"),  # noqa: F821
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),  # noqa: F821
        "HOST": os.environ.get("DB_HOST"),  # noqa: F821
        "PORT": os.environ.get("DB_PORT"),  # noqa: F821
        "OPTIONS": {"options": "-c search_path=public,content"},
    }
}
