import os, glob

temp_dir = os.environ.get("TEMP", r"C:\Users\USER\AppData\Local\Temp")
print(f"Checking TEMP dir: {temp_dir}")
total_temp = 0
for root, dirs, files in os.walk(temp_dir):
    for f in files:
        fp = os.path.join(root, f)
        try:
            total_temp += os.path.getsize(fp)
        except:
            pass
print(f"Total TEMP size: {total_temp / (1024**3):.2f} GB")

# Also check artifacts temp media storage
brain_dir = r"C:\Users\USER\.gemini\antigravity-ide\brain"
brain_size = 0
for root, dirs, files in os.walk(brain_dir):
    for f in files:
        fp = os.path.join(root, f)
        try:
            brain_size += os.path.getsize(fp)
        except:
            pass
print(f"Total Brain size: {brain_size / (1024**3):.2f} GB")
