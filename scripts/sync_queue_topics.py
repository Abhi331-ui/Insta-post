import sqlite3

TOPIC_MAP = {
    25: "1. Bolt.new In-Browser Runtime Breakthrough",
    26: "2. OpenAI Canvas Interface vs Traditional Editors",
    27: "3. Cursor Composer 20-File Orchestration",
    28: "4. v0.dev Next.js Component Generation",
    29: "5. Claude 3.5 Sonnet Artifacts for Productivity",
    30: "6. Perplexity Pro Computer Interaction Workflows",
    31: "7. NotebookLM Dual-Host Audio Synthesis",
    32: "8. Devin AI Autonomous Software Engineering Review",
    33: "9. Replit Agent Full-Stack Autonomous Deployments",
    34: "10. Supabase AI Auto-Migrate Vector Search",
}

conn = sqlite3.connect("promptpulse.db")
c = conn.cursor()

for post_id, topic_name in TOPIC_MAP.items():
    c.execute("UPDATE topic_queue SET topic = ?, status = 'ready' WHERE post_id = ?", (topic_name, post_id))

conn.commit()
print("Synchronized topic_queue records successfully.")

c.execute("SELECT id, day_index, topic, scheduled_date, post_id FROM topic_queue WHERE post_id >= 25 ORDER BY id")
for r in c.fetchall():
    print(r)

conn.close()
