# Sachsen-Anhalt (LHW / GLD) — Status: ZURÜCKGESTELLT (Lizenz)

Stand: 2026-07-17. Ein Provider `lhw_st` wurde **vollständig gebaut und live
verifiziert**, aber bewusst **nicht ins Repo aufgenommen** — allein wegen der
Lizenz (siehe unten). Technisch ist alles einsatzbereit; diese Notiz hält den
Stand fest, damit eine Reaktivierung ohne erneute Recherche möglich ist.

## Warum zurückgestellt

Das GLD Sachsen-Anhalt steht **nicht** unter einer offenen Lizenz (dl-de/CC),
sondern unter eigenen **Nutzungsbestimmungen GLD**:

- Nutzung/Vervielfältigung/**Veröffentlichung ausdrücklich erlaubt** — mit
  Pflicht-Quellenangabe „© LHW Sachsen-Anhalt",
- aber **unentgeltlich / nicht-kommerziell**,
- und **Veränderungshinweis** bei Bearbeitung/eigenen Berechnungen (der Provider
  rechnet „cm u. MP" → „m ü. NHN" um).

Das Repo-Code steht unter **MIT** (erlaubt kommerzielle Nutzung). Nicht-kommerzielle
Fremddaten ins MIT-Repo zu bündeln erzeugt eine gemischte Lizenzlage (die
Blanket-MIT-Aussage stimmt für die Datendatei nicht). Um das Repo einheitlich
offen-lizenziert zu halten, wurde SA zurückgestellt. (Anders als Niedersachsen ist
Veröffentlichung hier *erlaubt* — eine Aufnahme wäre mit eigenem Per-Datei-Lizenz-
Header zulässig; das ist eine bewusste Owner-Entscheidung, kein technischer Blocker.)

## Technischer Stand (live verifiziert 2026-07-17)

Das GLD-Portal `https://gld.lhw-sachsen-anhalt.de/` ist ein IDU **cardoMap3**-GIS
und nutzt **dieselben `IDU.cmApp.LFUBRB.Diagramme`-MultiExport-Controls wie
Brandenburgs APW** (`lfu_bb`) — dasselbe reverse-engineerte AjaxPro-Muster greift.
**KiWIS existiert nicht** (alle `/KiWIS/KiWIS?...`-Kandidaten → 404).

- **Stationen:** `SelectionControl.AxExecuteQuery`, Theme `10.263`
  („Messstellen Grundwasserstand", Layer `L197`), Spalte `NUMMER`. Maptip-HTML →
  MKZ, Name, Rechts-/Hochwert (**EPSG:25832**), Messpunkthöhe (MPH, mNHN),
  `id_messstelle=` (interne msid). Feld-Discovery via `IwanQueryEditor.
  AxGetSearchableFields`/`AxGetPreviewList` (1333 MKZ).
- **Werte:** `MultiExport.AxGetAvailableParameterChoice` → Parameter `10100005`
  „Wasserstand"; `AxGetZeitraum`; `AxExport(format=1)` → ZIP mit `…_messreihen.csv`
  („Wasserstand [cm u. MP]"). Umrechnung `NHN = MPH − cm/100` je Station.
- **Session:** Landing-Page-GET (Cookie) vor dem ersten Export nötig.
- **Live:** Umkreis Magdeburg (52.13/11.63) → 28 Stationen in 5 km, nächste
  „MD-Ratswaage" (38350101) → **48,38 m ü. NHN** (2026-03-22, 53 Wochenwerte).

## Reaktivierung

Falls LHW eine offene Lizenz nachzieht — oder die gemischte Lizenzlage bewusst
akzeptiert wird (Per-Datei-Lizenz-Header „© LHW Sachsen-Anhalt / nicht-kommerziell"
auf `lhw_st_stations.json` + README-NOTICE): der Provider lässt sich analog `lfu_bb`
bauen (`providers/lhw_st.py`, Offline-Bundle `lhw_st_stations.json` mit
lat/lon/msid/mph via `scripts/build_lhw_st_stations.py`, ~1290 Stationen). Domain
`lhw_st`, Label „Sachsen-Anhalt (LHW)", Attribution „© LHW Sachsen-Anhalt / Werte
aus cm u. MP in m ü. NHN umgerechnet".
