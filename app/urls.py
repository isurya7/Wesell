from django.urls import path
from . import views
urlpatterns = [
    #navbar
    path("", views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    # profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('edit-profile/<int:customer_id>/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    # cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_Cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('adjust-quantity/<int:item_id>/', views.adjust_quantity, name='adjust_quantity'),
    path('update-size/<int:item_id>/', views.UpdateSizeView.as_view(), name='update_size'),
    # registration
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.RegistrationView.as_view(), name='signup'),
    # wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.RemoveFromWishlist.as_view(), name='remove_from_wishlist'),
    # wishlist to cart
    path('wishlist-to-cart/', views.WishlistToCart.as_view(), name='wishlist_to_cart'),
    #payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    #order
    path('order/',views.order_view,name='orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    #product
    path('category/<slug:val>/', views.category, name='category_view'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    #search
    path('search/',views.search,name='search'),
]

