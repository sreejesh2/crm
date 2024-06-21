
from django.urls import path
from . import views

urlpatterns = [
   path('login/',views.LoginView.as_view(), name='login'), 
   path('module/list/', views.ModuleListAPIView.as_view(), name='module-list'),
   path('module/create/', views.ModuleCreateAPIView.as_view(), name='module-create'),
   path('module/update/<int:pk>/', views.ModuleUpdateAPIView.as_view(), name='module-update'),

]
