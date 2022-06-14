from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.expressions import F
from django.db.models.query_utils import Q


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name,
                    last_name, password, **other_fields):
        """
        Создает и сохраняет пользователя с указанным адресом электронной почты,
        логином, именем, фамилией и паролем.
        """
        if not email:
            raise ValueError('Введите email для создания пользователя')
        if not username:
            raise ValueError('Введите username для создания пользователя')
        if not first_name:
            raise ValueError('Введите имя для создания пользователя')
        if not last_name:
            raise ValueError('Введите фамилию для создания пользователя')
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name,
            last_name=last_name, **other_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, first_name,
                         last_name, password, **other_fields):
        """
        Создает и сохраняет суперпользователя с указанным адресом электронной
        почты, логином, именем, фамилией и паролем.
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if not other_fields.get('is_superuser'):
            raise ValueError('Нет доступа')
        if not other_fields.get('is_staff'):
            raise ValueError('Нет доступа')
        return self.create_user(email, username, first_name,
                                last_name, password, **other_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя.
    Поле e-mail используется для логина пользователя.
    Обязательные поля Email, логин, пароль, имя, фамилия.
    """
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Логин пользователя',
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z',)]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Модель подписки текущего пользователя
    на автора рецептов.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = (
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='user_author_can_not_be_equal'
            ),
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_follow'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на автора {self.author}'
