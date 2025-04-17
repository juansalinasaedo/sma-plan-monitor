from django.core.management.base import BaseCommand
from apps.notificaciones.signals import verificar_medidas_proximas_vencer


class Command(BaseCommand):
    help = 'Verifica medidas próximas a vencer y envía notificaciones'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando verificación de medidas próximas a vencer...'))

        verificar_medidas_proximas_vencer()

        self.stdout.write(self.style.SUCCESS('Verificación completada.'))