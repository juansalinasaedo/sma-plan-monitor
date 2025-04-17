from rest_framework import serializers
from .models import Medida

class MedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medida
        fields = '__all__'