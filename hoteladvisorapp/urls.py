from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('change_password/', change_password, name='change_password'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    # path('hotel/<int:pk>/', hotel_detail, name='hotel_detail'),
    path('hotel/<int:hotel_id>/', hotel_detail, name='hotel_detail'),
    path('hotel/<int:hotel_id>/book/', book_hotel, name='book_hotel'),
    # path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('book_hotel/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('add_hotel/', add_hotel, name='add_hotel'),
    path('delete_hotel/<int:hotel_id>/', delete_hotel, name='delete_hotel'),
    path('delete_review/<int:review_id>/', delete_review, name='delete_review'),
]