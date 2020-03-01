from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""
    # TokenAuthentication is required and user must be authenticated
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # data you want to return
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # overwrite queryset - auth required so self.request.user is available
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # hooks into create process - validator serializer will be passed in
    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)
