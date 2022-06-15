from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from .models import CustomUser, Follow
from .serializers import FollowSerializer


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для операций с пользователями.
    """
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['POST'], detail=True, permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(CustomUser, id=id)
        if request.user == author:
            return Response(
                {'errors': 'Невозможно подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на данного пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow = Follow.objects.create(user=request.user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(CustomUser, id=id)
        if request.user == author:
            return Response(
                {'errors': 'Невозможно отподписаться от самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow = Follow.objects.filter(user=request.user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на данного пользователя.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=['GET'], detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
