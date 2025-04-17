from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from apps.usuarios.models import Usuario
from apps.usuarios.serializers import UserSerializer
from django.shortcuts import redirect

from django.contrib import messages

class UserViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer
    # Usa autenticación basada en token




from django.shortcuts import redirect
from django.contrib.auth import logout

def manual_logout(request):
    logout(request)
    return redirect('/')  # Redirige a la página de inicio
