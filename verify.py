"""Verify the release payload and reject unmanifested files."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
IGNORED={".git", ".venv", "venv", "outputs", "__pycache__"}
def main():
    expected=json.loads((ROOT/"SHA256SUMS.json").read_text())["files"]
    actual={str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and not any(x in IGNORED for x in p.relative_to(ROOT).parts) and p.name != "SHA256SUMS.json"}
    assert actual==set(expected), "Missing or unmanifested payload files"
    for name,digest in expected.items():
        path=ROOT/name
        assert not path.is_symlink(), "Symlink forbidden"
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest, "Checksum mismatch: "+name
    print(json.dumps({"status":"PASS","files":len(expected)}))
if __name__=="__main__":main()
