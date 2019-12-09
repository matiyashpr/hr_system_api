from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserQuerySet(models.QuerySet):
    def is_active(self):
        return self.filter(is_active=True)


class UserManager(BaseUserManager):  # pragma: no cover
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError as e:
            if attr.startswith('__') and attr.endswith('__'):
                raise e
            return getattr(self.get_queryset(), attr, *args)

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    PROFILE_TYPE_ADMIN = 0
    PROFILE_TYPE_CANDIDATE = 10
    PROFILE_TYPE_RECRUITER = 20
    PROFILE_TYPE_CHOICES = (
        (PROFILE_TYPE_ADMIN, 'admin'),  # django admin
        (PROFILE_TYPE_CANDIDATE, 'candidate'),
        (PROFILE_TYPE_RECRUITER, 'recruiter'),
    )

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)
    profile_type = models.SmallIntegerField(choices=PROFILE_TYPE_CHOICES, db_index=True, default=PROFILE_TYPE_ADMIN)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def is_candidate(self):
        return self.profile_type == self.PROFILE_TYPE_CANDIDATE

    @property
    def is_recruiter(self):
        return self.profile_type == self.PROFILE_TYPE_RECRUITER


class Category(models.Model):
    name = models.CharField(max_length=25)


class Candidate(models.Model):
    GENDER_MALE = 10
    GENDER_FEMALE = 20
    GENDER_CHOICES = (
        (GENDER_MALE, 'male'),
        (GENDER_FEMALE, 'female'),
    )
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True, related_name='candidate_profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=50)
    about = models.TextField(blank=True)
    category = models.ManyToManyField(Category, related_name='+')
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, db_index=True, blank=True, null=True)
    city = models.CharField(max_length=25, db_index=True)
    phone = models.CharField(max_length=15)
    in_search = models.BooleanField(default=True)


class Skills(models.Model):
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    years_experience = models.SmallIntegerField()
    details = models.TextField(blank=True)


class Recruiter(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True, related_name='recruiter_profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
