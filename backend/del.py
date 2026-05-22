import sqlite3

conn = sqlite3.connect(
    "telemetry.db"
)

cursor = conn.cursor()

cursor.execute(
    "PRAGMA table_info(alerts)"
)

columns = [

    c[1]

    for c in cursor.fetchall()

]

print(columns)


cursor.execute(
    "SELECT * FROM alerts"
)

rows = cursor.fetchall()

for row in rows:

    print(

        dict(
            zip(
                columns,
                row
            )
        )

    )

conn.close()