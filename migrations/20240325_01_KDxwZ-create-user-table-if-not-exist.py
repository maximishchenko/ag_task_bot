"""Create user table if not exist."""

from yoyo import step

__depends__: dict = {}

steps = [
    step(
        'CREATE TABLE IF NOT EXISTS "user" \
            ("id" INTEGER NOT NULL, "chat_id" INTEGER NOT NULL UNIQUE,\
            "first_name" VARCHAR(255) NOT NULL, "last_name" VARCHAR(255), \
            "username"	VARCHAR(255), "status" INTEGER NOT NULL DEFAULT (0), \
            "tehn"	VARCHAR(255), PRIMARY KEY("id"));',
        'DROP TABLE "user"',
    )
]
