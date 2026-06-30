#!/usr/bin/env python3
"""
Remove X50 salary pages (keep only step 100 instead of step 50).
- Replace X50 pages with redirect HTML
- Update sitemap.xml to remove X50 URLs
- Update "montants proches" links on remaining pages
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# All amounts that will exist after cleanup (step 100 from 1000 to 10000)
valid_amounts = list(range(1000, 10001, 100))
valid_amounts_set = set(valid_amounts)

# X50 amounts to redirect (only exist from 1050 to 4950)
x50_amounts = list(range(1050, 5000, 100))


def format_amount(n):
    """Format number with French spacing: 1500 -> '1 500', 10000 -> '10 000'"""
    s = str(n)
    if len(s) <= 3:
        return s
    parts = []
    while s:
        parts.append(s[-3:])
        s = s[:-3]
    return " ".join(reversed(parts))


def get_neighbors(amount):
    """Get up to 4 neighbors for a given amount (±100, ±200)"""
    candidates = [amount - 200, amount - 100, amount + 100, amount + 200]
    return [a for a in candidates if a in valid_amounts_set]


# ── Step 1: Create redirect pages ──────────────────────────────────────

REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Redirection — {amount_fmt}\u20ac {label}</title>
<link rel="canonical" href="https://salairebrutonet.com/{target_slug}/">
<meta http-equiv="refresh" content="0; url=/{target_slug}/">
<meta name="robots" content="noindex, follow">
</head>
<body>
<p>Cette page a \xe9t\xe9 d\xe9plac\xe9e vers <a href="/{target_slug}/">{target_fmt}\u20ac {label}</a>.</p>
</body>
</html>"""

print("Step 1: Creating redirect pages for X50 amounts...")
redirect_count = 0
for amount in x50_amounts:
    target = amount + 50  # 1050 -> 1100, 1150 -> 1200, etc.
    for suffix, label in [("brut-en-net", "brut en net"), ("net-en-brut", "net en brut")]:
        dir_path = os.path.join(BASE, f"{amount}-euros-{suffix}")
        file_path = os.path.join(dir_path, "index.html")
        target_slug = f"{target}-euros-{suffix}"

        html = REDIRECT_TEMPLATE.format(
            amount_fmt=format_amount(amount),
            target_slug=target_slug,
            target_fmt=format_amount(target),
            label=label,
        )

        if os.path.exists(dir_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            redirect_count += 1
        else:
            print(f"  [WARN] Directory not found: {dir_path}")

print(f"  Created {redirect_count} redirect pages")


# ── Step 2: Update sitemap.xml ─────────────────────────────────────────

print("\nStep 2: Updating sitemap.xml...")
sitemap_path = os.path.join(BASE, "sitemap.xml")
with open(sitemap_path, "r", encoding="utf-8") as f:
    sitemap = f.read()

removed_count = 0
for amount in x50_amounts:
    for suffix in ["brut-en-net", "net-en-brut"]:
        url = f"https://salairebrutonet.com/{amount}-euros-{suffix}/"
        pattern = r"\s*<url>\s*<loc>" + re.escape(url) + r"</loc>.*?</url>"
        new_sitemap = re.sub(pattern, "", sitemap, flags=re.DOTALL)
        if new_sitemap != sitemap:
            removed_count += 1
            sitemap = new_sitemap

with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(sitemap)

remaining = sitemap.count("<loc>")
print(f"  Removed {removed_count} URLs from sitemap ({remaining} remaining)")


# ── Step 3: Update "montants proches" on remaining pages ───────────────

print("\nStep 3: Updating 'Montants proches' links on remaining pages...")

LINK_TEMPLATE = '<a href="/{slug}/" class="block rounded-xl border border-slate-200 bg-white p-3 text-center hover:border-brand-300 hover:shadow-sm transition-all"><span class="block text-lg font-bold text-slate-900">{amount_fmt} \u20ac</span><span class="block text-xs text-slate-500">{label}</span></a>'

updated_count = 0
errors = []

for amount in valid_amounts:
    neighbors = get_neighbors(amount)
    if not neighbors:
        continue

    for suffix, label in [("brut-en-net", "brut en net"), ("net-en-brut", "net en brut")]:
        file_path = os.path.join(BASE, f"{amount}-euros-{suffix}", "index.html")
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()

        if "Montants proches" not in html:
            continue

        # Build new neighbor links
        new_links = []
        for i, n in enumerate(neighbors):
            slug = f"{n}-euros-{suffix}"
            link = LINK_TEMPLATE.format(
                slug=slug, amount_fmt=format_amount(n), label=label
            )
            if i == 0:
                # First link gets indentation matching original
                new_links.append(f"                    {link}")
            else:
                new_links.append(link)

        new_links_html = "\n".join(new_links)

        # Replace content between the grid div and its closing tag
        pattern = (
            r"(Montants proches</h2>\s*"
            r'<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">\s*)'
            r"(.*?)"
            r"(\s*</div>)"
        )

        def replace_links(m):
            return m.group(1) + new_links_html + m.group(3)

        new_html = re.sub(pattern, replace_links, html, count=1, flags=re.DOTALL)

        if new_html != html:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_html)
            updated_count += 1

print(f"  Updated {updated_count} pages")


# ── Summary ────────────────────────────────────────────────────────────

print(f"\n{'='*50}")
print(f"DONE!")
print(f"  Redirect pages created: {redirect_count}")
print(f"  Sitemap URLs removed:   {removed_count}")
print(f"  Sitemap URLs remaining: {remaining}")
print(f"  Pages links updated:    {updated_count}")
print(f"{'='*50}")
