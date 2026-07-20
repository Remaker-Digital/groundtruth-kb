import hashlib
import sys

path = sys.argv[1]
with open(path, "rb") as f:
    data = f.read()
header = f"blob {len(data)}\0".encode("ascii")
digest = hashlib.sha1(header + data).hexdigest()
print(f"{path}\t{len(data)}\t{digest}")
