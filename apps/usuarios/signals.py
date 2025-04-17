# apps/usuarios/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Usuario, Perfil

@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente cuando se crea un nuevo usuario.
    """
    if created:
        # Verificar si ya existe un perfil para este usuario
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=Usuario)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Asegura que el perfil se guarde cuando se actualiza el usuario.
    """
    try:
        # Intentar acceder al perfil para ver si existe
        perfil = instance.perfil
        perfil.save()
    except Perfil.DoesNotExist:
        # Si no existe, crearlo
        Perfil.objects.create(usuario=instance)