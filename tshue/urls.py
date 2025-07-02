from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('terms/', views.terms, name='terms'),
    path('homophonic/', views.imik, name='imik'),
    path('subtitle/', views.subtitle, name='subtitle'),
    path('api/translate/', views.translation_proxy, name='translation_proxy'),
]
