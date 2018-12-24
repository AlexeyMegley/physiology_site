from django.urls import path

from . import views

app_name = 'store'
urlpatterns = [
    path('', views.index, name='index'),
    path('subsection/<int:pk>/', views.show_subsection, name='subsection'),
    path('theme/<int:pk>/', views.show_theme, name='theme')
]