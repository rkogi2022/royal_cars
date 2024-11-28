from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from carapp.models import DriverApplication, CarBooking, Newsletter, RideHailing, CarPurchase
from .models import Car, Staff
from .forms import CarForm, StaffForm


# Retrieve and display all cars
def car_list(request):
    cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})

# Add a new car
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('car_list')
    else:
        form = CarForm()
    return render(request, 'car_form.html', {'form': form})

# Edit an existing car
def car_edit(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_list')
    else:
        form = CarForm(instance=car)
    return render(request, 'car_form.html', {'form': form})

# Delete a car
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        return redirect('car_list')
    return render(request, 'car_confirm_delete.html', {'car': car})

def driver_applications(request):
    applications = DriverApplication.objects.all()
    return render(request, 'driver_applications.html', {'applications': applications})

# Car Booking View
def car_bookings(request):
    bookings = CarBooking.objects.all()
    return render(request, 'car_bookings.html', {'bookings': bookings})

def purchase_list(request):
    purchases = CarPurchase.objects.all().select_related('car')  # Fetch all purchases with car details
    template_name = 'purchase_list.html'
    context = {'purchases': purchases}
    return render(request, template_name, context)

# Newsletter View
def newsletter_list(request):
    subscribers = Newsletter.objects.all()
    return render(request, 'newsletter_list.html', {'subscribers': subscribers})

# Ride Hailing View
def ride_hailing_list(request):
    rides = RideHailing.objects.all()
    return render(request, 'ride_hailing_list.html', {'rides': rides})

# View all staff members
def staff_list(request):
    staff_members = Staff.objects.all()
    return render(request, 'staff_list.html', {'staff_members': staff_members})

# Add a new staff member
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member added successfully.')
            return redirect('staff_list')
    else:
        form = StaffForm()
    return render(request, 'staff_form.html', {'form': form})

# Edit staff member details
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff details updated successfully.')
            return redirect('staff_list')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff_form.html', {'form': form})

# Delete a staff member
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff member deleted successfully.')
        return redirect('staff_list')
    return render(request, 'staff_confirm_delete.html', {'staff': staff})
