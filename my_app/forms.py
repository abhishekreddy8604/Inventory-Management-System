from django import forms
from .models import ProductModel

class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['product_name', 'description', 'quantity','price', 'image','manager','modified_by' ]
