import sqlite3

conn = sqlite3.connect('promptpulse.db')
c = conn.cursor()
c.execute('SELECT id, topic, status, scheduled_at FROM posts ORDER BY id')
posts = c.fetchall()
print(f'Total posts: {len(posts)}')
for p in posts:
    c.execute('SELECT slide_number, layout_type, headline, image_path FROM post_slides WHERE post_id=? ORDER BY slide_number', (p[0],))
    slides = c.fetchall()
    print(f'Post {p[0]}: "{p[1]}" | status={p[2]} | sched={p[3]} | slides={len(slides)}')
    for s in slides:
        print(f'   Slide {s[0]} ({s[1]}): {s[3]}')
