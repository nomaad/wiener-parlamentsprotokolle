
"""Beispiel zur Verarbeitung mehrerer Wiener Gemeinderatsprotokolle."""

from wiener_protokolle import parse_many

urls = [
    "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-23.txt",
    "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-22.txt",
    "https://www.wien.gv.at/mdb/gr/2026/gr-015-w-2026-06-16.txt",
]

df_gesamt = parse_many(urls)

print(df_gesamt.head())
print(df_gesamt.columns.tolist())
print(f"Anzahl Redebeiträge: {len(df_gesamt)}")
