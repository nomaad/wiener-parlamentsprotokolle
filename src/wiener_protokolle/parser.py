
"""Parser für Wortprotokolle der Wiener Gremien."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import PurePosixPath
from urllib.parse import urlparse

import pandas as pd
import requests


# Amtsfunktion und Titel aus der Spalte "redner" extrahieren
def parse_redner(redner)-> pd.Series:
    """Parst einen Redner-Eintrag und teilt ihn in seine Bestandteile auf (Amtsfunktion, Titel, Name).
    
        Parameters
        ----------
        redner:
            Der Redner-Eintrag, der analysiert werden soll.

        Returns
        -------
        pandas.Series
            Eine Serie mit den Bestandteilen des Redners: Amtsfunktion, Titel vor dem Namen, Name und Titel nach dem Namen.
    
        """
    redner = str(redner).strip()

    # Amtsfunktion am Anfang erkennen
    match = re.match(
        r"^(?P<funktion>"
        r"Amtsf\.\s+StR(?:in)?|"
        r"Amtsführende[rn]?\s+Stadträt(?:in)?|"
        r"VBgm\.in|VBgm\.|"
        r"Bgm\.in|Bgm\.?|"
        r"StRin|StR|GRin|GR"
        r")\s+(?P<rest>.*)$",
        redner
    )

    if match:
        funktion = match.group("funktion")
        rest = match.group("rest").strip()
    else:
        funktion = ""
        rest = redner

    # Titel nach dem Namen, z.B. ", MA" oder ", BA"
    nachname_titel = ""
    if "," in rest:
        rest, nachname_titel = rest.split(",", 1)
        nachname_titel = nachname_titel.strip()

    # Titel vor dem Namen, z.B. "Mag.", "Dr.", "Dipl.-Ing."
    titel_pattern = (
        r"^(?:(?:Dipl\.-Ing\.|"
        r"Mag\.|Dr\.|DI|Ing\.|"
        r"BSc|MSc|BA|MA|LL\.M\.)\s+)+"
    )

    titel_match = re.match(titel_pattern, rest)
    if titel_match:
        titel_vorname = titel_match.group(0).strip()
        name = rest[titel_match.end():].strip()
    else:
        titel_vorname = ""
        name = rest.strip()

    return pd.Series({
        "amtsfunktion": funktion,
        "titel_vorname": titel_vorname,
        "name": name,
        "titel_nachname": nachname_titel
    })

def parse_protokoll(url: str) -> pd.DataFrame:
    """Lädt und parst ein einzelnes Wortprotokoll.

    Parameters
    ----------
    url:
        URL zur Textdatei des Protokolls. Siehe https://www.wien.gv.at/mdb/gr/
        Der Link muss auf eine Textdatei verweisen, die mit dem Parser kompatibel ist (.txt-Datei, verfügbar ab 2014).

    Returns
    -------
    pandas.DataFrame
        Eine Zeile pro Redebeitrag, ergänzt um Sitzungsmetadaten.

    Notes
    -----
    Die Implementierung wird im nächsten Schritt aus dem bisherigen
    Notebook-Code übernommen.
    """
    #url = "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-22.txt"

    response = requests.get(url)
    response.raise_for_status()
    text = response.content.decode("ISO-8859-1")


    header_pattern = re.compile(
        r"^[ \t]+"
        r"(?:(?P<funktion>"
        r"Vorsitzende[rn]?|"
        r"Berichterstatter(?:in)?|"
        r"Schriftführer(?:in)?|"
        r"Schlusswort Berichterstatter(?:in)?|"
        r"Amtsf\.|"
        r"Amtsführende[rn]?\s+Stadträt(?:in)?"
        r")\s+)?"
        r"(?P<redner>"
        r"(?:(?:VBgm\.?(?:in)?|"
        r"Bgm\.?(?:in)?|"
        r"StR(?:in)?|GR(?:in)?)\s+)"
        r"[^\r\n:]*?"
        r")"
        r"(?:\s+\((?P<partei>[^()\r\n]+)\))?"
        r":[ \t]*",
        re.MULTILINE
    )

    # Alle Rednerwechsel finden
    matches = list(header_pattern.finditer(text))

    if not matches:
        raise ValueError(
            "Keine Redebeiträge gefunden. Bitte das Regex-Muster prüfen."
        )

    beitraege = []

    for i, match in enumerate(matches):
        # Rede beginnt unmittelbar nach dem Doppelpunkt
        start = match.end()

        # Rede endet beim nächsten Rednerwechsel
        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(text)
        )

        rede = text[start:end].strip()

        beitraege.append({
            "funktion": (match.group("funktion") or "").strip(),
            "redner": match.group("redner").strip(),
            "partei": (match.group("partei") or "").strip(),
            "rede": rede
        })

    # In einen DataFrame umwandeln
    df = pd.DataFrame(beitraege)
    

    # Beiträge von Vorsitzenden entfernen, da diese nicht relevant sind
    df = df[~df["funktion"].isin(["Vorsitzende", "Vorsitzender"])].reset_index(drop=True)

    # Beiträge von Rednern, die "fortsetzend" in der Partei haben, mit dem vorherigen Beitrag zusammenführen
    for i in df.index[df["partei"].str.contains("fortsetzend", case=False, na=False)]:
        prev_idx = df.index[df.index < i][-1]
        df.at[prev_idx, "rede"] += "\n\n" + df.at[i, "rede"]

    df = df[~df["partei"].str.contains("fortsetzend", case=False, na=False)].reset_index(drop=True)

    # Manuell erstellte Zuordnung für die Stadtregierung ab Juni 2025
    stadtraete_parteien = {
        "Jürgen Czernohorszky": "SPÖ",
        "Bettina Emmerling": "NEOS",
        "Kathrin Gaál": "SPÖ",
        "Elke Hanel-Torsch": "SPÖ",
        "Peter Hacker": "SPÖ",
        "Veronica Kaup-Hasler": "SPÖ",
        "Barbara Novak": "SPÖ",
        "Ulli Sima": "SPÖ",
        "Stefan Berger": "FPÖ",
        "Dominik Nepp": "FPÖ",
        "Ulrike Nittmann": "FPÖ",
        "Peter Kraus": "GRÜNE",
        "Judith Pühringer": "GRÜNE",
        "Katarzyna Greco": "ÖVP",
        "Michael Ludwig": "SPÖ",
    }

    # Nur fehlende Parteizugehörigkeiten ergänzen
    for idx, row in df.iterrows():
        if pd.isna(row["partei"]) or not row["partei"].strip():
            redner = row["redner"]

            for name, partei in stadtraete_parteien.items():
                if name.casefold() in redner.casefold():
                    df.at[idx, "partei"] = partei
                    break

    df[["amtsfunktion", "titel_vorname", "name", "titel_nachname"]] = (
        df["redner"].apply(parse_redner)
    )

    # Titel vor und nach dem Namen in einer Spalte zusammenführen
    df["titel"] = (
        df["titel_vorname"].fillna("").str.strip()
        + df["titel_nachname"].fillna("").str.strip().radd(", ").where(
            df["titel_nachname"].fillna("").str.strip().ne(""), ""
        )
    ).str.strip().str.strip(",")

    # Spalten am Ort von "redner" einsetzen
    cols = list(df.columns)
    pos = cols.index("redner")

    neue_spalten = ["amtsfunktion", "name", "titel"]
    cols = [c for c in cols if c not in [
        "redner", "amtsfunktion", "name", "titel",
        "titel_vorname", "titel_nachname"
    ]]
    cols[pos:pos] = neue_spalten

    df = df[cols]

    # Dateiname aus der URL lesen
    filename = PurePosixPath(urlparse(url).path).name

    match = re.match(
        r"(?P<gremium>[a-z]+)-(?P<sitzungsnummer>\d+)-[a-z]+-"
        r"(?P<datum>\d{4}-\d{2}-\d{2})\.txt$",
        filename,
        re.IGNORECASE
    )

    if not match:
        raise ValueError(f"URL-Dateiname hat ein unerwartetes Format: {filename}")

    # Sitzungsdaten an alle Zeilen anhängen
    df["gremium"] = match.group("gremium").upper()
    df["sitzungsnummer"] = int(match.group("sitzungsnummer"))
    df["datum"] = pd.to_datetime(match.group("datum"))

    session_cols = ["gremium", "sitzungsnummer", "datum"]

    df = df[session_cols + [col for col in df.columns if col not in session_cols]]

    return df


def parse_many(urls: Iterable[str]) -> pd.DataFrame:
    """Parst mehrere Protokolle und fügt sie zusammen.

    Parameters
    ----------
    urls:
        Iterable mit URLs zu Protokolldateien.

    Returns
    -------
    pandas.DataFrame
        Zusammengeführte Redebeiträge.
    """
    frames = [parse_protokoll(url) for url in urls]

    if not frames:
        return pd.DataFrame()

    df_gesamt = pd.concat(frames, ignore_index=True)

    # Nach Datum und Sitzungsnummer sortieren
    df_gesamt = df_gesamt.sort_values(
        ["datum", "sitzungsnummer"]
    ).reset_index(drop=True)

    # Beiträge entfernen, die nur aus "Ich ersuche um Zustimmung" bestehen, da diese keine inhaltliche Aussage enthalten
    mask = (
        df_gesamt["partei"].fillna("").str.strip().eq("")
        & df_gesamt["rede"].str.strip().str.fullmatch(
            r".*(?:Ich\s+(?:ersuche|bitte)\s+um|Bitte\s+um)\s+Zustimmung[.!]?",
            case=False,
            flags=re.DOTALL
        )
    )
    df_gesamt = df_gesamt.loc[~mask].reset_index(drop=True)

    # Alle Berichterstatter:innen entfernen
    df_gesamt = df_gesamt[
        ~df_gesamt["funktion"].fillna("").str.strip().str.casefold().isin(
            ["berichterstatter", "berichterstatterin", "schriftführer", "schriftführerin"]
        )
    ].reset_index(drop=True)

    return df_gesamt
