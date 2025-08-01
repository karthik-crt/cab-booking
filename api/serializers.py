from rest_framework import serializers
from .models import User, Ride, DriverLocation, Payment, OTP

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id','username','email','password','is_driver']
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = ['user','driver','status','fare','completed','paid','created_at','completed_at']

class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = '__all__'
        read_only_fields = ['driver','updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user','ride','razorpay_order_id','paid']

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)