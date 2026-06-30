#!/usr/bin/env python3
"""
Replace JS-generated link grids on homepage with static HTML links
to ALL salary amounts (step 100). This ensures Google can crawl them.
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(BASE, "index.html")

# All amounts: 1000 to 10000, step 100
amounts = list(range(1000, 10001, 100))


def format_amount(n):
    s = str(n)
    if len(s) <= 3:
        return s
    parts = []
    while s:
        parts.append(s[-3:])
        s = s[:-3]
    return "\u00a0".join(reversed(parts))  # non-breaking space


def make_link(amount, suffix, label):
    return (
        f'<a href="/{amount}-euros-{suffix}/" class="block rounded-xl border border-slate-200 bg-white p-3 text-center hover:border-brand-300 hover:shadow-sm transition-all">'
        f'<span class="block text-lg font-bold text-slate-900">{format_amount(amount)} \u20ac</span>'
        f'<span class="block text-xs text-slate-500">{label}</span>'
        f"</a>"
    )


# Build static HTML for brut-en-net links
brut_links = "\n                    ".join(
    make_link(a, "brut-en-net", "brut en net") for a in amounts
)

# Build static HTML for net-en-brut links
net_links = "\n                    ".join(
    make_link(a, "net-en-brut", "net en brut") for a in amounts
)

# Read index.html
with open(INDEX, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace empty liens-montants div with static brut links
html = re.sub(
    r'(<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3" id="liens-montants">)\s*(</div>)',
    rf"\1\n                    {brut_links}\n                \2",
    html,
)

# 2. Replace empty liens-montants-net div with static net links
html = re.sub(
    r'(<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3" id="liens-montants-net">)\s*(</div>)',
    rf"\1\n                    {net_links}\n                \2",
    html,
)

# 3. Remove populateLiensInternes() call from init (keep populateMontantsTable)
html = html.replace(
    "populateMontantsTable();\n                populateLiensInternes();",
    "populateMontantsTable();",
)

with open(INDEX, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Done! Injected {len(amounts)} brut-en-net + {len(amounts)} net-en-brut static links")
print(f"Total: {len(amounts) * 2} static links added to homepage")
print("Removed populateLiensInternes() call from init")
