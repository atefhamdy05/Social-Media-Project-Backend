from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from django.db.models import Q
from .models import User, Role
from .forms import user_form
from project.helper import paginate_query_set_list
from datetime import datetime, timezone
from .permissions import permission_allowed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.utils.translation import gettext as _
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from .serializers import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user_serial = UserSerial(request.user)
    
    
    if not user_serial.data:
        return Response(
            data={'error':_('no user data exists')},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        data=user_serial.data,
        status=status.HTTP_200_OK
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer    # ✅

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                key='access',
                value=access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                path=settings.AUTH_COOKIE_PATH,
            )
            response.set_cookie(
                key='refresh',
                value=refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                path=settings.AUTH_COOKIE_PATH,
            )

            

        return response


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        # جهّز data كنسخة قابلة للتعديل
        try:
            data = request.data.copy()
        except Exception:
            data = dict(request.data) if isinstance(request.data, dict) else {}

        if refresh_token and not data.get('refresh'):
            data['refresh'] = refresh_token

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data  # يحتوي على 'access' وربما 'refresh' لو ROTATE_REFRESH_TOKENS=True

        access = validated.get('access')
        new_refresh = validated.get('refresh')  # موجود لو السيرفر أعاد refresh جديد

        response = Response(validated, status=status.HTTP_200_OK)

        # ضع الـ access cookie
        response.set_cookie('access', access,
            max_age=getattr(settings, 'AUTH_COOKIE_MAX_AGE', 60*60*24*3),
            secure=getattr(settings, 'AUTH_COOKIE_SECURE', False),
            httponly=getattr(settings, 'AUTH_COOKIE_HTTP_ONLY', True),
            samesite=getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax'),
            path=getattr(settings, 'AUTH_COOKIE_PATH', '/'),
        )

        # لو السيرفر أعاد refresh جديد (ROTATE_REFRESH_TOKENS=True) عَيّنّه في الكوكي أيضاً
        if new_refresh:
            response.set_cookie('refresh', new_refresh,
                max_age=getattr(settings, 'AUTH_COOKIE_MAX_AGE', 60*60*24*7),
                secure=getattr(settings, 'AUTH_COOKIE_SECURE', False),
                httponly=getattr(settings, 'AUTH_COOKIE_HTTP_ONLY', True),
                samesite=getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax'),
                path=getattr(settings, 'AUTH_COOKIE_PATH', '/'),
            )

        return response



class CustomTokenVerifyView(TokenVerifyView):
    serializer_class = TokenVerifySerializer

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        # جهّز data قابل للتعديل
        try:
            data = request.data.copy()
        except Exception:
            data = dict(request.data) if isinstance(request.data, dict) else {}

        if access_token and not data.get('token'):
            data['token'] = access_token

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)



@permission_classes([AllowAny])
class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response





############################ - USER MODULE - #################################

@api_view(['GET',])
@permission_allowed('permissions.users.view')
def get_list(request):
    if 'filter' in request.GET:
        users       = User.objects.order_by('created_at').filter(Q(full_name__contains=request.GET.get('filter', None))|Q(username__contains=request.GET.get('filter', None)))
        
    else:
        users       = User.objects.order_by('created_at').select_related('role').all()
    
    data            = paginate_query_set_list(users, request.GET,serializer=ListUserSerial)


    return Response(
        
           
        data, 
        status=status.HTTP_200_OK
    )



@api_view(['GET',])
@permission_allowed('permissions.users.view')
def user_details(request, id):
    user = User.objects.select_related('role').filter(id=id).first()
    if not user:
        return Response(data={
                'message': _("this user doesn't exist or has been deleted")
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    user_serial     = DetailedUserSerial(user)
    return Response(
        {
            'user': user_serial.data,
        }, 
        status=status.HTTP_200_OK
    )


@api_view(['GET',])
@permission_allowed('permissions.users.add')
def get_add_user_dropdowns(request):
    roles       = list(Role.objects.order_by('name').values('id', 'name'))


    return Response(
        {
            'roles':roles,
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST',])
@permission_allowed('permissions.users.add')
def add_user(request):
    form = user_form(data=request.POST)
    if form.is_valid():
        form.save()

        return Response({
                'message': f'{_('user')} "{request.POST['full_name']}" {_('added successfully')}'
            },
            status=status.HTTP_201_CREATED
        )
    return Response({
            'errors': form.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['PUT',])
@permission_allowed('permissions.users.edit')
def edit_user(request, id):
    user = User.objects.filter(id=id).first()
    if not user:
        return Response({
                'message': _("this user doesn't exist or has been deleted")
            },
            status=status.HTTP_404_NOT_FOUND
        )
    form = user_form(data=request.POST, instance=user)
    if form.is_valid():
        form            = form.save(created_by=request.user)
        form.updated_by = request.user
        form.updated_at = datetime.now(tz=timezone.utc)

        form.save()

        return Response({
                'message': f'user "{request.POST['full_name']}" updated successfully'
            },
            status=status.HTTP_201_CREATED
        )
    return Response({
        'errors': form.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )



@api_view(['GET',])
@permission_allowed('permissions.users.view')
def user_search(request):
    if 'query' not in request.GET:
        return Response({'error':_('you should enter a valid search value')})
    query   = request.GET['query']
    exclude = request.GET.get('exclude', None)

    users = User.objects.filter(
            Q(full_name__contains=query)|Q(username__contains=query)
        )
    if exclude:
        users = users.exclude(id=exclude)
    
    
    # users_serial = IncludedUserSerial(users.order_by('full_name'), many=True)

    users_list = list(users.order_by('full_name').values('id', 'username', 'full_name'))
    
    return Response(
        data={'users': users_list},
        status=status.HTTP_200_OK
    )

##############################################################################

