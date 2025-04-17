from django.shortcuts import render
from rest_framework import viewsets
from .models import Organismo
from .serializers import OrganismoSerializer

# Create your views here.
class OrganismoViewSet(viewsets.ModelViewSet):
    queryset = Organismo.objects.all()
    serializer_class = OrganismoSerializer
