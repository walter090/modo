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

    def add_interests(self, user_id, keywords=None, sources=None):
        if sources is None and keywords is None:
            return
        if sources is None:
            sources = []
        if keywords is None:
            keywords = []

        human = self.get(identifier=user_id)
        if 'sources' in human.interests:
            human.interests['sources'] += sources
        else:
            human.interests[sources] = sources

        if 'keywords' in human.interests:
            human.interests['keywords'] += keywords
        else:
            human.interests['keywords'] = keywords

        human.save()

    def add_settings(self, user_id, settings):
        human = self.get(identifier=user_id)

        for setting, value in settings.items():
            human.settings[setting] = value

        human.save()
