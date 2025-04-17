from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class CustomAuthToken(ObtainAuthToken):
    """
    Vista personalizada para obtener un token de autenticación.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'rol': user.rol if hasattr(user, 'rol') else None,
            'is_admin': user.is_staff,
        })


class LogoutView(APIView):
    """
    Vista para invalidar el token actual (logout).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Eliminar el token del usuario
        try:
            request.user.auth_token.delete()
            return Response({"detail": "Successfully logged out."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)