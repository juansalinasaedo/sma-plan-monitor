from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = 'Genera un token de API para un usuario existente'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username del usuario')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Usuario "{username}" no existe')

        token, created = Token.objects.get_or_create(user=user)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Se ha creado un token para el usuario {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'El usuario {username} ya tenía un token'))

        self.stdout.write(f'Token: {token.key}')