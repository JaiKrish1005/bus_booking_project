from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Bus, Booking
from .forms import UserSignupForm, BookingForm

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'booking/login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserSignupForm()
    return render(request, 'booking/signup.html', {'form': form})

@login_required
def home(request):
    buses = Bus.objects.all().order_by('date', 'time')
    return render(request, 'booking/home.html', {'buses': buses})

@login_required
def bus_list(request):
    buses = Bus.objects.all().order_by('date', 'time')
    return render(request, 'booking/bus_list.html', {'buses': buses})

@login_required
def bus_detail(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    return render(request, 'booking/bus_detail.html', {'bus': bus})

@login_required
def book_ticket(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.bus = bus
            if booking.num_seats <= bus.available_seats:
                bus.available_seats -= booking.num_seats
                bus.save()
                booking.save()
                messages.success(request, 'Booking successful!')
                return redirect('my_bookings')
            else:
                messages.error(request, 'Not enough seats available.')
    else:
        form = BookingForm()
        form.fields['num_seats'].widget.attrs.update({'class': 'form-control'})  # Add Bootstrap class here
    return render(request, 'booking/booking_form.html', {'form': form, 'bus': bus})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    bus = booking.bus
    bus.available_seats += booking.num_seats
    bus.save()
    booking.delete()
    messages.success(request, 'Booking cancelled successfully!')
    return redirect('my_bookings')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')