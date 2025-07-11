from django.db import models

# Create your models here.
import uuid
import base64
import datetime
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models \
    import BaseUserManager, AbstractBaseUser, PermissionsMixin


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    access_at = models.DateTimeField(
        verbose_name='アクセス時刻',
        default=timezone.now,
    )
    token = models.CharField(
        verbose_name='トークン(sha256)',
        max_length=64,
        default="xxxxxxxxxx",
    )

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    TIMEOUT = datetime.timedelta(minutes=30, seconds=0)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_eid(self):
        sid = str(self.id).replace('-', 'z')
        return base64.b64encode(sid.encode()).decode()

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.email + "/" + str(self.access_at) + "/" + self.token + \
            ("/A" if self.is_admin else "") + \
            ("/S" if self.is_staff else "") + \
            ("/a" if self.is_active else "")

    def get_itemlist(self):
        return (str(self.email), self.access_at, self.token,
                self.is_active, self.is_staff, self.is_admin)
