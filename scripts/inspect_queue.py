import sqlite3

conn = sqlite3.connect('promptpulse.db')
c = conn.cursor()
c.execute("SELECT id, day_index, topic, scheduled_date, status, post_id FROM topic_queue ORDER BY id")
for r in c.fetchall():
    print(r)
