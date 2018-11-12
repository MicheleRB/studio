from django.urls import path

from . import views

from django.conf.urls import url



urlpatterns = [
    path('fattura/<str:id_fattura>/pdf/', views.fattura_pdf, name='fattura_pdf'),
    #path('dashboard/', views.dashboard, name='dashborad'),
    path('', views.report, name='index'),

]
