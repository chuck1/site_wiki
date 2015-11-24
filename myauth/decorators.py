
from django.contrib.auth.decorators import login_requred as auth_login_required

def login_required(function, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field

