"""Copy a freshly built mod into the git repository, keeping the repo's own files.

usage: python3 publish.py <built_mod_dir> <repo_dir> [preview.jpg]
Everything at the repo root is replaced by the build except .git, tools/ and LICENSE.

Leader portraits are managed by the repo owner by hand on GitHub, so they are protected:
  - the folders Images/LeaderIcons and Images.Portraits,
  - the owner's packed portrait atlas at the repo root (Portraits.atlas and its
    Portraits*.png pages),
are left exactly as they are in the repo, and the build's copies of them (if any) are
ignored. The faction music folders (music/factions/<Nation>/) are kept the same way, because
they are the source the build reads tracks from. If a packed portrait atlas is kept, "Portraits" is added to the build's
Atlases.json so Unciv loads it. Nothing else is touched: every other file still comes
from the build.
"""
import fnmatch, os, shutil, sys, tempfile

KEEP = {".git", "tools", "LICENSE", "preview.jpg"}
PROTECTED_DIRS = ["Images/LeaderIcons", "Images.Portraits",
                  "music/factions"]   # the owner's faction-music slots: the build flattens copies into music/
PROTECTED_FILES = ["Portraits.atlas", "Portraits*.png"]      # repo-root patterns
PORTRAIT_ATLAS = "Portraits"


def protected_file(name):
    return any(fnmatch.fnmatchcase(name, pat) for pat in PROTECTED_FILES)


def read_atlases(path):
    """Atlases.json is a bare list like [RaceUnits,WarcraftIcons,game]."""
    if not os.path.isfile(path):
        return []
    text = open(path, encoding="utf-8").read().strip().lstrip("[").rstrip("]")
    return [x.strip().strip('"') for x in text.split(",") if x.strip()]


src, repo = sys.argv[1], sys.argv[2]
os.makedirs(repo, exist_ok=True)

# 1. set the owner's portrait files aside
stash = tempfile.mkdtemp(prefix="publish-protected-")
for rel in PROTECTED_DIRS:
    p = os.path.join(repo, rel)
    if os.path.isdir(p):
        shutil.move(p, os.path.join(stash, rel.replace("/", "__")))
kept_files = [n for n in os.listdir(repo) if os.path.isfile(os.path.join(repo, n)) and protected_file(n)]
for n in kept_files:
    shutil.move(os.path.join(repo, n), os.path.join(stash, n))

# 2. replace the repo root with the build
for name in os.listdir(repo):
    if name in KEEP:
        continue
    p = os.path.join(repo, name)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
for name in os.listdir(src):
    s, d = os.path.join(src, name), os.path.join(repo, name)
    shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)

# 3. drop any build copies of the protected items, then restore the owner's
for rel in PROTECTED_DIRS:
    built = os.path.join(repo, rel)
    if os.path.isdir(built):
        shutil.rmtree(built)
    saved = os.path.join(stash, rel.replace("/", "__"))
    if os.path.isdir(saved):
        os.makedirs(os.path.dirname(built), exist_ok=True)
        shutil.move(saved, built)
for n in os.listdir(repo):
    if os.path.isfile(os.path.join(repo, n)) and protected_file(n):
        os.remove(os.path.join(repo, n))
for n in kept_files:
    shutil.move(os.path.join(stash, n), os.path.join(repo, n))
shutil.rmtree(stash, ignore_errors=True)

# 4. make sure Unciv loads the kept portrait atlas (and doesn't list one that isn't there)
atlases_path = os.path.join(repo, "Atlases.json")
atlases = [a for a in read_atlases(atlases_path) if a != PORTRAIT_ATLAS]
if os.path.isfile(os.path.join(repo, PORTRAIT_ATLAS + ".atlas")):
    atlases.append(PORTRAIT_ATLAS)
if atlases:
    with open(atlases_path, "w", encoding="utf-8") as f:
        f.write("[" + ",".join(sorted(atlases)) + "]")

if len(sys.argv) > 3:
    shutil.copy2(sys.argv[3], os.path.join(repo, "preview.jpg"))
# copy the build tools themselves into tools/
here = os.path.dirname(os.path.abspath(__file__))
tools = os.path.join(repo, "tools")
shutil.rmtree(tools, ignore_errors=True)
shutil.copytree(here, tools, ignore=shutil.ignore_patterns("__pycache__", "*.class", "svg", "node_modules", "music"))
print("published", src, "->", repo, "| kept portraits:", len(kept_files), "files +",
      sum(os.path.isdir(os.path.join(repo, r)) for r in PROTECTED_DIRS), "folders")
