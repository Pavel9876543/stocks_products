from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class StockProductSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product'
    )

    product = ProductSerializer(read_only=True)

    class Meta:
        model = StockProduct
        fields = ['product_id', 'product', 'quantity', 'price']



class StockSerializer(serializers.ModelSerializer):
    positions = StockProductSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    # настройте сериализатор для склада

    def create(self, validated_data):
        positions_data = validated_data.pop('positions')
        stock = Stock.objects.create(**validated_data)

        for position in positions_data:
            StockProduct.objects.create(
                stock=stock,
                **position
            )

        return stock

    def update(self, instance, validated_data):
        positions_data = validated_data.pop('positions')
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        for position in positions_data:
            StockProduct.objects.update_or_create(
                stock=instance,
                product=position['product'],
                defaults={
                    'quantity': position['quantity'],
                    'price': position['price']
                }
            )
        return instance

