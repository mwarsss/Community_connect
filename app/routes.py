from flask import render_template, request, redirect, url_for, flash
from app.models import get_opportunities
from .models import add_opportunity, get_opportunities
CATEGORIES = ["Education", "Health", "Environment",
              "Technology", "Community Service"]


def register_routes(app):
    @app.route("/")
    def index():
        query = request.args.get("q", "")
        selected_category = request.args.get("category", "")

        results = get_opportunities(query=query, category=selected_category)

        return render_template("index.html", opportunities=results, query=query, selected_category=selected_category, categories=CATEGORIES)

    @app.route("/new", methods=["GET", "POST"])
    def new_opportunity():
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            category = request.form["category"]
            location = request.form["location"]

            if not title or not description or not category or not location:
                flash("All fields are required!", "error")
                return redirect("/new")

                new_opportunity = Opportunity(
                    title=title,
                    description=description,
                    category=category,
                    location=location
                )
                db.session.add(new_opp)
                db.session.commit()
                flash("Opportunity added successfully!", "success")
                return redirect("/")

            add_opportunity(title, description, category, location)
            return redirect(url_for("home"))

        return render_template("new.html", categories=CATEGORIES)
