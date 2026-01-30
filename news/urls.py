from django.urls import path
from . import views

urlpatterns = [
    # صفحات اصلی
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('config/', views.config_view, name='config'),
    path('news/', views.news_view, name='news'),
    path('edit_news/', views.edit_news_view, name='edit_news'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints - همه با اسلش پایانی
    path('api/news/', views.api_get_news, name='api_news'),
    path('api/news/add/', views.api_add_news, name='api_add_news'),
    path('api/news/edit/', views.api_edit_news, name='api_edit_news'),
    path('api/news/delete/', views.api_delete_news, name='api_delete_news'),
    path('api/news/view/', views.api_increment_view, name='api_increment_view'),
    path('api/categories/', views.api_get_categories, name='api_categories'),
    path('api/check-auth/', views.api_check_auth, name='api_check_auth'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/save-config/', views.api_save_config, name='api_save_config'),
    path('api/news/all/', views.api_get_all_news, name='api_all_news'),
]