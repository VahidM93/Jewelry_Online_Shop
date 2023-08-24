from rest_framework import serializers
from accounts.models import Account
from customers.models import Customer, Address
from orders.models import Order, OrderItem
from products.models import Product, Category, Comment


# --------------------- accounts app ---------------------
class RegisterSerializers(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Account
        fields = ('phone_number', 'full_name', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},# ```write only means it just can be write and it is 
            #possible to read due to security  
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

class ProfileUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'user', 'gender', 'age', 'image')
# --------------------- customers app ---------------------
class AddressSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'customer', 'city', 'body', 'postal_code')


# --------------------- product app ---------------------

class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'is_sub', 'sub_categories')

    def get_sub_categories(self, obj):
        return CategorySerializer(obj.scategory.all(), many=True).data


class ProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = (
                'id', 'name', 'slug', 'image', 'description', 'price_no_discount', 'discount', 'price', 'is_available')


class ProductDetailSerializer(serializers.ModelSerializer):
        category = serializers.StringRelatedField(read_only=True, many=True)
        properties = serializers.StringRelatedField(read_only=True, many=True)
        comments = serializers.SerializerMethodField()

        class Meta:
            model = Product
            fields = (
            'id', 'name', 'category', 'properties', 'slug', 'image', 'description',
            'price_no_discount', 'discount', 'price', 'is_available', 'comments')

        def get_comments(self, obj):
            return CommentSerializer(obj.pcomments.all(), many=True).data


class CommentSerializer(serializers.ModelSerializer):
        customer = serializers.StringRelatedField(read_only=True)
        product = serializers.StringRelatedField(read_only=True)

        class Meta:
            model = Comment
            fields = ('id', 'product', 'customer', 'title', 'body', 'created')

class QuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value < 1 or value > 2:
            raise serializers.ValidationError("Quantity must be greater than 0 and lower than 3")
        return value

# --------------------- orders app ---------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = serializers.SerializerMethodField()
    code = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = (
            "id", "customer", "is_paid", "discount", "city", "body", "postal_code", "phone_number", "status", "coupon",
            "code", "transaction_code", "items",
        )

    def get_items(self, obj):
        items = obj.items.all()
        return OrderItemSerializer(instance=items, many=True).data

class CustomerUnpaidOrdersSerializer(serializers.ModelSerializer):
    unpaid_orders = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('unpaid_orders',)

    def get_unpaid_orders(self, obj):
        if obj:
            unpaid_orders = obj.orders.filter(is_paid=False)
            result = OrderSerializer(unpaid_orders, many=True).data
        else:
            result = {'unpaid_orders': None}
        return result
