from flask import render_template, request, redirect, flash, url_for, Blueprint
from app import db
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
