#!/usr/bin/env python3
# Phase 4, step 1: replace standalone imaginary-unit i/j with 1i/1j in tftb-0.3.
# Conservative: only on lines listed by the mlint scan, and only when the char
# is (a) not part of a bigger identifier and (b) immediately preceded by an
# operator/paren/equals -- i.e. clearly the imaginary unit, never a variable.
import re, sys

M = r"D:\TOOLBOX\tftb-0.3\mfiles"
LIST = r"D:\Source\hermes-dir\tftb03_migration\logs\p4\ij.txt"

# parse flagged sites: file, line (skip the trailing BY_MSG summary lines)
sites = {}  # file -> set(line)
with open(LIST, encoding="utf-8") as f:
    for raw in f:
        parts = raw.rstrip("\n").split("\t")
        if len(parts) < 3:
            continue
        fn, ln = parts[0], parts[2]
        if fn in ("mfiles", "tests", "demos", "scripts"):
            continue
        if not ln.strip().isdigit():
            continue
        sites.setdefault(fn, set()).add(int(ln))

pat = re.compile(r"([+*\-/(,=]\s*)([ij])(?![A-Za-z0-9_.])")
# the required preceding operator/paren/equals/comma guarantees the i/j is
# not the tail of an identifier; the lookahead guarantees it is not the head
# of one (or a .method / _ member). Only lines mlint already flagged are touched.

dry = "--dry" in sys.argv
total = 0
for fn, lines in sorted(sites.items()):
    path = M + "\\" + fn
    with open(path, encoding="utf-8") as f:
        ls = f.readlines()
    changed = 0
    for ln in lines:
        idx = ln - 1
        if idx < 0 or idx >= len(ls):
            continue
        orig = ls[idx]
        new = pat.sub(r"\g<1>1\g<2>", orig)
        if new != orig:
            if not dry:
                ls[idx] = new
            changed += 1
            total += 1
            if dry:
                print(f"{fn}:{ln}: {orig.rstrip()}  ->  {new.rstrip()}")
    if changed and not dry:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(ls)
    if changed:
        print(f"{fn}: {changed} line(s) changed")

print(f"TOTAL lines changed: {total}  (dry={dry})")
