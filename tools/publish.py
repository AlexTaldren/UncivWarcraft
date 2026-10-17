"""Copy a freshly built mod into the git repository, keeping the repo's own files.

usage: python3 publish.py <built_mod_dir> <repo_dir> [preview.jpg]
Everything at the repo root is replaced by the build except .git, tools/ and LICENSE.
Folders in PROTECTED are owned by the repo owner (edited by hand on GitHub): they are
left exactly as they are in the repo, and the build's copy of them (if any) is ignored.
"""
import os, shutil, sys, tempfile

KEEP = {".git", "tools", "LICENSE", "preview.jpg"}
PROTECTED = ["Images/LeaderIcons"]      # leader portraits: managed by the owner, never overwritten
src, repo = sys.argv[1], sys.argv[2]
os.makedirs(repo, exist_ok=True)
stash = tempfile.mkdtemp(prefix="publish-protected-")
for rel in PROTECTED:
    p = os.path.join(repo, rel)
    if os.path.isdir(p):
        shutil.move(p, os.path.join(stash, rel.replace("/", "__")))
for name in os.listdir(repo):
    if name in KEEP:
        continue
    p = os.path.join(repo, name)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
for name in os.listdir(src):
    s, d = os.path.join(src, name), os.path.join(repo, name)
    shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)
for rel in PROTECTED:
    built = os.path.join(repo, rel)
    if os.path.isdir(built):
        shutil.rmtree(built)                # the build's version never replaces the owner's
    saved = os.path.join(stash, rel.replace("/", "__"))
    if os.path.isdir(saved):
        os.makedirs(os.path.dirname(built), exist_ok=True)
        shutil.move(saved, built)
shutil.rmtree(stash, ignore_errors=True)
if len(sys.argv) > 3:
    shutil.copy2(sys.argv[3], os.path.join(repo, "preview.jpg"))
# copy the build tools themselves into tools/
here = os.path.dirname(os.path.abspath(__file__))
tools = os.path.join(repo, "tools")
shutil.rmtree(tools, ignore_errors=True)
shutil.copytree(here, tools, ignore=shutil.ignore_patterns("__pycache__", "*.class", "svg", "node_modules", "music"))
print("published", src, "->", repo)
