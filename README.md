# Grundwasser (Deutschland) für Home Assistant

[![hassfest](https://github.com/hnehnes/grundwasser-de/actions/workflows/hassfest.yml/badge.svg)](https://github.com/hnehnes/grundwasser-de/actions/workflows/hassfest.yml)
[![HACS](https://github.com/hnehnes/grundwasser-de/actions/workflows/hacs.yml/badge.svg)](https://github.com/hnehnes/grundwasser-de/actions/workflows/hacs.yml)

Home-Assistant-Integration für **Grundwasserstände in Deutschland** aus mehreren
Quellen hinter einer gemeinsamen **Provider-Architektur**. Deutschland-Grundwasser
ist föderal organisiert – ein bundesweites, kuratiertes Netz (NIWIS/BfG) plus je
Bundesland ein dichtes Landesnetz. Diese Integration bündelt die Quellen und bietet
im Config-Flow die **tatsächlich nächste** Messstelle quellenübergreifend an.

## Datenquellen (Provider)

| Provider | Quelle | Abdeckung | Lizenz | Besonderheit |
| -------- | ------ | --------- | ------ | ------------ |
| `niwis` | Niedrigwasserinformationssystem der BfG – [niwis-online.de](https://niwis-online.de) | bundesweit | – | zusätzlich **Niedrigwasserklasse** + Trend (1991–2020) |
| `lfu_bb` | LfU Brandenburg, APW – [apw.brandenburg.de](https://apw.brandenburg.de) | Brandenburg | dl-de/by-2.0 | ~1850 Pegel, Ganglinie, m ü. NHN |
| `bukea_hh` | BUKEA Hamburg – OGC API Features | Hamburg | CC0 | Ganglinie, m ü. NHN |
| `hlnug_he` | HLNUG Hessen – GruSchu (ArcGIS) | Hessen | CC-BY 4.0 | Ganglinie, m ü. NN |
| `wasserportal_be` | Wasserportal Berlin | Berlin | dl-de/by-2.0 | CSV-Ganglinie, m ü. NHN |
| `lfu_sh` | LfU Schleswig-Holstein – WFS + Open Data | Schleswig-Holstein | dl-de/by-2.0 | Ganglinie, m ü. NN |
| `lanuk_nw` | LANUK NRW – OpenHygrisC-Bulk | Nordrhein-Westfalen | dl-de/zero-2.0 | aktueller Wert (monatl. Snapshot), m ü. NHN |

Weitere Landesnetze lassen sich als zusätzliche Provider unter
`custom_components/grundwasser_de/providers/` ergänzen; das Interface ist in
[`providers/base.py`](custom_components/grundwasser_de/providers/base.py) dokumentiert,
generische Helfer für **ArcGIS** (`_arcgis.py`) und **WFS** (`_wfs.py`) liegen bereit.
Recherche-Stand aller 16 Länder: [`docs/research/laender-grundwasser-quellen.md`](docs/research/laender-grundwasser-quellen.md).

## Funktionsumfang

Pro ausgewählter Messstelle wird ein **Gerät** angelegt, mit diesen Sensoren:

| Sensor | Beispiel-State | Einheit | Quellen |
| ------ | -------------- | ------- | ------- |
| Grundwasserstand | `42.0` | m (ü. NHN) | alle |
| Niedrigwasserklasse | `sehr niedrig` | ENUM-Text | nur NIWIS |
| Trend | `gleichbleibend` | ENUM-Text | nur NIWIS |

Die Niedrigwasserklasse ist ein Text-Sensor (ENUM) mit den Zuständen
**kein Niedrigwasser · niedrig · sehr niedrig · extrem niedrig · keine Daten**.
Die Quelle steht als **Hersteller** am Gerät, die Stations-ID als **Seriennummer**.

## Installation

### HACS (empfohlen)

1. HACS öffnen → *Integrationen* → Menü → **Benutzerdefinierte Repositories**.
2. `https://github.com/hnehnes/grundwasser-de` als Kategorie *Integration* hinzufügen.
3. „Grundwasser (Deutschland)" installieren und Home Assistant neu starten.

### Manuell

Den Ordner `custom_components/grundwasser_de` nach
`<config>/custom_components/grundwasser_de` kopieren und Home Assistant neu starten.

## Einrichtung

1. *Einstellungen → Geräte & Dienste → Integration hinzufügen → **Grundwasser (Deutschland)***.
2. Suche wählen:
   - **Umkreis** um den Home-Assistant-Standort (Radius konfigurierbar) – sucht über
     **alle** Provider und sortiert nach Entfernung, oder
   - **Name/Stations-ID**.
3. Eine oder mehrere Messstellen aus der quellenübergreifenden Liste auswählen.

### Optionen

Über *Konfigurieren* am Eintrag:

- **Aktualisierungsintervall** (Standard 3 h, Minimum 1 h – Fair Use gegenüber den APIs).
- **Weitere Messstellen** per Umkreis- oder Namenssuche nachrüsten.

## Hinweise zur Datenlage

- Die LfU-Umkreissuche bietet **nur Messstellen mit tatsächlich abrufbarem
  Grundwasserstand** an: reine **Güte**-Pegel (nur Wasserqualität) und Stationen,
  die in der Auskunftsplattform keine Zeitreihe haben, sind vorab herausgefiltert.
  Die Filterliste wird offline erzeugt (`scripts/build_lfu_bb_stations.py`) und ist
  gebündelt – bei Bedarf regenerierbar.
- Sollte eine Station später doch keine Daten liefern, bleibt ihr Wert-Sensor
  *unbekannt* (kein Fehler, der Rest der Messstellen bleibt aktuell).

## Beispiel-Dashboard

Ein fertiges Beispiel (Sektionen je Station, Wert-Kachel, Niedrigwasserklasse/Trend
bei NIWIS, Verlaufs- und Statistik-Graph) liegt unter
[`examples/grundwasser_de-dashboard.yaml`](examples/grundwasser_de-dashboard.yaml).
Den Raw-Konfigurationseditor eines neuen Dashboards damit füllen und die `entity_id`s
an deine Messstellen anpassen.

## Datenquelle & Attribution

- **NIWIS**: Bundesanstalt für Gewässerkunde (BfG), Bund/Länder und DWD –
  [niwis-online.de](https://niwis-online.de).
- **LfU Brandenburg**: Landesamt für Umwelt, Auskunftsplattform Wasser –
  [apw.brandenburg.de](https://apw.brandenburg.de), Datenlizenz **dl-de/by-2-0**.

Bitte die jeweils geltenden Nutzungs-/Lizenzbedingungen der Betreiber beachten.
Diese Integration steht in keiner Verbindung zu BfG oder LfU und wird nicht von
ihnen unterstützt. Das reverse-engineerte APW-Protokoll ist in
[`docs/research/apw-brandenburg.md`](docs/research/apw-brandenburg.md) dokumentiert.

## Logo / brands

Icon-/Logo-Dateien liegen unter
[`brands/custom_integrations/grundwasser_de/`](brands/custom_integrations/grundwasser_de/).
Für die Anzeige in Home Assistant und HACS die Dateien per PR bei
[home-assistant/brands](https://github.com/home-assistant/brands) unter
`custom_integrations/grundwasser_de/` einreichen.
