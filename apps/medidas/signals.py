from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Medida, LogMedida
from django.contrib.auth import get_user_model

Usuario = get_user_model()

@receiver(post_save, sender=Medida)
def log_medida_save(sender, instance, created, **kwargs):
    if hasattr(instance, '_request_user'): # Check if user is set
        usuario = instance._request_user
        accion = 'crear' if created else 'actualizar'
        LogMedida.objects.create(usuario=usuario, medida=instance, accion=accion)
        
@receiver(post_delete, sender=Medida)
def log_medida_delete(sender, instance, **kwargs):
    if hasattr(instance, '_request_user'):
        usuario = instance._request_user
        LogMedida.objects.create(usuario=usuario, medida=instance, accion='eliminar')