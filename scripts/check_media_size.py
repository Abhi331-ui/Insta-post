import os, glob

d = r"C:\Users\USER\.gemini\antigravity-ide\brain\fac18f0b-dc5a-4917-bfdb-5b5d12db40b7\.tempmediaStorage"
if os.path.exists(d):
    files = os.listdir(d)
    sz = sum(os.path.getsize(os.path.join(d, f)) for f in files)
    print(f"tempmediaStorage has {len(files)} files, total {sz / (1024**2):.2f} MB")

d2 = r"C:\Users\USER\.gemini\antigravity-ide\brain\fac18f0b-dc5a-4917-bfdb-5b5d12db40b7"
files2 = [f for f in os.listdir(d2) if f.endswith(('.png', '.webp', '.jpg'))]
sz2 = sum(os.path.getsize(os.path.join(d2, f)) for f in files2)
print(f"brain dir media has {len(files2)} files, total {sz2 / (1024**2):.2f} MB")
