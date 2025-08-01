from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.utils import timezone
from .models import *
from .serializers import *
import razorpay
from django.conf import settings

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user, _ = User.objects.get_or_create(email=email, username=email)
        code = f"{random.randint(100000,999999)}"
        OTP.objects.create(user=user, code=code)
        send_mail("Your OTP", f"OTP: {code}", 'no-reply@cabapp.com', [email])
        return Response({"message": "OTP sent"})

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        user = User.objects.get(email=email)
        otp = OTP.objects.filter(user=user, code=code, is_used=False).latest('created_at')
        if not otp.is_valid():
            return Response({"error": "OTP expired or invalid"}, status=400)
        otp.is_used = True
        otp.save()
        token = RefreshToken.for_user(user)
        return Response({"access": str(token.access_token), "refresh": str(token)})

class BookRideView(generics.CreateAPIView):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RideHistoryView(generics.ListAPIView):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_driver:
            return Ride.objects.filter(driver=self.request.user)
        return Ride.objects.filter(user=self.request.user)

class AvailableRidesView(generics.ListAPIView):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Ride.objects.filter(status='pending')

class AcceptRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, ride_id):
        ride = Ride.objects.get(id=ride_id, status='pending')
        ride.status = 'accepted'
        ride.driver = request.user
        ride.save()
        return Response({"message": "Ride accepted"})

class DriverLocationUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        loc, _ = DriverLocation.objects.get_or_create(driver=request.user)
        loc.latitude = request.data.get('latitude')
        loc.longitude = request.data.get('longitude')
        loc.save()
        return Response({"message": "Location updated"})

class GetDriverLocation(APIView):
    def get(self, request, driver_id):
        loc = DriverLocation.objects.get(driver_id=driver_id)
        return Response({"lat": loc.latitude, "lng": loc.longitude})

class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, ride_id):
        ride = Ride.objects.get(id=ride_id, user=request.user)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        order = client.order.create({"amount": int(ride.fare * 100), "currency": "INR", "payment_capture": 1})
        Payment.objects.create(user=request.user, ride=ride, razorpay_order_id=order['id'])
        return Response(order)

class ConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        data = request.data
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        payment = Payment.objects.get(razorpay_order_id=data['razorpay_order_id'])
        payment.razorpay_payment_id = data['razorpay_payment_id']
        payment.razorpay_signature = data['razorpay_signature']
        payment.paid = True
        payment.save()
        ride = payment.ride
        ride.paid = True
        ride.completed = True
        ride.completed_at = timezone.now()
        ride.save()
        return Response({"message": "Payment confirmed"})
    
class RejectRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]
 
    def post(self, request, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id, status='pending')
        except Ride.DoesNotExist:
            return Response({"error": "Ride not found or already accepted/rejected."}, status=404)
 
        # Optional: Mark this ride as rejected (or simply leave as pending for next driver)
        ride.status = 'pending'  # Still pending, just rejected by this driver
        ride.save()
 
        # Send notification to rider
        Notification.objects.create(
            user=ride.user,
            title='Ride Rejected',
            message=f'Your ride to {ride.drop} was rejected by {request.user.username}. Searching for another driver...'
        )
 
        return Response({"message": "Ride rejected, rider notified."})
