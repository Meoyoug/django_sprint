from django.urls import path
from restaurants import views

urlpatterns = [
    path('', views.RestaurantListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', views.RestaurantDetailAPIView.as_view(), name='detail'),
    path('menu/', views.MenuCreateAPIView.as_view(), name='menu-create'),
    path('menu/<int:pk>/delete', views.MenuDeleteAPIView.as_view(), name='menu-delete'),
]
