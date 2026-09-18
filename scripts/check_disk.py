import shutil
c_total, c_used, c_free = shutil.disk_usage("C:")
print(f"C: Drive Free: {c_free / (1024**3):.2f} GB")
h_total, h_used, h_free = shutil.disk_usage("H:")
print(f"H: Drive Free: {h_free / (1024**3):.2f} GB")
