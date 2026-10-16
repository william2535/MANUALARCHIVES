# Adding and correcting records

1. Find the manufacturer's original download or an explicitly manufacturer-linked document host.
2. Open the exact document and check its title, model applicability, issue, language and market. A similar model name or a directory date is not sufficient.
3. Add or correct an entry in `data/catalogue.json`. Keep unknown fields null or `not-verified`. `revision_hint` records only a filename hint; it is not a verified revision.
4. Use a separate record for a distinct edition or language. Reuse one record with multiple `models` when the manufacturer explicitly associates the same document with them.
5. Run `python3 scripts/build_index.py`, then `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`.

Keep the four category keys stable: `fire`, `security`, `access-control`, `cctv`. Door entry and intercoms live under access control; intrusion and related security equipment live under security. Source PDFs and observations take precedence over inferred folder names. Model folders are navigation aids and do not certify compatibility.

Generated category, brand and model README files should be rebuilt from the JSON, not edited individually. Report broken links by identifying the record ID and source URL. Do not silently replace an older edition with a newer one or label a document “latest” without evidence.
