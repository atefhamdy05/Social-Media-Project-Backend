from django.urls import path, re_path
from .views import (
    # CustomProviderAuthView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    me,
    get_list,
    get_add_user_dropdowns,
    add_user,
    user_details,
    user_search,
    edit_user,
)
app_name='accounts'

urlpatterns = [
    path('me/', me),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),

    #############################################################

    path("list/", get_list, name="get_list"),
    path("search/", user_search, name="user_search"),
    path("add/", add_user, name="add_user"),
    path("<str:id>/", user_details, name="user_details"),
    path("<str:id>/edit/", edit_user, name="edit_user"),
    path("add/dropdowns/", get_add_user_dropdowns, name="get_add_user_dropdowns"),

]