from models import db, User
from app import app
from werkzeug.security import generate_password_hash

MARKETERS = ['abdulla', 'salem', 'moad', 'riyad', 'kilani']

with app.app_context():
    db.drop_all()
    db.create_all()

    # Admin
    db.session.add(User(
        name='Murad', username='murad',
        password_hash=generate_password_hash('admin123'),
        role='admin'))

    # Marketers (default pwd = 123456)
    for m in MARKETERS:
        db.session.add(User(
            name=m.capitalize(), username=m,
            password_hash=generate_password_hash('123456'),
            role='marketer'))

    db.session.commit()
    print('Database initialised ✨')
