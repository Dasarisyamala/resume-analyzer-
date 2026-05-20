from app import app
from database import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Add user_id to resumes
        try:
            db.session.execute(text('ALTER TABLE resumes ADD COLUMN user_id INTEGER'))
            print("Successfully added 'user_id' column to 'resumes' table.")
        except Exception as e:
            print(f"Failed to add 'user_id' to 'resumes': {e}")

        # Add notifications to users
        try:
            db.session.execute(text("ALTER TABLE users ADD COLUMN notifications TEXT DEFAULT '[]'"))
            print("Successfully added 'notifications' column to 'users' table.")
        except Exception as e:
            print(f"Failed to add 'notifications' to 'users': {e}")

        db.session.commit()
        print("Migration process complete.")

if __name__ == "__main__":
    migrate()
