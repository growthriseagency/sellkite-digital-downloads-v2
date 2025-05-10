from django.shortcuts import render
from shopify_auth.decorators import login_required
from django.conf import settings # To access SHOPIFY_APP_API_KEY for an example API call

# Import shopify an pyactiveresource for making API calls
import shopify
import pyactiveresource.connection

@login_required
def home(request, *args, **kwargs):
    shop_url = request.user.myshopify_domain
    access_token = request.user.token # This is the Shopify access token

    products = []
    shop_details = None
    error_message = None

    # Example: Making a Shopify API call to get shop details and products
    # The `with request.user.session:` block activates the Shopify API session for the current user
    try:
        with request.user.session:
            # Get shop details
            shop_details = shopify.Shop.current()
            
            # Get a list of products (limit to 5 for this example)
            products = shopify.Product.find(limit=5)
            
    except pyactiveresource.connection.UnauthorizedAccess:
        error_message = "Failed to authorize with Shopify. Please check your API key, secret, and scopes."
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"

    return render(request, "auth_app/home.html", {
        'shop_url': shop_url,
        'access_token': access_token, # Be careful about displaying tokens directly in production HTML
        'shop_details': shop_details,
        'products': products,
        'error_message': error_message,
        'shopify_app_api_key': settings.SHOPIFY_APP_API_KEY # For display, to help debug
    })
