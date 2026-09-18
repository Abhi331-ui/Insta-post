import sqlite3

conn = sqlite3.connect("promptpulse.db", timeout=60)
c = conn.cursor()

# 1. Delete obsolete queue items 1..20
c.execute("DELETE FROM topic_queue WHERE id < 21")
print("Deleted obsolete topic_queue rows (id < 21)")

# 2. Re-index day_index for remaining items 21..30 to be strictly 1..10
c.execute("SELECT id, post_id, scheduled_date FROM topic_queue ORDER BY scheduled_date ASC")
remaining = c.fetchall()
print(f"Remaining active queue items: {len(remaining)}")

for idx, (qid, pid, sdate) in enumerate(remaining):
    c.execute("UPDATE topic_queue SET day_index = ?, status = 'ready' WHERE id = ?", (idx + 1, qid))

# 3. Clean up old obsolete test posts (id between 4 and 23)
c.execute("DELETE FROM scheduled_posts WHERE post_id BETWEEN 4 AND 23")
c.execute("DELETE FROM post_slides WHERE post_id BETWEEN 4 AND 23")
c.execute("DELETE FROM posts WHERE id BETWEEN 4 AND 23")
print("Cleaned up obsolete test posts (IDs 4 to 23)")

conn.commit()

# Verify remaining posts and queue
c.execute("SELECT id, topic, status, scheduled_at FROM posts ORDER BY id")
print("\nRemaining Posts:")
for p in c.fetchall():
    print(f"  Post {p[0]}: '{p[1]}' | status={p[2]} | sched={p[3]}")

c.execute("SELECT id, day_index, topic, scheduled_date, status, post_id FROM topic_queue ORDER BY scheduled_date ASC")
print("\nActive Topic Queue:")
for q in c.fetchall():
    print(f"  Day {q[1]}: '{q[2]}' | sched={q[3]} | post_id={q[5]} | status={q[4]}")

conn.close()
