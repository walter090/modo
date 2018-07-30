from django.contrib.auth.base_user import BaseUserManager


class HumanManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **kwargs):

        if not email:
            raise ValueError('Email is required')

        username = username.strip()
        email = self.normalize_email(email)
        human = self.model(email=email, username=username, **kwargs)
        human.set_password(raw_password=password)
        human.save()

        return human

    def create_user(self, username, email, password, **kwargs):
        kwargs.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **kwargs)

    def create_superuser(self, username, email, password, **kwargs):
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)

        if kwargs.get('is_superuser') is not True:
            raise ValueError('The user is not a superuser')

        return self._create_user(username, email, password, **kwargs)
