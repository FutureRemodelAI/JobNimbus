from app import create_app
from app import database

app = create_app()

with app.app_context():
    database.db.create_all()  # This creates all tables from your models

if __name__ == "__main__":
    app.run(debug=True)
