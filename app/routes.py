# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user

from functools import wraps
import random, string
from .extensions import db, bcrypt
from .forms import RegistrationForm, LoginForm, ShipmentForm, PaymentForm, TrackingForm
from .models import User, Shipment, Tracking, Payment




main_routes = Blueprint("main_routes", __name__)

def generate_tracking_number():
    return "TRK" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Home + static
@main_routes.route("/")
def home():
    return render_template("home.html")

@main_routes.route("/about")
def about():
    return render_template("about.html")

@main_routes.route("/contact")
def contact():
    return render_template("contact.html")

@main_routes.route("/pricing")
def pricing():
    return render_template("pricing.html")

# Admin dashboard (for admins only)
@main_routes.route("/admin")
@login_required
@admin_required
def admin_dashboard():

    users = User.query.all()
    shipments = Shipment.query.all()

    return render_template(
        "admin/dashboard.html",
        users=users,
        shipments=shipments
    )

# Registration / Login
@main_routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("main_routes.register"))

        new_user = User(
            username=form.username.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)  # ✅ single source of truth

        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("main_routes.login"))

    return render_template("register.html", form=form)

#------------------------------------------
#LOGIN WITH NO EMAIL REQUIRED
#-----------------------------------------------

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user)

            flash('Login successful', 'success')
            return redirect(url_for('main_routes.dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


#------------------------------------------------




@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main_routes.login"))

# Dashboard / Create shipment
@main_routes.route("/dashboard")
@login_required
def dashboard():
    shipments = Shipment.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", shipments=shipments, user=current_user)

@main_routes.route("/create_shipment", methods=["GET", "POST"])
@login_required
def create_shipment():
    form = ShipmentForm()
    if form.validate_on_submit():
        shipment = Shipment(
            sender_name=form.sender_name.data,
            receiver_name=form.receiver_name.data,
            origin=form.origin.data,
            destination=form.destination.data,
            tracking_number=generate_tracking_number(),
            user_id=current_user.id
        )
        db.session.add(shipment)
        db.session.commit()
        flash("Shipment created!", "success")
        return redirect(url_for("main_routes.confirmation", tracking_number=shipment.tracking_number))
    return render_template("create_shipment.html", form=form)

@main_routes.route("/confirmation")
@login_required
def confirmation():
    # optionally accept query args or show last shipment
    tracking_number = request.args.get("tracking_number")
    return render_template("confirmation.html", tracking_number=tracking_number)

# Track form (GET shows form, POST redirects to view)
@main_routes.route("/track", methods=["GET","POST"])
def track_shipment():
    if request.method == "POST":
        tracking_number = request.form.get("tracking_number")
        return redirect(url_for("main_routes.track", tracking_code=tracking_number))
    return render_template("track.html")  # if you want a separate form page, or home has form



@main_routes.route("/track/<string:tracking_code>")
def track(tracking_code):
    shipment = Shipment.query.filter_by(tracking_number=tracking_code).first()

    if not shipment:
        flash("Tracking number not found!", "danger")
        return redirect(url_for("main_routes.home"))

    updates = Tracking.query.filter_by(shipment_id=shipment.id).all()
    return render_template("track.html", shipment=shipment, updates=updates)




# Admin update
@main_routes.route("/admin/update/<int:shipment_id>", methods=["GET","POST"])
@admin_required
def admin_update(shipment_id):
    form = TrackingForm()
    shipment = Shipment.query.get_or_404(shipment_id)
    if form.validate_on_submit():
        update = Tracking(status=form.status.data, location=form.location.data, shipment_id=shipment.id)
        db.session.add(update); db.session.commit()
        flash("Tracking updated!", "success")
        return redirect(url_for("main_routes.track", tracking_code=shipment.tracking_number))
    return render_template("admin_update.html", form=form, shipment=shipment)

# Payment
@main_routes.route("/payment/<int:shipment_id>", methods=["GET","POST"])
@login_required
def payment(shipment_id):
    form = PaymentForm()
    shipment = Shipment.query.get_or_404(shipment_id)
    if form.validate_on_submit():
        new_payment = Payment(amount=form.amount.data, method=form.method.data, status="Completed",
                              user_id=current_user.id, shipment_id=shipment.id)
        db.session.add(new_payment); db.session.commit()
        flash("Payment successful!", "success")
        return redirect(url_for("main_routes.dashboard"))
    return render_template("payment.html", form=form, shipment=shipment)


@main_routes.route("/admin/user/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.is_admin = bool(request.form.get("is_admin"))
        db.session.commit()
        flash("User updated successfully", "success")
        return redirect(url_for("main_routes.admin_dashboard"))

    return render_template("edit_user.html", user=user)
