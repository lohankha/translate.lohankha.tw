from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'terms/', views.terms, name='terms'),
    url(r'homophonic/', views.imik, name='imik'),
    url(r'subtitle/', views.subtitle, name='subtitle'),
]


