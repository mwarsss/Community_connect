from flask import render_template, request, redirect, flash, url_for, Blueprint, current_app
from app import db, create_app
from app.models import User, Opportunity
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app.models import User, Opportunity
from app.models import get_db
from app.models import Opportunity

# Category options (centralized list)
CATEGORIES = ["Education", "Climate", "Health", "Youth", "Technology"]

# ---------- Home Route with Search + Filter + Pagination ----------

main = Blueprint("main", __name__)


@main.route("/")
def index():
    query = request.args.get("q", "")
    selected_category = request.args.get("category", "")
    page = request.args.get("page", 1, type=int)

    results_query = Opportunity.query

    if query:
        results_query = results_query.filter(
            (Opportunity.title.ilike(f"%{query}%")) |  # type: ignore
            (Opportunity.category.ilike(f"%{query}%"))  # type: ignore
        )

    if selected_category:
        results_query = results_query.filter_by(category=selected_category)

    paginated = results_query.order_by(
        Opportunity.id.desc()).paginate(page=page, per_page=5)

    return render_template(
        "index.html",
        opportunities=paginated.items,
        pagination=paginated,
        query=query,
        selected_category=selected_category,
        categories=CATEGORIES
    )

# ---------- Form for Submitting a New Opportunity ----------


@main.route('/new', methods=["GET", "POST"])
def new_opportunity():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()

        # Basic validation
        if not title or not description or not category or not location:
            flash("All fields are required.", "error")
            return redirect("/new")

        new_opp = Opportunity(
            title=title,
            description=description,
            category=category,
            location=location
        )

        db.session.add(new_opp)
        db.session.commit()
        flash("Opportunity posted successfully!", "success")
        return redirect("/")

    return render_template("new.html", categories=CATEGORIES)


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "error")
            # Pass debug_mode in case of error too
            return render_template("register.html", debug_mode=current_app.config['DEBUG'])

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered.", "error")
            # Pass debug_mode in case of existing user too
            return render_template("register.html", debug_mode=current_app.config['DEBUG'])

        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect("/login")

    # Pass the debug status to the template when rendering GET request
    return render_template("register.html", debug_mode=current_app.config['DEBUG'])


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1. Get data from the form.
        # Your form uses 'username', so retrieve that instead of 'email'.
        # Ensure you import 'request' from Flask if not already done.
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # 2. Basic validation for empty fields.
        if not username or not password:
            flash("Username and password are required.", "error")
            # If there's an error, re-render the login page, passing debug_mode
            return render_template("login.html", debug_mode=current_app.config['DEBUG'])

        # 3. Query the User model using the 'username' from the form.
        # Make sure your User model has a 'username' column and it's unique.
        user = User.query.filter_by(username=username).first()

        # 4. Check if the user exists and the password is correct.
        if user and user.check_password(password):
            # 5. Log the user in using Flask-Login's login_user function.
            login_user(user)
            flash("Login successful!", "success")

            # 6. Redirect to the home route ('/').
            # url_for('main.index') generates the URL for the 'index' function
            # defined in your 'main' blueprint, which corresponds to '/'.
            return redirect(url_for('main.index'))
        else:
            # 7. Handle invalid credentials.
            flash("Invalid username or password.", "error")
            # If login fails, re-render the login page, passing debug_mode
            return render_template("login.html", debug_mode=current_app.config['DEBUG'])

    # For GET requests, just render the login form.
    # Pass debug_mode to the template as well.
    return render_template("login.html", debug_mode=current_app.config['DEBUG'])


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect("/")
