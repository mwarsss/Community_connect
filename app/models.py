from app import db


def get_db():
    from app import db  # ✅ local import to avoid circular import
    return db


# Define model at top to avoid circular use


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def __init__(self, title, description, category, location) -> None:
        self.title = title
        self.description = description
        self.category = category
        self.location = location


def add_opportunity(title, description, category, location):
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
    db = get_db()
    if not query:
        return db.session.query(Opportunity).all()
    query = f"%{query.lower()}%"
    return db.session.query(Opportunity).filter(
        (Opportunity.title.ilike(query)) |  # type: ignore
        (Opportunity.category.ilike(query))  # type: ignore
    ).all()
