#!/usr/bin/env python3
"""Competitive selection: pool 1000 old + 103 new -> final exactly 1000.

Per-category targets (thin boosted, thick trimmed). Within each category,
samples are ranked by a quality+diversity score:
  score = weaknesses (short answer, low concreteness, hedge-spam)
        + genericity (shared 6-gram openings across same-category samples)
        - bonus for new candidates in boosted categories (keep best new)
Dry-run prints bottom candidates per category for eyeball review; with
--apply it removes dropped OLD samples from their part files (AST segment
removal) and APPENDS kept NEW samples to matching part files.
"""
import ast, glob, importlib.util, json, re, sys
from collections import Counter, defaultdict

APPLY = "--apply" in sys.argv

RE = "\n"
def load(path, attr="SAMPLES"):
    spec = importlib.util.spec_from_file_location("m", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return getattr(mod, attr)

# ---------- load pool ----------
old = []
for k, l in enumerate(open("repository_understanding_dataset.jsonl", encoding="utf-8").read().strip().split(RE)):
    old.append({"src": "old", "line": k + 1, **json.loads(l)})
new = []
for path in ("part36_boost_a.py", "part37_boost_b.py", "part39_boost_d.py"):
    for i, s in enumerate(load(path)):
        new.append({"src": path, "idx": i, **s})
for i, s in enumerate(load("boost_staging_c_candidates.py", "CANDIDATES")):
    new.append({"src": "boost_staging_c_candidates.py", "idx": i, **s})
print(f"pool: {len(old)} old + {len(new)} new = {len(old)+len(new)}")

# ---------- targets ----------
CUR = Counter(o["category"] for o in old)
BOOST = {
    "adaptive_repository_understanding": 20, "legacy_code_detection": 30,
    "generated_file_detection": 28, "context_selection": 30, "scope_control": 28,
    "hypothesis_verification": 30, "test_structure": 30, "git_state": 30,
    "monorepo_reasoning": 28, "environment_reasoning": 29,
    "architecture_inference": 30, "missing_information": 30,
    "repository_navigation": 30, "bug_trace": 30, "authentication_structure": 30,
    "authorization_structure": 30, "configuration_discovery": 30,
    "control_flow": 29, "database_structure": 30, "deployment_structure": 30,
}
TRIM = {  # untouched cats trimmed to fit total
    "cross_layer_reasoning": 31, "feature_ownership": 31, "api_trace": 31,
    "frontend_structure": 31, "backend_structure": 30, "data_flow": 30,
    "file_relevance": 29, "repository_structure": 28, "dependency_reasoning": 29,
    "build_structure": 28, "entry_point_detection": 28,
}
# targets computed by /tmp/tcal.py: thin cats boosted with new candidates,
# thick cats trimmed; sums to exactly 1000. Regenerate via tcal if CUR changes.
T = {c: t for c, t in json.load(open("/tmp/targets.json")).items()}
total = sum(T.values())
print("current total:", sum(CUR.values()), "| explicit-target total:", total)
need = total - 1000
assert need == 0, f"targets need adjustment by {need}"
for c in sorted(T):
    have = CUR.get(c, 0)
    t = T[c]
    flag = "boost" if t > have else ("trim" if t < have else "")
    if flag:
        print(f"  {flag}: {c}: {have} -> {t} ({'+' if t>have else ''}{t-have})")
assert total == 1000, f"targets sum {total} != 1000"
for c, t in T.items():
    assert t <= CUR[c] + 10, c

# ---------- scoring ----------
ARTIFACT_PATTERNS = [
    r"[\w./-]+\.\w{1,5}\b",
    r"\b(?:src|app|apps|pages|server|packages|pkg|docs|tests?|spec|e2e|config|configs|dist|build|out|public|components?|containers?|routes|services|modules|api|lib|plugins|hooks|migrations|models|controllers|resolvers|middleware|utils|helpers|scripts|bin|cmd|deploy|infra|k8s|helm|charts)/[\w./-]+",
    r"\b[a-z][\w-]*/[a-z][\w./-]+", r"\b/[a-z][\w./{}:-]+",
    r"\b(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b", r"@[\w-]+/[\w.-]+",
    r"\b[a-z]+_[a-z][a-z0-9_]*\b", r"\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b",
    r"\b[A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)+\b",
    r"\b(?:npm|npx|pnpm|yarn|node|git|curl|psql|docker|kubectl|helm|redis-cli|nc|openssl|bash|sh|python3?|pip|cargo|go)\s+[\w-]+",
    r"\bv\d+\.\d+(?:\.\d+)?\b", r"\b[45]\d\d\b", r":\b\d{2,5}\b",
    r"\b\d+(?:ms|s|MB|GB|kb|%)\b", r"\bp\d\d\b|\bp99\b",
    r"\b[a-z][a-z0-9_-]{2,}/",
]
ARTIFACT = re.compile("|".join(f"(?:{p})" for p in ARTIFACT_PATTERNS))
HEDGE = re.compile(r"\b(might|maybe|perhaps|probably|possibly|likely)\b", re.I)

# domain vocabulary that legitimately anchors a sample without file paths
DOMAIN_TERMS = re.compile(r"\b(materialized view|read model|write model|read replica|primary key|foreign key|unique constraint|check constraint|connection pool|thread pool|event loop|service worker|service mesh|circuit breaker|dead[- ]letter|poison message|blue[- ]green|canary|rolling deploy|load balancer|reverse proxy|rate limit|idempotenc\w+|time[- ]to[- ]live|ttl|upsert|stored procedure|window function|saga pattern|outbox|mvcc|optimistic locking|pessimistic|write[- ]through|write[- ]behind|lazy loading|eager loading|n\+1|websocket|server[- ]sent events|graphql|grpc|protobuf|jsonb|oauth|oidc|saml|csrf|xss|cache invalidation|cache stampede|thundering herd|exponential backoff|backoff|jitter|fan[- ]out|split brain|quorum|tombstone|write[- ]ahead log|\bwal\b|binlog|\bcdc\b|snapshot isolation|read committed|serializable|deadlock|livelock|starvation|lock escalation|b[- ]tree|bloom filter|consistent hash\w+|shard\w+|replication|isolation level|row[- ]level security|content[- ]addressed|append[- ]only|copy[- ]on[- ]write|zero[- ]copy|backpressure|flow control|head[- ]of[- ]line|long polling|short polling|etag|last[- ]modified|if[- ]none[- ]match|content negotiation|surrogate key|edge po?p|stale[- ]while[- ]revalidate|stale[- ]if[- ]error|grace period|cascad\w+ delete|soft[- ]delet\w+|hard delet\w+|optimistic ui|optimistic update|reconciliation|hydration|resumab\w+|islands architecture|partial hydration|streaming ssr|edge runtime|middleware chain|request context|correlation id|trace context|span|structured log\w+|log aggregation|heartbeat|lease|fenc\w+ token|ballot|epoch)\b", re.I)

def conc(s):
    hits = set(m.group(0) for m in ARTIFACT.finditer(s))
    hits |= set(m.group(0).lower() for m in DOMAIN_TERMS.finditer(s))
    return len(hits)

pool = old + new
def ngrams(s, n=6):
    w = re.sub(r"[^a-z0-9]+", " ", s.lower()).split()
    return frozenset(tuple(w[i:i+n]) for i in range(len(w)-n+1))

# genericity: 6-grams shared with category-mates
cat_items = defaultdict(list)
for i, s in enumerate(pool):
    cat_items[s["category"]].append(i)
shared_g = defaultdict(set)
for c, idxs in cat_items.items():
    seen = Counter()
    gm = {i: ngrams(pool[i]["instruction"]) for i in idxs}
    for i in idxs:
        for g in gm[i]:
            seen[g] += 1
    for i in idxs:
        shared_g[i] = {g for g in gm[i] if seen[g] >= 3}

scores = {}
for i, s in enumerate(pool):
    sc = 0.0
    alen = len(s["answer"])
    if alen < 700: sc += (700 - alen) / 700.0
    cc = conc(s["answer"]) + conc(s["instruction"])
    if cc == 0: sc += 2.0
    elif cc == 1: sc += 0.7
    elif cc == 2: sc += 0.25
    hed = len(HEDGE.findall(s["answer"]))
    bec = s["answer"].lower().count("because") + s["answer"].lower().count("therefore")
    if hed >= 4 and bec == 0: sc += 0.6
    sc += len(shared_g[i]) * 0.03            # genericity penalty
    scores[i] = sc

BOOST_BONUS = 0.18
EASY_KEEP_BONUS = 0.5

# ---------- select ----------
keep, drop = {}, defaultdict(list)
precisions = []
for c, idxs in cat_items.items():
    t = T[c]
    boosted = T[c] > CUR[c]

    def retention(i):
        # higher = keep. Primary term is quality; bonuses are explicit priorities:
        #   +EASY_KEEP_BONUS shields easies (band floor is a hard constraint)
        #   +BOOST_BONUS favors new candidates ONLY in categories being boosted
        # Tiebreak: longer answers are more concrete on average.
        r = -scores[i]
        if boosted and pool[i]["src"] != "old":
            r += BOOST_BONUS
        if pool[i]["difficulty"] == "easy":
            r += EASY_KEEP_BONUS
        return (r, len(pool[i]["answer"]))

    # retention: higher = keep (quality first, bonuses shield easy + boost new)
    idxs_sorted = sorted(idxs, key=retention, reverse=True)
    keeps = idxs_sorted[:t]
    dset = set(idxs_sorted[t:])
    keep[c] = keeps
    for i in dset:
        drop[c].append(i)

ndrop = sum(len(v) for v in drop.values())
nnew_kept = sum(1 for c in keep for i in keep[c] if pool[i]["src"] != "old")
nold_dropped = sum(1 for c in drop for i in drop[c] if pool[i]["src"] == "old")
print(f"drop total: {ndrop} (old {nold_dropped}, new {ndrop-nold_dropped}); new kept: {nnew_kept}")

final = sorted([i for c in keep for i in keep[c]], key=lambda i: (pool[i]["src"] == "old" and 0 or 1, pool[i].get("line", 10**9)))
print("final:", len(final))
dfinal = Counter(pool[i]["difficulty"] for i in final)
print("final difficulty:", dict(dfinal))
band_ok = True
for d, (lo, hi) in {"easy": (70,150), "medium": (160,300), "hard": (340,530), "expert": (180,330)}.items():
    frac = dfinal[d]
    ok = lo <= frac <= hi
    band_ok = band_ok and ok
    print(f"  {d}: {frac} {'OK' if ok else 'VIOLATION'}")


def easy_count(idxs):
    return sum(1 for i in idxs if pool[i]["difficulty"] == "easy" and pool[i]["src"] == "old")

print("\n--- review: dropped per category (weakest shown) ---")
for c in sorted(drop):
    items = drop[c]
    e_dropped = sum(1 for i in items if pool[i]["difficulty"] == "easy")
    msg = []
    for i in items[:6]:
        s = pool[i]
        tag = "NEW" if s["src"] != "old" else f"old#{s['line']}"
        msg.append(f"{tag}[{s['difficulty'][:1]}s{scores[i]:.2f}] {s['instruction'][:52]!r}")
    print(f"{c} (drop {len(items)}, easy {e_dropped}):")
    for m in msg: print("   ", m)
print("\nband_ok:", band_ok)

if not APPLY:
    json.dump({
        "final": [{"cat": pool[i]["category"], "src": pool[i]["src"],
                   "line": pool[i].get("line"), "idx": pool[i].get("idx"),
                   "instruction": pool[i]["instruction"],
                   "difficulty": pool[i]["difficulty"]} for i in final]
    }, open("/tmp/selection.json", "w"))
    print("\nDRY RUN — rerun with --apply to mutate part files + write final")
else:
    # Map old drops to part files by scanning parts for the instruction text
    drop_old = [i for c in drop for i in drop[c] if pool[i]["src"] == "old"]
    drop_instr = {pool[i]["instruction"] for i in drop_old}
    kept_new = [i for c in keep for i in keep[c] if pool[i]["src"] != "old"]
    import shutil, datetime
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.rmtree(f"/tmp/parts_backup_{stamp}", ignore_errors=True)
    shutil.copytree(".", f"/tmp/parts_backup_{stamp}", ignore=shutil.ignore_patterns("__pycache__", "repository_understanding_dataset.jsonl"))
    # remove old samples by matching instruction text inside part files
    part_files = [pf for pf in sorted(glob.glob("part*_*.py")) if pf != "boost_staging_c_candidates.py"]
    for pf in part_files:
        if pf in ("part36_boost_a.py", "part37_boost_b.py", "part39_boost_d.py"):
            continue
        src = open(pf, encoding="utf-8").read()
        tree = ast.parse(src)
        assign = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SAMPLES"][0]
        segs = []
        hit = False
        for elt in assign.value.elts:
            seg = ast.get_source_segment(src, elt)
            d = ast.literal_eval(seg)
            if d["instruction"] in drop_instr:
                hit = True
                continue
            segs.append(seg)
        if hit:
            body = ",\n".join(segs)
            src2 = src[:assign.value.elts[0].lineno-1]  # crude rebuild: reconstruct whole file tail
            # safer: full re-render
            header = src[:src.index("[") + 1]
            rendered = header + "\n" + ",\n".join("    " + s.replace("\n", "\n    ") for s in segs)
            rendered = src[:src.index("[") + 1] + "\n" + ",\n".join(segs) + "\n]\n"
            ast.parse(rendered)
            open(pf, "w", encoding="utf-8").write(rendered)
    # append kept new samples to category-matched part files.
    # Canonical category homes are part01..part35 ONLY; staging part36/37/39
    # get drained below, so they must never be chosen as append targets.
    CATFILE = {}
    for pf in part_files:
        if pf[:6] >= "part36":
            continue
        ns = load(pf)
        if ns:
            CATFILE.setdefault(ns[0]["category"], pf)
    by_cat = defaultdict(list)
    for i in kept_new:
        by_cat[pool[i]["category"]].append(pool[i])
    missing = [c for c in by_cat if c not in CATFILE]
    assert not missing, f"no canonical part for categories: {missing}"
    def esc(x): return x.replace("\\", "\\\\").replace('"', '\\"')  # U+2019 stays as-is: 7,464 of them already live in the pool and both validator allowlists include them
    # IMPORTANT: mirror the removal loop — only re-parse segs when this
    # file had drops. Re-slicing an untouched file is what corrupts it
    # (src.index("[") on unmodified sources bites on bracketed comments).
    for c, items in by_cat.items():
        pf = CATFILE[c]
        src = open(pf, encoding="utf-8").read()
        tree = ast.parse(src)
        assign = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SAMPLES"][0]
        elts = assign.value.elts
        hit = False
        for elt in elts:
            seg0 = ast.get_source_segment(src, elt)
            if seg0 and ast.literal_eval(seg0)["instruction"] in drop_instr:
                hit = True
                break
        seg_news = [("    {" + "\n" +
                     f'        "instruction": "{esc(o["instruction"])}",\n' +
                     f'        "reasoning": "{esc(o["reasoning"])}",\n' +
                     f'        "answer": "{esc(o["answer"])}",\n' +
                     f'        "category": "{c}",\n' +
                     f'        "difficulty": "{o["difficulty"]}",\n' +
                     "    }") for o in items]
        if hit:
            segs = [ast.get_source_segment(src, elt) for elt in elts] + seg_news
            rendered = src[:src.index("[") + 1] + "\n" + ",\n".join(segs) + "\n]\n"
            ast.parse(rendered)
            open(pf, "w", encoding="utf-8").write(rendered)
        else:
            close = src.rfind("]")
            prev = src[:close].rstrip()
            if prev.endswith("}"):
                prev += ","
            src2 = prev + "\n" + ",\n".join(seg_news) + "\n" + "]"
            ast.parse(src2)
            open(pf, "w", encoding="utf-8").write(src2)
    # drain staging: every kept staging sample now lives in its canonical
    # part; empties prevent build.py from double-counting them.
    for pf in ("part36_boost_a.py", "part37_boost_b.py", "part39_boost_d.py"):
        open(pf, "w", encoding="utf-8").write(
            '"""Staging pool drained by select_final.py --apply.\n'
            "Kept entries were moved to their canonical category parts.\"\"\"\n"
            "SAMPLES = []\n")
    print("APPLIED. backup at /tmp/parts_backup_" + stamp)
    json.dump({"kept_new": nnew_kept, "dropped_old": nold_dropped}, open("/tmp/applied.json", "w"))
