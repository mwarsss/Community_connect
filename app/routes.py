from flask import render_template, request, redirect, flash, url_for, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash

# IMPORTANT: Only import 'db' directly from 'app'
# This 'db' instance is the one initialized by SQLAlchemy in app/__init__.py
from app import db  # Correct way to import the db instance

# Import your models. Do NOT import 'db' again from models.
from app.models import User, Opportunity  # Assuming these are your models

# Import your custom decorator
# Make sure role_required is correctly defined in app/utils.py
from app.utils import role_required


# Category options (centralized list)
CATEGORIES = ["Education", "Climate", "Health", "Youth", "Technology"]

# ---------- Define your Blueprints ----------
# Define the 'main' blueprint
main = Blueprint("main", __name__)

# Define the 'moderator' blueprint
# If moderator_bp is used globally in this file, it's defined here.
# If it's intended to be in its own file (e.g., app/moderator_routes.py),
# then you would import it from there (e.g., from app.moderator_routes import moderator_bp)
moderator_bp = Blueprint('moderator', __name__)


# ---------- Home Route with Search + Filter + Pagination ----------
@main.route("/")
def index():
    query = request.args.get("q", "")
    selected_category = request.args.get("category", "")
    page = request.args.get("page", 1, type=int)

    # Note: opportunities = Opportunity.query.filter_by(is_approved=True).all()
    # This line immediately fetches *all* approved opportunities.
    # If you intend to filter/paginate ALL opportunities, then `results_query` should start from Opportunity.query.
    # The subsequent `filter` calls will then refine the query before pagination.
    # Let's start `results_query` directly from Opportunity.query to ensure correct filtering/pagination.
    results_query = Opportunity.query.filter_by(
        is_approved=True)  # Start with only approved

    if query:
        results_query = results_query.filter(
            (Opportunity.title.ilike(f"%{query}%")) |
            (Opportunity.category.ilike(f"%{query}%"))
        )

    if selected_category:
        results_query = results_query.filter_by(category=selected_category)

    paginated = results_query.order_by(
        # Add error_out=False for cleaner pagination
        Opportunity.id.desc()).paginate(page=page, per_page=5, error_out=False)

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
@login_required  # Often, submitting new opportunities requires login
def new_opportunity():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()

        # Basic validation
        if not title or not description or not category or not location:
            flash("All fields are required.", "error")
            # Render the template with current data/errors
            return render_template("new.html", categories=CATEGORIES)

        new_opp = Opportunity(
            title=title,
            description=description,
            category=category,
            location=location,
            user_id=current_user.id  # Assign the opportunity to the current user
        )

        # Check if current_user.role is a string before using 'in' operator
        if current_user.is_authenticated and current_user.role in ['admin', 'moderator']:
            new_opp.is_approved = True
            new_opp.approved_by = current_user.username
        else:
            new_opp.is_approved = False  # Default to false if not admin/moderator

        db.session.add(new_opp)
        db.session.commit()

        if new_opp.is_approved:
            flash("Opportunity posted and approved successfully!", "success")
        else:
            flash("Opportunity submitted for approval!", "info")
        # Redirect to user's dashboard or home
        return redirect(url_for("main.dashboard"))

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
            return render_template("register.html", debug_mode=current_app.config['DEBUG'])

        # Check if user already exists
        existing_user_email = User.query.filter_by(email=email).first()
        if existing_user_email:
            flash("Email is already registered.", "error")
            return render_template("register.html", debug_mode=current_app.config['DEBUG'])

        existing_user_username = User.query.filter_by(
            username=username).first()
        if existing_user_username:
            flash("Username is already taken.", "error")
            return render_template("register.html", debug_mode=current_app.config['DEBUG'])

        # Default role for new registrations should usually be 'user', not 'moderator'
        # Unless your registration process specifically creates moderators.
        new_user = User(
            username=username,
            email=email,
            role="user"  # Default to 'user' for new registrations
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("main.login"))  # Use url_for for redirects

    return render_template("register.html", debug_mode=current_app.config['DEBUG'])


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html", debug_mode=current_app.config['DEBUG'])

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            # Get the 'next' parameter from the URL if a user was redirected here
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html", debug_mode=current_app.config['DEBUG'])

    return render_template("login.html", debug_mode=current_app.config['DEBUG'])


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))


@main.route("/admin/dashboard")
@login_required
@role_required("admin")  # Assuming admin_dashboard is only for 'admin'
def admin_dashboard():
    return render_template("admin/dashboard.html")


# Helper function to check moderator status (can be used in templates or other functions)
def is_moderator_or_admin():
    # Use 'in' operator to check if current_user.role is one of the allowed roles
    return current_user.is_authenticated and current_user.role in ['admin', 'moderator']

# Moderator dashboard using the moderator_bp


@moderator_bp.route("/moderate/opportunities")
@login_required
def moderate_opportunities():  # Renamed function to match route
    if not is_moderator_or_admin():  # Use the helper function
        flash("Access denied", "danger")
        return redirect(url_for("main.index"))

    # .all should be a method call for SQLAlchemy query objects, so it's .all()
    opportunities = Opportunity.query.filter_by(is_approved=False).all()
    return render_template('moderate_opportunities.html', opportunities=opportunities)


@moderator_bp.route('/moderate/approve/<int:id>')
@login_required
def approve_opportunity(id):
    if not is_moderator_or_admin():  # Use the helper function
        flash("Access denied", "danger")
        return redirect(url_for('main.index'))

    opp = Opportunity.query.get_or_404(id)
    opp.is_approved = True
    opp.approved_by = current_user.username
    db.session.commit()
    flash("Opportunity approved.", "success")
    # Correct blueprint name
    return redirect(url_for('moderator.moderate_opportunities'))


@moderator_bp.route('/moderate/reject/<int:id>')
@login_required
def reject_opportunity(id):
    if not is_moderator_or_admin():  # Use the helper function
        flash("Access denied", "danger")
        return redirect(url_for('main.index'))

    opp = Opportunity.query.get_or_404(id)
    db.session.delete(opp)
    db.session.commit()
    flash("Opportunity rejected.", "warning")
    # Correct blueprint name
    return redirect(url_for('moderator.moderate_opportunities'))


@main.route("/dashboard")
@login_required
def dashboard():
    opportunities = Opportunity.query.filter_by(
        user_id=current_user.id).order_by(Opportunity.created_at.desc()).all()
    return render_template("dashboard.html", opportunities=opportunities)


# Edit an opportunity
@main.route('/opportunity/<int:opportunity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.user_id != current_user.id:
        flash('You are not authorized to edit this opportunity.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        opportunity.title = request.form['title']
        opportunity.description = request.form['description']
        opportunity.location = request.form['location']
        db.session.commit()
        flash('Opportunity updated successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_opportunity.html', opportunity=opportunity)

# Delete an opportunity


@main.route('/opportunity/<int:opportunity_id>/delete', methods=['POST'])
@login_required
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.user_id != current_user.id:
        flash('You are not authorized to delete this opportunity.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(opportunity)
    db.session.commit()
    flash('Opportunity deleted successfully.', 'success')
    return redirect(url_for('main.dashboard'))
