import glob, os, time

files = glob.glob('media/slides/*.*')
now = time.time()
recent = [f for f in files if now - os.path.getmtime(f) < 300]
print(f"Total files: {len(files)}, generated in last 5 minutes: {len(recent)}")
for f in sorted(recent, key=os.path.getmtime, reverse=True)[:15]:
    age = int(now - os.path.getmtime(f))
    print(f"  {os.path.basename(f)} ({age}s ago)")
