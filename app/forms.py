from django import forms
from django.contrib.auth.models import User
from .models import Customer,Order,Product

class CustomerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2
    

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class Customerprofileform(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(Customerprofileform, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Customer
        fields = ['name', 'locality', 'city', 'mobile', 'zipcode', 'state']
        widgets = {
            'name': forms.TextInput(),
            'locality': forms.TextInput(),
            'city': forms.TextInput(),
            'mobile': forms.NumberInput(),
            'zipcode': forms.NumberInput(),
            'state': forms.Select(),  # Use Select for dropdown
        }

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'autofocus': True, 'autocomplete': 'current-password', 'class': 'form-control'}))
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password do not match.")
        
class WishlistForm(forms.Form):
    size = forms.CharField(max_length=10)
    quantity = forms.IntegerField(min_value=1, initial=1)


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'locality', 'city', 'zipcode', 'state', 'mobile']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['number', 'address', 'pincode', 'state', 'mode_of_payment']
        labels = {
            'address': 'Address',
            'pincode': 'Pincode',
            'state': 'State',
            'number': 'Mobile Number',
            'mode_of_payment': 'Mode of Payment'
        }
        widgets = {
            'mode_of_payment': forms.Select(choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')])
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'selling_price', 'discount_price', 'product_image', 'description', 'category']