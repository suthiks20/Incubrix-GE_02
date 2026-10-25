import hashlib, json, logging, re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()

def sha(text, n=16):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]

def shingles(text, k=4):
    w = norm(text).split()
    if len(w) < k:
        return {" ".join(w)}
    return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}

def jaccard(a, b):
    A, B = shingles(a), shingles(b)
    return len(A & B) / len(A | B) if A and B else 0.0

def get_logger(log_path):
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    lg = logging.getLogger("engine:" + str(log_path))
    if not lg.handlers:
        lg.setLevel(logging.INFO)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        lg.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        lg.addHandler(sh)
    return lg

class Timer:
    def __enter__(self):
        self.t0 = time.time(); return self
    def __exit__(self, *a):
        self.seconds = time.time() - self.t0
