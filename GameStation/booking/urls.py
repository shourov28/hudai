from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('book/<int:game_id>/', views.book_game, name='book_game'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('admin-summary/', views.admin_summary, name='admin_summary'),
    path('renew/<int:booking_id>/', views.renew_booking, name='renew_booking'),
    path('signup/', views.signup, name='signup'),
    path('payment-confirmation/<int:booking_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('login/', auth_views.LoginView.as_view(template_name='booking/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
