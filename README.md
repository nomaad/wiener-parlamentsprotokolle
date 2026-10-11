
# Wiener Parlamentsprotokolle

Python-Paket zum Einlesen und Strukturieren von Wortprotokollen des Wiener Parlaments.

**Funktionen:**

- Wortprotokolle anhand ihrer URL herunterladen
- Redebeiträge anhand von Rednerwechseln extrahieren
- Sitzungsmetadaten aus der URL auslesen
- Redner, Amtsfunktion, Titel, Partei und Rede strukturieren
- Mehrere Sitzungen zu einem pandas DataFrame zusammenführen

**Status:**

- Nur Gemeinderatsprotokolle ab 2014 werden unterstützt
- Spalte "Wahlperiode" fehlt
- Extraktion der Titel (Dr., Mag. etc.) funktioniert nur bei neueren Protokollen
- Beiträge von Vorsitzenden, Berichterstatter:innen und Schriftführer:innen werden automatisch entfernt, da sie oft nur formal bzw. inhaltslos sind
- Name von Parteien/Clubs werden nicht vereinheitlicht

## Installation

Voraussetzung: Python 3.10 oder neuer.

```bash
git clone https://github.com/nomaad/wiener-parlamentsprotokolle.git
cd wiener-parlamentsprotokolle

python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Verwendung

Achtung: Die API ist unvollständig implementiert. Die extrahierten Daten können fehlerhaft sein und sollten stichprobenartig überprüft werden.

```python
from wiener_protokolle import parse_protokoll, parse_many

url = (
    "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-23.txt"
)

df = parse_protokoll(url)

# Mehrere Protokolle laden
urls = urls = [
    "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-23.txt",
    "https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-22.txt",
    "https://www.wien.gv.at/mdb/gr/2026/gr-015-w-2026-06-16.txt",
]

df_gesamt = parse_many(urls)

print(df_gesamt.head())
print(df_gesamt.columns.tolist())
print(f"Anzahl Redebeiträge: {len(df_gesamt)}")
```

## Datenstruktur

| Spalte | Inhalt |
| --- | --- |
| `gremium` | Gremium-Kürzel, z. B. `GR` (Gemeinderat) |
| `sitzungsnummer` | Sitzungsnummer |
| `datum` | Sitzungsdatum |
| `funktion` | Funktion im Protokoll, z.B. `Schriftführer` |
| `amtsfunktion` | z. B. `GR` (Gemeinderat), `StR` (Stadtrat), `Bgm` (Bürgermeister) |
| `name` | Name der sprechenden Person |
| `titel` | Akademische Titel, z.B. `Dr.` oder `MA` |
| `partei` | Parteizugehörigkeit, z.B. `SPÖ` oder `ÖVP` |
| `rede` | Text des Redebeitrags |

## Datenquelle

Die Protokolle werden von der Stadt Wien veröffentlicht (*.txt-Dateien seit 2014): https://www.wien.gv.at/mdb/

Beispiel:
https://www.wien.gv.at/mdb/gr/2026/gr-016-w-2026-06-23.txt

Dieses Projekt ist unabhängig von der Stadt Wien. Bitte beachte die Nutzungsbedingungen und Hinweise der Originalquelle.

## Qualität und Nutzung

Die Extraktion basiert auf Formatmustern und kann Fehler enthalten. Insbesondere Rednerwechsel, Fortsetzungen, Titel und Parteizugehörigkeiten sollten stichprobenartig überprüft werden.

Ergänzte Parteizugehörigkeiten sollten für den jeweiligen Zeitraum belegt und die Quellen dokumentiert werden.

## Entwicklung



Tests ausführen:

```bash
pytest
```

Code prüfen und formatieren:

```bash
ruff check .
ruff format .
```

## Lizenz

Der Quellcode steht unter der MIT-Lizenz. Diese Lizenz erstreckt sich nicht automatisch auf die Quelldaten der Stadt Wien.
