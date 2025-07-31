from flask import jsonify, request, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.decorators import moderator_required
from app import db
from app.models import User, Opportunity, Report, PasswordResetToken
from app.utils import role_required

CATEGORIES = ["Education", "Climate", "Health", "Youth", "Technology", "Mental Health"]

main = Blueprint("main", __name__)
moderator_bp = Blueprint('moderator', __name__, url_prefix='/moderator')

@main.route("/")
def index():
    query = request.args.get("q", "").strip()
    selected_category = request.args.get("category", "").strip()
    page = request.args.get("page", 1, type=int)

    results_query = Opportunity.query.filter_by(is_approved=True)

    if query:
        results_query = results_query.filter(
            (Opportunity.title.ilike(f"%{query}%")) |
            (Opportunity.description.ilike(f"%{query}%")) |
            (Opportunity.category.ilike(f"%{query}%")) |
            (Opportunity.location.ilike(f"%{query}%"))
        )

    if selected_category and selected_category in CATEGORIES:
        results_query = results_query.filter_by(category=selected_category)

    paginated = results_query.order_by(Opportunity.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )

    return jsonify({
        'opportunities': [opp.to_dict() for opp in paginated.items],
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total_pages': paginated.pages,
            'total_items': paginated.total
        }
    })

@main.route('/new', methods=["POST"])
@login_required
def new_opportunity():
    data = request.get_json()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    category = data.get("category", "").strip()
    location = data.get("location", "").strip()

    if not all([title, description, category, location]):
        return jsonify({"error": "All fields are required."}), 400

    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category selected."}), 400

    new_opp = Opportunity(
        title=title,
        description=description,
        category=category,
        location=location,
        user_id=current_user.id
    )

    if current_user.is_authenticated and current_user.role in ['admin', 'moderator']:
        new_opp.is_approved = True
        new_opp.approved_by = current_user.username
    else:
        new_opp.is_approved = False

    try:
        db.session.add(new_opp)
        db.session.commit()
        return jsonify(new_opp.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the opportunity."}), 500

@main.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not all([username, email, password]):
        return jsonify({"error": "All fields are required."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered."}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not all([username, password]):
        return jsonify({"error": "Username and password are required."}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "Invalid username or password."}), 401

@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "You have been logged out."}), 200

@main.route("/@me")
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())

@moderator_bp.route("/opportunities")
@login_required
@moderator_required
def moderate_opportunities():
    opportunities = Opportunity.query.filter_by(is_approved=False).order_by(Opportunity.created_at.desc()).all()
    return jsonify([opp.to_dict() for opp in opportunities])

@moderator_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
@moderator_required
def approve_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    opp.is_approved = True
    opp.approved_by = current_user.username
    db.session.commit()
    return jsonify(opp.to_dict())

@moderator_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
@moderator_required
def reject_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    db.session.delete(opp)
    db.session.commit()
    return jsonify({"message": "Opportunity rejected."}), 200

@main.route("/dashboard")
@login_required
def dashboard():
    opportunities = Opportunity.query.filter_by(user_id=current_user.id).order_by(Opportunity.created_at.desc()).all()
    return jsonify([opp.to_dict() for opp in opportunities])

@main.route('/opportunity/<int:opportunity_id>')
def view_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    return jsonify(opportunity.to_dict())

@main.route('/opportunity/<int:opportunity_id>/edit', methods=['POST'])
@login_required
def edit_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to edit this opportunity."}), 403

    data = request.get_json()
    opportunity.title = data.get('title', opportunity.title).strip()
    opportunity.description = data.get('description', opportunity.description).strip()
    opportunity.location = data.get('location', opportunity.location).strip()
    opportunity.category = data.get('category', opportunity.category).strip()

    if opportunity.category not in CATEGORIES:
        return jsonify({"error": "Invalid category selected."}), 400

    db.session.commit()
    return jsonify(opportunity.to_dict())

@main.route('/opportunity/<int:opportunity_id>/delete', methods=['DELETE'])
@login_required
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to delete this opportunity."}), 403

    db.session.delete(opportunity)
    db.session.commit()
    return jsonify({"message": "Opportunity deleted successfully."}), 200

@main.route('/opportunities')
def public_feed():
    opportunities = Opportunity.query.filter_by(is_approved=True).order_by(Opportunity.id.desc()).all()
    return jsonify([opp.to_dict() for opp in opportunities])

@main.route('/admin/users')
@login_required
@role_required(['admin', 'moderator'])
def user_moderation():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@main.route('/admin/suspend/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin', 'moderator'])
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({"error": "You cannot suspend yourself."}), 403

    user.suspend()
    db.session.commit()
    return jsonify(user.to_dict())

@main.route('/admin/activate/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin', 'moderator'])
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.activate()
    db.session.commit()
    return jsonify(user.to_dict())

@main.route('/admin/role/<int:user_id>/<role>', methods=['POST'])
@login_required
@role_required('admin')
def change_role(user_id, role):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id and role != current_user.role:
        return jsonify({"error": "You cannot change your own role."}), 403

    valid_roles = ['user', 'moderator', 'admin']
    if role not in valid_roles:
        return jsonify({"error": "Invalid role specified."}), 400

    user.promote(role)
    db.session.commit()
    return jsonify(user.to_dict())

@main.route('/report', methods=['POST'])
@login_required
def submit_report():
    data = request.get_json()
    reason = data.get('reason')
    reported_user_id = data.get('reported_user_id')
    reported_opportunity_id = data.get('reported_opportunity_id')

    if not reason or (not reported_user_id and not reported_opportunity_id):
        return jsonify({"error": "Missing required fields"}), 400

    if reported_user_id and reported_opportunity_id:
        return jsonify({"error": "Report must be for a user OR an opportunity, not both."}), 400

    reported_user = User.query.get(reported_user_id) if reported_user_id else None
    reported_opportunity = Opportunity.query.get(reported_opportunity_id) if reported_opportunity_id else None

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

@moderator_bp.route('/reports', methods=['GET'])
@login_required
@moderator_required
def view_reports():
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    data = []

    for report in reports:
        data.append({
            'id': report.id,
            'reporter_username': report.reporter.username,
            'reason': report.reason,
            'timestamp': report.timestamp.isoformat(),
            'is_reviewed': report.is_reviewed,
            'reported_user': report.reported_user.to_dict() if report.reported_user else None,
            'reported_opportunity': report.reported_opportunity.to_dict() if report.reported_opportunity else None
        })
    return jsonify(data), 200

@moderator_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
@moderator_required
def moderator_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({"error": "Cannot delete your own account via this route."}), 403
    if user.role == 'admin' and current_user.role != 'admin':
        return jsonify({"error": "Only an admin can delete another admin."}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User '{user.username}' deleted."}), 200

@moderator_bp.route('/delete_opportunity/<int:opp_id>', methods=['DELETE'])
@login_required
@moderator_required
def moderator_delete_opportunity(opp_id):
    opportunity = Opportunity.query.get_or_404(opp_id)
    db.session.delete(opportunity)
    db.session.commit()
    return jsonify({"message": f"Opportunity '{opportunity.title}' deleted."}), 200

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
    return jsonify(user.to_dict()), 200

@moderator_bp.route('/mark_reviewed/<int:report_id>', methods=['POST'])
@login_required
@moderator_required
def mark_report_reviewed(report_id):
    report = Report.query.get_or_404(report_id)
    report.is_reviewed = True
    db.session.commit()
    return jsonify({"message": "Report marked as reviewed"}), 200