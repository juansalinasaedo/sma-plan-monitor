from rest_framework import serializers
from .models import Usuario  # Importa el nuevo modelo
from apps.organismos.models import Organismo

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type':'password'})
    organismo_id = serializers.PrimaryKeyRelatedField(
        queryset = Organismo.objects.all(), source="organismo", write_only=True
    )
    organismo = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'organismo_id', 'organismo', 'rol']

    """ def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            organismo=validated_data['organismo'],
            rol=validated_data['rol']
        )
        return user """
    
    def create(self, validated_data):
        password = validated_data.pop('password')  # Remove password from validated_data
        user = Usuario.objects.create(**validated_data)  # Create user without password first
        user.set_password(password)  # Hash the password
        user.save()
        return user
