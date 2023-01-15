#!/usr/bin/env python3

import json
import sqlite3

from datetime import datetime


def store_reports(db_location: str, reports: list[dict]):
    # Connect to or create a new SQLite database
    conn = sqlite3.connect(db_location)

    # Create a table with timestamp and text columns
    conn.execute('''CREATE TABLE IF NOT EXISTS reports
                     (timestamp TIMESTAMP, text BLOB)''')

    # Convert the JSON document to a string
    json_str = json.dumps(reports)

    # Get the current UTC timestamp
    now = datetime.utcnow()

    # Insert the JSON document and timestamp into the table
    conn.execute("INSERT INTO reports (timestamp, text) VALUES (?, ?)", (now, json_str))

    # Commit the changes to the database
    conn.commit()

    # Close the connection to the database
    conn.close()


def read_all_reports_from(db_location: str, ts: datetime):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_location)
    c = conn.cursor()

    # Select all rows from the table with timestamp greater than or equal to the first day of the current month
    c.execute("SELECT * FROM reports WHERE timestamp >= ?", (ts,))

    for row in c:
        timestamp, text = row
        reports = json.loads(text)

        yield (timestamp, reports)

    # Close the connection to the database
    conn.close()
