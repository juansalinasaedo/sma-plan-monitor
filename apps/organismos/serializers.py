from rest_framework import serializers
from .models import Organismo

class OrganismoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organismo
        fields = '__all__'