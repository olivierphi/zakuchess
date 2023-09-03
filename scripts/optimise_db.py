def optimise_db():
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA journal_mode=WAL;")


if __name__ == "__main__":
    from django import setup

    setup()

    optimise_db()
