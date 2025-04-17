# Generated by Django 5.1.7 on 2025-04-04 21:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auditoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')),
                ('accion', models.CharField(choices=[('creacion', 'Creación'), ('modificacion', 'Modificación'), ('eliminacion', 'Eliminación'), ('login', 'Inicio de sesión'), ('logout', 'Cierre de sesión'), ('exportacion', 'Exportación de datos'), ('importacion', 'Importación de datos'), ('descarga', 'Descarga de archivo'), ('validacion', 'Validación de datos'), ('rechazo', 'Rechazo de datos'), ('planificacion', 'Planificación'), ('configuracion', 'Configuración del sistema')], max_length=20, verbose_name='Acción')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP')),
                ('navegador', models.CharField(blank=True, max_length=255, verbose_name='Navegador')),
                ('datos_adicionales', models.JSONField(blank=True, null=True, verbose_name='Datos adicionales')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auditorias', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Auditoría',
                'verbose_name_plural': 'Auditorías',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='CambioDetalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campo', models.CharField(max_length=100, verbose_name='Campo')),
                ('valor_anterior', models.TextField(blank=True, null=True, verbose_name='Valor anterior')),
                ('valor_nuevo', models.TextField(blank=True, null=True, verbose_name='Valor nuevo')),
                ('auditoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='auditorias.auditoria', verbose_name='Auditoría')),
            ],
            options={
                'verbose_name': 'Detalle de cambio',
                'verbose_name_plural': 'Detalles de cambios',
            },
        ),
        migrations.CreateModel(
            name='ConfiguracionAuditoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auditar_creacion', models.BooleanField(default=True, verbose_name='Auditar creación')),
                ('auditar_modificacion', models.BooleanField(default=True, verbose_name='Auditar modificación')),
                ('auditar_eliminacion', models.BooleanField(default=True, verbose_name='Auditar eliminación')),
                ('campos_auditados', models.JSONField(blank=True, help_text='Lista de campos a auditar. Dejar en blanco para auditar todos los campos.', null=True, verbose_name='Campos auditados')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Tipo de contenido')),
            ],
            options={
                'verbose_name': 'Configuración de auditoría',
                'verbose_name_plural': 'Configuraciones de auditoría',
                'unique_together': {('content_type',)},
            },
        ),
    ]
