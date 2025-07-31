from app import create_app, db
from app.models import User, Opportunity

app = create_app()

with app.app_context():
    # Create users
    user1 = User(username='john_doe', email='john.doe@example.com')
    user1.set_password('password123')

    user2 = User(username='jane_doe', email='jane.doe@example.com')
    user2.set_password('password123')

    moderator = User(username='mod_user', email='moderator@example.com', role='moderator')
    moderator.set_password('password123')

    db.session.add_all([user1, user2, moderator])
    db.session.commit()

    # Create opportunities
    opp1 = Opportunity(
        title='Community Garden Cleanup',
        description='Help us clean up the community garden for the spring season.',
        category='Climate',
        location='City Park',
        user_id=user1.id,
        is_approved=True,
        approved_by='mod_user'
    )

    opp2 = Opportunity(
        title='Tech Tutoring for Seniors',
        description='Volunteer to teach seniors how to use their smartphones and computers.',
        category='Technology',
        location='Community Center',
        user_id=user2.id,
        is_approved=True,
        approved_by='mod_user'
    )

    opp3 = Opportunity(
        title='Youth Soccer Coach',
        description='Coach a youth soccer team for the summer league.',
        category='Youth',
        location='City Sports Complex',
        user_id=user1.id,
        is_approved=False
    )

    db.session.add_all([opp1, opp2, opp3])
    db.session.commit()

    print('Dummy data has been added to the database.')
