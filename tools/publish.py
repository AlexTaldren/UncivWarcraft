"""Copy a freshly built mod into the git repository, keeping the repo's own files.

usage: python3 publish.py <built_mod_dir> <repo_dir> [preview.jpg]
Everything at the repo root is replaced by the build except .git, tools/ and LICENSE.
"""
import os, shutil, sys

KEEP = {".git", "tools", "LICENSE", "preview.jpg"}
src, repo = sys.argv[1], sys.argv[2]
os.makedirs(repo, exist_ok=True)
for name in os.listdir(repo):
    if name in KEEP:
        continue
    p = os.path.join(repo, name)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
for name in os.listdir(src):
    s, d = os.path.join(src, name), os.path.join(repo, name)
    shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)
if len(sys.argv) > 3:
    shutil.copy2(sys.argv[3], os.path.join(repo, "preview.jpg"))
# copy the build tools themselves into tools/
here = os.path.dirname(os.path.abspath(__file__))
tools = os.path.join(repo, "tools")
shutil.rmtree(tools, ignore_errors=True)
shutil.copytree(here, tools, ignore=shutil.ignore_patterns("__pycache__", "*.class", "svg", "node_modules"))
print("published", src, "->", repo)
