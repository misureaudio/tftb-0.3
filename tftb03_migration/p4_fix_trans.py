#!/usr/bin/env python3
# Phase 4, step 2: replace transpose ' with element-wise transpose .' in tftb-0.3.
# Only on lines the mlint scan flagged. Rule: replace a ' that is NOT already
# preceded by '.' (i.e. a plain transpose) with .'. No string literals exist on
# these math lines, and the operands were verified real-valued, so this is
# behavior-identical and prevents a silent-conjugate bug on complex data.
import re, sys

BASE = r"D:\TOOLBOX\tftb-0.3"
LIST = r"D:\Source\hermes-dir\tftb03_migration\logs\p4\trans.txt"

sites = {}  # (sub,file) -> set(line)
with open(LIST, encoding="utf-8") as f:
    for raw in f:
        parts = raw.rstrip("\n").split("\t")
        if len(parts) < 3:
            continue
        fn, sub, ln = parts[0], parts[1], parts[2]
        if sub not in ("mfiles", "tests", "demos", "scripts"):
            continue
        if not ln.strip().isdigit():
            continue
        sites.setdefault((sub, fn), set()).add(int(ln))

dry = "--dry" in sys.argv
total = 0
for (sub, fn), lines in sorted(sites.items()):
    path = BASE + "\\" + sub + "\\" + fn
    with open(path, encoding="utf-8") as f:
        ls = f.readlines()
    changed = 0
    for ln in sorted(lines):
        idx = ln - 1
        if idx < 0 or idx >= len(ls):
            continue
        orig = ls[idx]
        # replace ' not preceded by '.'  ->  . '   (transpose -> element-wise)
        new = re.sub(r"(?<!\.)'", r".'", orig)
        if new != orig:
            if not dry:
                ls[idx] = new
            changed += 1
            total += 1
            if dry:
                print(f"{sub}/{fn}:{ln}: {orig.rstrip()}  ->  {new.rstrip()}")
    if changed and not dry:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(ls)
    if changed:
        print(f"{sub}/{fn}: {changed} line(s) changed")

print(f"TOTAL lines changed: {total}  (dry={dry})")
