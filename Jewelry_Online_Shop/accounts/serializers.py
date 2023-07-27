from rest_framework import serializers
from .models import Account


class RegisterSerializers(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Account
        fields = ('phone_number', 'full_name', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        del validated_data['password2']
        return Account.objects.create_user(**validated_data)

    def validate_username(self, value):
        if value == 'admin':
            raise serializers.ValidationError('user cant be admin')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('password must match')
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= Account
        fields = '__all__'