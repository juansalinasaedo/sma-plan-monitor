from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permite acceso solo a usuarios superadmin.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'is_superadmin') and request.user.is_superadmin


class IsAdminSMA(permissions.BasePermission):
    """
    Permite acceso solo a usuarios admin_sma.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'is_admin_sma') and request.user.is_admin_sma


class IsOrganismoMember(permissions.BasePermission):
    """
    Permite acceso solo a usuarios de organismos.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'is_organismo') and request.user.is_organismo


class IsOrganismoOwner(permissions.BasePermission):
    """
    Permite modificar solo objetos pertenecientes al organismo del usuario.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not hasattr(request.user, 'organismo'):
            return False

        # Si el objeto tiene un campo organismo directamente
        if hasattr(obj, 'organismo'):
            return obj.organismo == request.user.organismo

        # Para RegistroAvance y otras relaciones
        if hasattr(obj, 'organismo_id'):
            return obj.organismo_id == request.user.organismo.id

        return False


class IsPublicEndpoint(permissions.BasePermission):
    """
    Permite acceso a endpoints públicos sin autenticación.
    """

    def has_permission(self, request, view):
        return True