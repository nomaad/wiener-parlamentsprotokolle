
import pandas as pd

#import pytest
from wiener_protokolle import parse_many, parse_protokoll

# Einzelnes Protokoll parsen
url = "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-23.txt"
df = parse_protokoll(url)

# Altes Protokoll parsen (2014)
url14 = "https://www.wien.gv.at/mdb/gr/2014/gr-058-w-2014-11-12.txt"
df2014 = parse_protokoll(url14)

def test_parse_protokoll_correct_columns():
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "gremium" in df.columns
    assert "sitzungsnummer" in df.columns
    assert "datum" in df.columns
    assert "funktion" in df.columns
    assert "amtsfunktion" in df.columns
    assert "name" in df.columns
    assert "titel" in df.columns
    assert "partei" in df.columns
    assert "rede" in df.columns

def test_parse_protokoll_amtsfunktion_items_correct():
    allowed = {"GR", "GRin", "StR", "StRin", "Bgm", "VBgm", "VBgm.in"}
    values = set(df["amtsfunktion"].dropna().unique())
    assert values <= allowed

def test_parse_protokoll_partei_items_correct():
    allowed = {
        "", "SPÖ", "ÖVP", "FPÖ", "GRÜNE", "NEOS", "PILZ", "KPÖ", "MFG"
    }
    values = set(df["partei"].dropna().unique())
    assert values <= allowed
    #assert all(value != "" for value in values)

def test_parse_protokoll_old_partei_items_correct():
    allowed = {
        "",
        "ÖVP-Klub der Bundeshauptstadt Wien", 
        "Grüner Klub im Rathaus",
        "Klubungebundener Mandatar",
        "Klub der Wiener Freiheitlichen",
        "Sozialdemokratische Fraktion des Wiener Landtages und Gemeinderates",
        'Sozialdemokratische Fraktion des Wiener Landtages'
    }
    values = set(df2014["partei"].dropna().unique())
    assert values <= allowed
    #assert all(value != "" for value in values)

def test_parse_many_with_empty_list():
    result = parse_many([])

    assert isinstance(result, pd.DataFrame)
    assert result.empty

# def test_parse_many_22_wahlperiode_export_csv():
    
#     urls_wahlperiode22 = [
#             "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-22.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-23.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-015-w-2026-06-16.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-014-w-2026-05-19.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-013-w-2026-04-27.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-012-w-2026-03-25.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-011-w-2026-02-18.txt",
#             "https://www.wien.gv.at/mdb/gr/2026/gr-010-w-2026-01-20.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-009-w-2025-12-18.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-008-w-2025-12-16.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-008-w-2025-12-17.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-007-w-2025-11-18.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-006-w-2025-10-22.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-005-w-2025-09-24.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-004-w-2025-09-22.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-003-w-2025-06-25.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-002-w-2025-06-23.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-002-w-2025-06-24.txt",
#             "https://www.wien.gv.at/mdb/gr/2025/gr-001-w-2025-06-10.txt"
#         ]
    
#     df_gesamt_wp22 = parse_many(urls_wahlperiode22)

#     # Formale Angelobung entfernen
#     df_gesamt_wp22 = df_gesamt_wp22.iloc[176:].reset_index(drop=True)

#     # Exportiere das Ergebnis als CSV-Datei
#     df_gesamt_wp22.to_csv("data/wiener_gemeinderat_wahlperiode22.csv", index=False, sep=";", encoding="utf-8-sig")