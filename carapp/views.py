from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient

from carapp.forms import DriverApplicationForm, BookCarForm, NewsletterForm, CarPurchaseForm
from royaladmin.models import Car
from carapp.models import RideHailing, CarBooking
import logging, json


# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    template_name = 'index.html'
    context = {}
    return render(request, template_name, context)

def subscribe_newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for subscribing to our newsletter!")
            return redirect('index')
    else:
        form = NewsletterForm()
    return render(request, 'index.html', {'form': form})

def about(request):
    template_name = 'aboutus.html'
    context = {}
    return render(request, template_name, context)

def apply_as_driver(request):
    if request.method == 'POST':
        form = DriverApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.warning(request, 'Application sent successfully.')
            return redirect('about')  # Redirect after successful form submission
    else:
        form = DriverApplicationForm()

    return render(request, 'driverapp.html', {'form': form})


# Helper function to get MPESA access token
@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body.decode('utf-8'))

            # Extract necessary fields from the response
            transaction_id = data['Body']['stkCallback']['CheckoutRequestID']
            result_code = data['Body']['stkCallback']['ResultCode']
            result_desc = data['Body']['stkCallback']['ResultDesc']

            # Find the booking using transaction_id
            booking = CarBooking.objects.get(transaction_id=transaction_id)

            if result_code == 0:
                # Payment successful
                booking.status = 'Success'
                booking.is_paid = True
            elif result_code == 1032:
                # User cancelled/terminated the transaction
                booking.status = 'Terminated'
            else:
                # Other errors (transaction failed)
                booking.status = 'Failed'

            booking.transaction_time = timezone.now()
            booking.save()

            return JsonResponse({"message": "Callback received successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def book_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()

        # Create and save the booking initially with a "Pending" status
        booking = CarBooking(
            car=car,
            name=name,
            phone_number=phone_number,
            start_date=start_date,
            end_date=end_date,
            status='Pending'  # Default status before payment
        )
        booking.save()

        # Initiate STK Push
        client = MpesaClient()
        amount = int(booking.deposit)  # Assuming deposit is defined in the model
        account_reference = f'CarBooking-{booking.id}'
        transaction_desc = f'Car booking deposit for {car.name}'
        callback_url = 'https://51e-41-90-176-35.ngrok-free.app/carapp/mpesa-callback/'

        response = client.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc,
            callback_url=callback_url
        )

        # Handle response from Mpesa
        if response.response_description == 'Success' and response.redirect_url:
            # If STK push is successful, redirect the user to the payment page
            booking.status = 'Payment Initiated'
            booking.transaction_time = timezone.now()
            booking.save()
            return render(request, 'payment_prompt_sent.html', {
                'booking': booking,
                'phone_number': phone_number,
                'car': car,
                'redirect_url': response.redirect_url  # Include the redirect URL for M-Pesa
            })
        elif response.response_description == 'Terminated':
            # If the user terminated the payment initiation
            booking.status = 'Terminated'
            booking.transaction_time = timezone.now()
            booking.save()
            return render(request, 'payment_failed.html', {
                'message': 'Payment was terminated by the user.',
                'car': car
            })
        else:
            # If failed initiation
            booking.status = 'Failed'
            booking.transaction_time = timezone.now()
            booking.save()
            return render(request, 'payment_failed.html', {
                'message': response.error_message,
                'car': car
            })

    return render(request, 'bookcar.html', {'car': car})

def payment_prompted(request):
    return render(request, "payment_prompt_sent.html")
def payment_terminated(request):
    return render(request, "payment_terminated.html")
def payment_success(request):
    return render(request, "payment_success.html")

def payment_failed(request):
    return render(request, "payment_failed.html")


def book_road_test(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = CarPurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.car = car
            purchase.save()
            messages.success(request, 'Road test booked successfully!')
            return redirect('cardetails') # Redirect to a car detail page
    else:
        form = CarPurchaseForm()

    return render(request, 'book_road_test.html', {'form': form, 'car': car})

def services(request):
    template_name = 'services.html'
    context = {}
    return render(request, template_name, context)

def cardetails(request):
    cars = Car.objects.all()
    template_name = 'cars.html'
    context = {'cars': cars}
    return render(request, template_name, context)


def ridehail(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        pickup_location = request.POST['pickup_location']
        pickup_latitude = request.POST['pickup_latitude']
        pickup_longitude = request.POST['pickup_longitude']
        dropoff_location = request.POST['dropoff_location']
        dropoff_latitude = request.POST['dropoff_latitude']
        dropoff_longitude = request.POST['dropoff_longitude']
        pickup_date = request.POST['pickup_date']
        pickup_time = request.POST['pickup_time']

        RideHailing.objects.create(
            car=car,
            pickup_location=pickup_location,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropoff_location=dropoff_location,
            dropoff_latitude=dropoff_latitude,
            dropoff_longitude=dropoff_longitude,
            pickup_date=pickup_date,
            pickup_time=pickup_time,
        )

        return redirect('cardetails')  # Define this URL for a success message

    return render(request, 'ridehailing.html', {'car': car})