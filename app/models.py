def get_db():
    from app import db  # ✅ local import to avoid circular import
    return db


def add_opportunity(title, description, category, location):
    from app.models import Opportunity  # ✅ local import
    db = get_db()
    opp = Opportunity(
        title=title,
        description=description,
        category=category,
        location=location
    )
    db.session.add(opp)
    db.session.commit()


def get_opportunities(query=None):
    from app.models import Opportunity  # ✅ local import
    db = get_db()
    if not query:
        return db.session.query(Opportunity).all()
    query = f"%{query.lower()}%"
    return db.session.query(Opportunity).filter(
        (Opportunity.title.ilike(query)) |
        (Opportunity.category.ilike(query))
    ).all()

# Define model at bottom to avoid circular use


def define_models():
    from app import db

    class Opportunity(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text, nullable=False)
        category = db.Column(db.String(50), nullable=False)
        location = db.Column(db.String(100), nullable=False)

    return Opportunity


# Register models for global access
Opportunity = define_models()
