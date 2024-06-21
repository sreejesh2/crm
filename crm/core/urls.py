
from django.urls import path
from . import views

urlpatterns = [
   path('login/',views.LoginView.as_view(), name='login'), 
   path('module/list/', views.ModuleListAPIView.as_view(), name='module-list'),

]
