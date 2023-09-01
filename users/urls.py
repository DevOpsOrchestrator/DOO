from django.urls import path, include

from . import views

app_name = 'user'
urlpatterns = [

     # Login/logout
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('password/', views.ChangePasswordView.as_view(), name='alterar_senha'),
    path('api-tokens/', views.TokenListView.as_view(), name='token_list'),
    path('api-tokens/add/', views.TokenCreateView.as_view(), name='token_add'),
    path('api-tokens/<int:pk>/edit/', views.TokenUpdateView.as_view(), name='token_edit'),
    path('api-tokens/<int:pk>/delete/', views.TokenDeleteView.as_view(), name='token_delete'),

]
