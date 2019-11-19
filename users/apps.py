from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):## Importing signals inorder for the user->profile signals work
        import users.signals
