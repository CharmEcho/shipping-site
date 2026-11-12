import random, string
from flask_login import current_user
from flask import abort

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


def generate_tracking_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
