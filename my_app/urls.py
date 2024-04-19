"""
URL configuration for InventoryManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.signup, name='signup'),
    path('admin/', admin.site.urls),
    path('signin', views.signin, name="signin"),
    path('view_inventory', views.view_inventory, name="view_inventory"),
    path('add_item',views.add_item, name= "add_item"),
    path('logout',views.signup, name= "logout"),
    path('create_product', views.create_product, name='create_product'),
    path('editprod/<int:product_id>/', views.editprod, name='editprod'),
    path('product_audit_history/<int:product_id>/', views.product_audit_history, name='product_audit_history'),
    path('delete/<int:product_id>/', views.delprod, name='confirm_delete'),
    path('delprod/<int:product_id>/', views.confirm_delete, name='delprod'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)