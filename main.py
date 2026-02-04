from cli import admin
from database.queries import init_db

if __name__ == "__main__":
    init_db()
    print("🚆 Train Booking System started")
    #admin()
