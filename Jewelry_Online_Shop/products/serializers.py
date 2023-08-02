from rest_framework import serializers
from customers.serializers import CommentSerializer
from .models import Category, Product, Comment

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
