import sqlite3

conn = sqlite3.connect('promptpulse.db')
c = conn.cursor()
c.execute('SELECT id, topic, hook, scheduled_at, status FROM posts WHERE id >= 24 ORDER BY id')
posts = c.fetchall()
for p in posts:
    print(f"Post {p[0]}: topic='{p[1]}', hook='{p[2]}', sched='{p[3]}', status='{p[4]}'")
    c.execute('SELECT slide_number, layout_type, headline FROM post_slides WHERE post_id=? ORDER BY slide_number', (p[0],))
    slides = c.fetchall()
    for s in slides:
        print(f"   Slide {s[0]} ({s[1]}): {s[2]}")
