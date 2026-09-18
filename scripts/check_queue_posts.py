import sqlite3

conn = sqlite3.connect("promptpulse.db")
c = conn.cursor()
c.execute("""
    SELECT q.id, q.day_index, q.topic, q.scheduled_date, q.post_id, p.topic, 
           (SELECT count(*) FROM post_slides WHERE post_id=q.post_id),
           (SELECT image_path FROM post_slides WHERE post_id=q.post_id AND slide_number=1)
    FROM topic_queue q
    LEFT JOIN posts p ON p.id = q.post_id
    ORDER BY q.id
""")
for r in c.fetchall():
    print(r)
