from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('otp/send/', SendOTPView.as_view()),
    path('otp/verify/', VerifyOTPView.as_view()),

    path('rides/book/', BookRideView.as_view()),
    path('rides/history/', RideHistoryView.as_view()),
    path('rides/available/', AvailableRidesView.as_view()),
    path('rides/accept/<int:ride_id>/', AcceptRideView.as_view()),
    path('rides/reject/<int:ride_id>/', RejectRideView.as_view()),
    path('rides/feedback/<int:ride_id>/', SubmitRideFeedbackView.as_view()),

    path('location/update/', DriverLocationUpdate.as_view()),
    path('location/<int:driver_id>/', GetDriverLocation.as_view()),

    path('payments/initiate/<int:ride_id>/', CreatePaymentView.as_view()),
    path('payments/confirm/', ConfirmPaymentView.as_view()),
]