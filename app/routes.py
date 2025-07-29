from flask import jsonify, render_template, request, redirect, flash, url_for, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required
# Keep if still used elsewhere, otherwise can remove
from werkzeug.security import check_password_hash

# Ensure this decorator exists in app/decorators.py
from app.decorators import moderator_required

# IMPORTANT: Only import 'db' directly from 'app'
# This 'db' instance is the one initialized by SQLAlchemy in app/__init__.py
from app import db  # Correct way to import the db instance

# Import your models. Do NOT import 'db' again from models.
# Assuming Report model exists, based on your routes
from app.models import User, Opportunity, Report

# Import your custom decorator
# Make sure role_required is correctly defined in app/utils.py
from app.utils import role_required


# Category options (centralized list)
CATEGORIES = ["Education", "Climate", "Health", "Youth", "Technology"]

# ---------- Define your Blueprints ----------
# Define the 'main' blueprint
main = Blueprint("main", __name__)

# Define the 'moderator' blueprint
# It's good practice to register routes under the blueprint they belong to.
# The previous `moderator_bp` was being used, but its routes were often tied to `main`.
# Let's ensure the routes meant for `moderator_bp` actually use it.
# Added url_prefix for consistency
moderator_bp = Blueprint('moderator', __name__, url_prefix='/moderator')


# ---------- Home Route with Search + Filter + Pagination ----------
@main.route("/")
def index():
    query = request.args.get("q", "").strip()  # Strip whitespace from queries
    selected_category = request.args.get("category", "").strip()
    page = request.args.get("page", 1, type=int)

    results_query = Opportunity.query.filter_by(is_approved=True)

    if query:
        # Use OR to search in multiple fields
        results_query = results_query.filter(
            (Opportunity.title.ilike(f"%{query}%")) |
            # Also search in description
            (Opportunity.description.ilike(f"%{query}%")) |
            (Opportunity.category.ilike(f"%{query}%")) |
            (Opportunity.location.ilike(f"%{query}%"))
        )

    if selected_category and selected_category in CATEGORIES:  # Validate category
        results_query = results_query.filter_by(category=selected_category)

    # Ordered by creation date (descending) is often more useful for a feed
    paginated = results_query.order_by(Opportunity.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )

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
@login_required
def new_opportunity():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()

        if not all([title, description, category, location]):  # More concise validation
            flash("All fields are required.", "error")
            return render_template("new.html", categories=CATEGORIES,
                                   form_data=request.form)  # Pass form data back to pre-fill

        if category not in CATEGORIES:  # Validate category input
            flash("Invalid category selected.", "error")
            return render_template("new.html", categories=CATEGORIES,
                                   form_data=request.form)

        new_opp = Opportunity(
            title=title,
            description=description,
            category=category,
            location=location,
            user_id=current_user.id
        )

        # Use the same logic everywhere
        if current_user.is_authenticated and current_user.role in ['admin', 'moderator']:
            new_opp.is_approved = True
            new_opp.approved_by = current_user.username
        else:
            new_opp.is_approved = False

        try:
            db.session.add(new_opp)
            db.session.commit()

            if new_opp.is_approved:
                flash("Opportunity posted and approved successfully!", "success")
            else:
                flash("Opportunity submitted for approval!", "info")
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating the opportunity.", "error")
            return render_template("new.html", categories=CATEGORIES, form_data=request.form)

    return render_template("new.html", categories=CATEGORIES)


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:  # Prevent logged-in users from registering again
        flash("You are already logged in.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not all([username, email, password]):
            flash("All fields are required.", "error")
            return render_template("register.html", debug_mode=current_app.config['DEBUG'],
                                   form_data=request.form)

        existing_user_email = User.query.filter_by(email=email).first()
        existing_user_username = User.query.filter_by(
            username=username).first()

        if existing_user_email:
            flash("Email is already registered.", "error")
        elif existing_user_username:
            flash("Username is already taken.", "error")
        else:
            new_user = User(
                username=username,
                email=email,
                role="user"
            )
            new_user.set_password(password)  # Hash the password
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("main.login"))

        return render_template("register.html", debug_mode=current_app.config['DEBUG'],
                               form_data=request.form)

    return render_template("register.html", debug_mode=current_app.config['DEBUG'])


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not all([username, password]):
            flash("Username and password are required.", "error")
            return render_template("login.html", debug_mode=current_app.config['DEBUG'])

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
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
@role_required("admin")
def admin_dashboard():
    # You might want to pass some data here, e.g., user counts, pending opportunities
    return render_template("admin/dashboard.html")


# Helper function to check moderator status (can be used in templates or other functions)
# Keep this as it's useful for internal checks
def is_moderator_or_admin():
    return current_user.is_authenticated and current_user.role in ['admin', 'moderator']


# ----- MODERATOR BLUEPRINT ROUTES -----
# These routes are now correctly associated with `moderator_bp`
# and will inherit its `/moderator` url_prefix

@moderator_bp.route("/opportunities")  # This will be /moderator/opportunities
@login_required
@moderator_required  # Use the decorator for consistency and clarity
def moderate_opportunities():
    opportunities = Opportunity.query.filter_by(
        is_approved=False).order_by(Opportunity.created_at.desc()).all()
    return render_template('moderate_opportunities.html', opportunities=opportunities)


# This will be /moderator/approve/<id>
@moderator_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
@moderator_required  # Use the decorator
def approve_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    opp.is_approved = True
    opp.approved_by = current_user.username
    db.session.commit()
    flash("Opportunity approved.", "success")
    return redirect(url_for('moderator.moderate_opportunities'))


# This will be /moderator/reject/<id>
@moderator_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
@moderator_required  # Use the decorator
def reject_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    db.session.delete(opp)
    db.session.commit()
    flash("Opportunity rejected.", "warning")
    return redirect(url_for('moderator.moderate_opportunities'))


# ----- MAIN BLUEPRINT ROUTES (User Dashboard and Opportunity Management) -----

@main.route("/dashboard")
@login_required
def dashboard():
    opportunities = Opportunity.query.filter_by(
        user_id=current_user.id).order_by(Opportunity.created_at.desc()).all()
    return render_template("dashboard.html", opportunities=opportunities)


@main.route('/opportunity/<int:opportunity_id>')
def view_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    return render_template('view_opportunity.html', opportunity=opportunity)


@main.route('/opportunity/<int:opportunity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.user_id != current_user.id:
        flash('You are not authorized to edit this opportunity.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        opportunity.title = request.form.get('title', '').strip()
        opportunity.description = request.form.get('description', '').strip()
        opportunity.location = request.form.get('location', '').strip()
        # Ensure category is also handled if it's editable
        opportunity.category = request.form.get('category', '').strip()
        if opportunity.category not in CATEGORIES:
            flash("Invalid category selected.", "error")
            return render_template('edit_opportunity.html', opportunity=opportunity, categories=CATEGORIES)

        db.session.commit()
        flash('Opportunity updated successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_opportunity.html', opportunity=opportunity, categories=CATEGORIES)


# Changed to POST, as deletes should not be GET
@main.route('/opportunity/<int:opportunity_id>/delete', methods=['POST'])
@login_required
# This is the user's own opportunity delete
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.user_id != current_user.id:
        flash('You are not authorized to delete this opportunity.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(opportunity)
    db.session.commit()
    flash('Opportunity deleted successfully.', 'success')
    return redirect(url_for('main.dashboard'))


# Consider renaming to /feed or similar for clarity
@main.route('/opportunities')
def public_feed():
    # You might want to filter only approved opportunities here, similar to index
    opportunities = Opportunity.query.filter_by(
        is_approved=True).order_by(Opportunity.id.desc()).all()
    return render_template('public_feed.html', opportunities=opportunities)


# ----- ADMIN/MODERATOR ROUTES (User Management) -----
# These are still under the 'main' blueprint, but guarded by role checks.
# You could move these to the 'moderator_bp' if preferred, adjusting URLs.

@main.route('/admin/users')
@login_required
# Use role_required with a list for multiple roles
@role_required(['admin', 'moderator'])
def user_moderation():
    # No need for redundant check if using role_required decorator correctly
    users = User.query.all()
    return render_template('user_moderation.html', users=users)


# Changed to POST
@main.route('/admin/suspend/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin', 'moderator'])
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:  # Prevent self-suspension
        flash("You cannot suspend yourself.", "danger")
        return redirect(url_for('main.user_moderation'))

    user.suspend()
    db.session.commit()
    flash("User suspended", "success")  # Use success/danger for flashes
    return redirect(url_for('main.user_moderation'))


# Changed to POST
@main.route('/admin/activate/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin', 'moderator'])
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.activate()
    db.session.commit()
    flash("User activated", "success")
    return redirect(url_for('main.user_moderation'))


# Changed to POST
@main.route('/admin/role/<int:user_id>/<role>', methods=['POST'])
@login_required
@role_required('admin')  # Only admin can change roles
def change_role(user_id, role):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id and role != current_user.role:  # Prevent self-demotion/promotion
        flash("You cannot change your own role.", "danger")
        return redirect(url_for('main.user_moderation'))

    # Validate target role
    valid_roles = ['user', 'moderator', 'admin']
    if role not in valid_roles:
        flash("Invalid role specified.", "danger")
        return redirect(url_for('main.user_moderation'))

    # Assuming promote method correctly handles setting role
    user.promote(role)
    db.session.commit()
    flash(f"Role for {user.username} changed to {role}", "success")
    return redirect(url_for('main.user_moderation'))

# ----- API/JSON Endpoints (Reports and Moderator Actions via API) -----


@main.route('/report', methods=['POST'])
@login_required
def submit_report():
    data = request.get_json()
    reason = data.get('reason')
    reported_user_id = data.get('reported_user_id')
    reported_opportunity_id = data.get('reported_opportunity_id')

    if not reason or (not reported_user_id and not reported_opportunity_id):
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure at least one of user_id or opportunity_id is provided, not both
    if reported_user_id and reported_opportunity_id:
        return jsonify({"error": "Report must be for a user OR an opportunity, not both."}), 400

    # Fetch User/Opportunity objects to ensure they exist
    reported_user = User.query.get(
        reported_user_id) if reported_user_id else None
    reported_opportunity = Opportunity.query.get(
        reported_opportunity_id) if reported_opportunity_id else None

    if (reported_user_id and not reported_user) or (reported_opportunity_id and not reported_opportunity):
        return jsonify({"error": "Reported user or opportunity not found."}), 404

    report = Report(
        reporter_id=current_user.id,
        reported_user_id=reported_user_id,
        reported_opportunity_id=reported_opportunity_id,
        reason=reason
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report submitted"}), 201


# This will be /moderator/reports
@moderator_bp.route('/reports', methods=['GET'])
@login_required
@moderator_required
def view_reports():
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    data = []

    for report in reports:
        data.append({
            'id': report.id,
            'reporter_username': report.reporter.username,  # More explicit
            'reason': report.reason,
            'timestamp': report.timestamp.isoformat(),
            'is_reviewed': report.is_reviewed,  # Add review status
            'reported_user': {
                'id': report.reported_user.id,
                'username': report.reported_user.username
            } if report.reported_user else None,
            'reported_opportunity': {
                'id': report.reported_opportunity.id,
                'title': report.reported_opportunity.title
            } if report.reported_opportunity else None
        })
    return jsonify(data), 200


# This will be /moderator/delete_user/<id>
@moderator_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
@moderator_required
def moderator_delete_user(user_id):  # Renamed for clarity
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({"error": "Cannot delete your own account via this route."}), 403
    if user.role == 'admin' and current_user.role != 'admin':
        return jsonify({"error": "Only an admin can delete another admin."}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User '{user.username}' deleted."}), 200


# This will be /moderator/delete_opportunity/<id>
@moderator_bp.route('/delete_opportunity/<int:opp_id>', methods=['DELETE'])
@login_required
@moderator_required
def moderator_delete_opportunity(opp_id):  # <--- RENAMED THIS FUNCTION!
    opportunity = Opportunity.query.get_or_404(opp_id)
    db.session.delete(opportunity)
    db.session.commit()
    return jsonify({"message": f"Opportunity '{opportunity.title}' deleted."}), 200


# This will be /moderator/ban_user/<id>
@moderator_bp.route('/ban_user/<int:user_id>', methods=['POST'])
@login_required
@moderator_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({"error": "Cannot ban yourself."}), 403
    if user.role == 'admin' and current_user.role != 'admin':
        return jsonify({"error": "Only an admin can ban another admin."}), 403

    user.is_banned = True
    db.session.commit()
    return jsonify({"message": f"User '{user.username}' banned."}), 200


# This will be /moderator/mark_reviewed/<id>
@moderator_bp.route('/mark_reviewed/<int:report_id>', methods=['POST'])
@login_required
@moderator_required
def mark_report_reviewed(report_id):
    report = Report.query.get_or_404(report_id)
    report.is_reviewed = True
    db.session.commit()
    return jsonify({"message": "Report marked as reviewed"}), 200
