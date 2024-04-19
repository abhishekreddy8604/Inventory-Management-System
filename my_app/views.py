from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import  ProductModel, userModel  # Import the necessary models
from .forms import ProductForm
from django.shortcuts import redirect


def view_inventory(request):
    products = ProductModel.objects.all()
    return render(request, 'inventory.html', {"products": products})


def signup(request):
    return render(request, 'signup.html')



def add_item(request):
    return render(request, 'AddProd.html')



def signin(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "signup":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            
            existing_users = userModel.objects.filter(first_name=first_name, last_name=last_name)
            
            if existing_users.exists():
                # Assuming that user_id is unique, get the user_id of the first user in the QuerySet
                manager_id = existing_users[0].user_id
            else:
                # Create a new user if it doesn't exist
                messages.success(request, f'User not registered please register')
                return render(request, 'signup.html')

            
            showall = ProductModel.objects.all()
            

            return render(request, 'inventory.html', {"products": showall})
    

        
        elif action == "Insert":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            if userModel.objects.filter(first_name=first_name, last_name=last_name).exists():
                messages.error(request, 'User already exists. Please sign in.')
            else:
                if (request.POST.get('first_name') and request.POST.get('last_name')):
                    saverecord = userModel()
                    saverecord.first_name = request.POST.get("first_name")
                    saverecord.last_name = request.POST.get('last_name')
                    saverecord.save()
                    messages.success(request, f'User {saverecord.first_name} is saved successfully.')
        
        elif action == "user_id":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            existing_users = userModel.objects.filter(first_name=first_name, last_name=last_name)
    
            if existing_users.exists():
            # Assuming there's only one matching user, you can retrieve user_id
                user_id = existing_users[0].user_id
                messages.success(request, f'Your user ID is {user_id}')
            else:
                messages.error(request, 'No matching user found, Please Register.')


    return render(request, 'signup.html')




# View for creating a product
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            user_id = request.POST.get('manager')
            user = get_object_or_404(userModel, user_id=user_id)
            
            product = form.save(commit=False)
            product.manager = user
            product.save()

            product.create_audit_entry()
    products = ProductModel.objects.all()

    return render(request, 'inventory.html', {"products": products})




def editprod(request, product_id):
    product = get_object_or_404(ProductModel, pk=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            user_id = request.POST.get('manager')
            user = get_object_or_404(userModel, user_id=user_id)

            product.modified_by = user
            product.save()

            product.create_audit_entry()

            return redirect('view_inventory')  # Redirect to the product list view
    else:
        form = ProductForm(instance=product)
    return render(request, 'editprod.html', {'form': form, 'product': product})



from django.shortcuts import render, redirect
from .models import ProductModel
from django.contrib import messages

def delprod(request, product_id):
    if request.method == "POST":
        manager_id = request.POST.get("manager_id")
        product = get_object_or_404(ProductModel, id=product_id)
        
        if manager_id == str(product.manager.user_id):
            product.delete()
            messages.success(request, 'Product deleted successfully.')
        else:
            messages.error(request, 'Invalid manager ID. Product not deleted.')

    return redirect('view_inventory')








def product_audit_history(request, product_id):
    product = get_object_or_404(ProductModel, pk=product_id)
    audit_entries = product.audits.all()  # Assuming you have defined a related_name 'audits'

    return render(request, 'product_audit_history.html', {'product': product, 'audit_entries': audit_entries})



def confirm_delete(request, product_id):
    product = ProductModel.objects.get(id=product_id)
    return render(request, 'confirm_delete.html', {'product': product})