import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_("full_name"), max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmType(models.TextChoices):
        MOVIE = "MOVIE", _("Movie")
        TV_SHOW = "TV_SHOW", _("TV_Show")

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation_date"), blank=True, null=True)
    rating = models.FloatField(
        _("rating"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")

    type = models.CharField(
        _("type"),
        max_length=255,
        choices=FilmType.choices,
        default=FilmType.MOVIE,
        blank=True,
    )

    genres = models.ManyToManyField(
        Genre, verbose_name=_("genres"), through="GenreFilmwork"
    )
    persons = models.ManyToManyField(
        Person, verbose_name=_("persons"), through="PersonFilmwork"
    )

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("Filmwork")
        verbose_name_plural = _("Filmworks")

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        "Filmwork", on_delete=models.CASCADE, verbose_name=_("Filmwork")
    )
    genre = models.ForeignKey(
        "Genre", on_delete=models.CASCADE, verbose_name=_("Genre")
    )
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'

        constraints = [
            models.constraints.UniqueConstraint(
                fields=["film_work", "genre"], name="film_work_genre_idx"
            ),
        ]

        indexes = [
            models.Index(
                fields=["film_work_id", "genre_id"], name="film_work_genre_idx"
            ),
        ]


class PersonFilmwork(UUIDMixin):
    class PersonRole(models.TextChoices):
        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        WRITER = "writer", _("writer")

    film_work = models.ForeignKey(
        "Filmwork", on_delete=models.CASCADE, verbose_name=_("Filmwork")
    )
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, verbose_name=_("Person")
    )
    role = models.TextField(_("role"), null=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'

        constraints = [
            models.constraints.UniqueConstraint(
                fields=["film_work", "person", "role"], name="film_work_person_role_idx"
            ),
        ]

        indexes = [
            models.Index(
                fields=["film_work_id", "person_id", "role"],
                name="film_work_person_role_idx",
            ),
        ]
