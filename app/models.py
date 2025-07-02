# app/models.py

opportunities = []


def add_opportunity(title, description, category, location):
    opportunity = {
        "title": title,
        "description": description,
        "category": category,
        "location": location
    }
    opportunities.append(opportunity)


def get_opportunities(query=None):
    if not query:
        return opportunities
    query_lower = query.lower()
    return [opp for opp in opportunities if query_lower in opp["title"].lower() or query_lower in opp["category"].lower()]
