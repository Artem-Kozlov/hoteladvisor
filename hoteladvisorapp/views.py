from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .forms import SignUpForm, CustomAuthenticationForm, EditProfileForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
import logging
from django.shortcuts import render, get_object_or_404
from .models import Hotel, Review, Booking
from .forms import ReviewForm, BookingForm, HotelSearchForm, HotelForm
from django.core.mail import send_mail
from django.conf import settings



# Настройка логирования
logger = logging.getLogger(__name__)

@login_required
def change_password(request):
    if request.method == 'POST':
        logger.debug('Received POST request for password change')  # Debug message
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Обновление сессии, чтобы не разлогинивало пользователя
            logger.debug('Password change successful')  # Debug message
            return JsonResponse({'success': True})
        else:
            errors = {field: [error['message'] for error in error_list] for field, error_list in form.errors.get_json_data().items()}
            logger.debug('Form errors: %s', errors)  # Debug message
            return JsonResponse({'success': False, 'errors': errors})
    logger.debug('Invalid request method: %s', request.method)  # Debug message
    return JsonResponse({'success': False, 'errors': 'Invalid request'})

def home(request):
    hotels = Hotel.objects.all()
    form = HotelSearchForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['name']:
            hotels = hotels.filter(name__icontains=form.cleaned_data['name'])
        if form.cleaned_data['location']:
            hotels = hotels.filter(location__icontains=form.cleaned_data['location'])
        if form.cleaned_data['min_rating']:
            hotels = hotels.filter(rating__gte=form.cleaned_data['min_rating'])
        if form.cleaned_data['max_price']:
            hotels = hotels.filter(price_per_night__lte=form.cleaned_data['max_price'])

    return render(request, 'home.html', {'hotels': hotels, 'form': form})

def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    return render(request, 'hotel_detail.html', {'hotel': hotel})

def about(request):
    return render(request, 'about.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Загрузка профиля пользователя, созданного сигналом
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Неправильное имя пользователя или пароль")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = {field: [error['message'] for error in error_list] for field, error_list in form.errors.get_json_data().items()}
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request'})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    reviews = hotel.reviews.all()
    if request.method == 'POST':
        if 'start_date' in request.POST and 'end_date' in request.POST:
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.hotel = hotel
                booking.save()
                return redirect('profile')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.hotel = hotel
                review.save()
                return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = ReviewForm()
    return render(request, 'hotel_detail.html', {'hotel': hotel, 'reviews': reviews, 'form': form})

@login_required
def book_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.save()
            send_mail(
                'Бронирование подтверждено',
                f'Ваше бронирование в {hotel.name} с {booking.start_date} по {booking.end_date} подтверждено.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            return redirect('profile')
    return redirect('hotel_detail', hotel_id=hotel_id)

# @login_required
# def delete_booking(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)
#     booking.delete()
#     return redirect('profile')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()

    # Отправка email после отмены бронирования
    send_mail(
        'Отмена бронирования',
        f'Ваше бронирование в отеле {booking.hotel.name} с {booking.start_date} по {booking.end_date} было отменено.',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )

    return redirect('profile')

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_hotel(request):
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_hotel(request, hotel_id):
    if request.method == 'POST':
        try:
            hotel = Hotel.objects.get(id=hotel_id)
            hotel.delete()
            return JsonResponse({'success': True})
        except Hotel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Отель не найден'}, status=404)
    return JsonResponse({'success': False}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
        review.delete()
        return JsonResponse({'success': True})
    except Review.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Review not found'})