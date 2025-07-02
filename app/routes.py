from flask import render_template, request, redirect, url_for
from .models import add_opportunity, get_opportunities


def register_routes(app):
    @app.route("/")
    def home():
        search_query = request.args.get("q", "")
        filtered = get_opportunities(search_query)
        return render_template("index.html", opportunities=filtered, query=search_query)

    @app.route("/new", methods=["GET", "POST"])
    def new_opportunity():
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            category = request.form["category"]
            location = request.form["location"]
            add_opportunity(title, description, category, location)
            return redirect(url_for("home"))
        return render_template("new.html")
