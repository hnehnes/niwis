# Länder-Grundwasserquellen — Recherche für `grundwasser_de`-Provider

Stand: 2026-07-17. Recherche der öffentlich zugänglichen **Grundwasserstands-Datenquellen**
(Messstellen + Zeitreihen) der 15 Bundesländer **außer Brandenburg** (bereits als `lfu_bb`
umgesetzt) und Bund (`niwis`).

**Ziel-Interface je Provider** (siehe `custom_components/grundwasser_de/providers/`):
- `async_search_radius(lat, lon, radius_km)` → Messstellen **mit Koordinaten** (WGS84 oder
  bekanntes CRS, meist EPSG:25832/25833).
- `async_fetch(station)` → aktueller **Grundwasserstand** + möglichst Historie; Einheit
  m ü. NHN oder cm/m unter GOK.

Bevorzugt: maschineller Zugang **ohne Login** (REST/JSON, WFS, ArcGIS REST, OGC SensorThings/
OGC API Features, oder reverse-engineerbare GIS-XHR wie bei `lfu_bb`/cardoMap).

Legende: **[V]** = Endpoint per WebFetch live abgerufen und Inhalt bestätigt · **[A]** =
aus Doku/Metadaten/Portal-Quellcode abgeleitet, nicht am Live-Endpoint bestätigt.

---

## Übersichtstabelle

| Land | Behörde | Zugangstyp | GW-Zeitreihe? | Koord./CRS | Lizenz | Aufwand | Status |
|------|---------|-----------|---------------|------------|--------|---------|--------|
| **Hamburg** | BUKEA | OGC API Features (JSON) + WFS | **Ja** (Tageswerte, m NHN & GOK) | WGS84 / 25832 | CC-Zero | **leicht** | **[V]** |
| **Hessen** | HLNUG | ArcGIS REST (+ WFS) | **Ja** (volle Ganglinie, m NN & GOK) | EPSG:25832 | CC-BY 4.0 | **leicht** | **[V]** |
| **Berlin** | SenMVKU | REST-artige PHP-GET (HTML+CSV) | **Ja** (CSV/Station, m NHN) | EPSG:25833 | dl-de/by-2.0 | **leicht** | **[V]** |
| **Niedersachsen** | NLWKN | REST/JSON (Azure APIM, Key im JS) | Aktuell **ja**; Historie unklar | WGS84 | ungeklärt | leicht–mittel | **[V]** (Wert) |
| **Schleswig-Holstein** | LfU SH | WFS (GML) + CSV/Station | **Ja** (automatisierbar) | EPSG:25832 | dl-de/by-2.0 | leicht–mittel | **[V]** (Stationen) |
| **Rheinland-Pfalz** | LfU RLP | WFS GeoServer (GeoJSON!) | Stationen ja; Zeitreihe nur AKSAM-XHR | EPSG:25832 | dl-de/by-2.0 [A] | mittel | **[V]** (Stationen) |
| **Sachsen** | LfULG/BfUL | ArcGIS REST + WFS | Stationen ja; Werte nur iDA/Cadenza-XHR | EPSG:25833 | dl-de/by-2.0 | mittel–schwer | **[V]** (Stationen) |
| **NRW** | LANUK | Bulk-CSV/ZIP + JSON-Index | Ja, aber Bulk-Snapshot, kein Live | EPSG:25832 | dl-de/zero-2.0 | mittel | **[V]** |
| **Bayern** | LfU/GKD | GIS-Portal-XHR + Shapefile | Ja, aber Download-Token-Reverse-Eng. | 25832/4258 | CC-BY(-SA) 4.0 | mittel–schwer | **[V]** (Portal) |
| **Sachsen-Anhalt** | LHW/GLD | KISTERS WISKI (KiWIS?) + Shape | Download/Portal; KiWIS unverifiziert | 25832 [A] | ungeklärt | mittel–schwer | **[A]** |
| **Baden-Württemberg** | LUBW | Disy Cadenza (UDO), nur UI/CSV | Nur UI-Export; Datenschutz-Restriktion | EPSG:25832 | UIS/eingeschränkt | **schwer** | **[V]** (neg.) |
| **Thüringen** | TLUBN | Disy Cadenza (antares) | Nur Cadenza-XHR (session) | 25832 [A] | „offene Daten" [A] | **schwer** | **[V]** (neg.) |
| **Meckl.-Vorp.** | LUNG M-V | WFS (nur Güte-Messst.) + cardoMap | **Nein** (kein Stand-Endpoint) | 5650/25833/4326 | CC-BY-SA | **schwer** | **[V]** (neg.) |
| **Saarland** | LUA | WFS (nur Standorte) | **Nein** (Werte nur per Antrag) | EPSG:25832 | Werte other-closed | **schwer** | **[V]** (neg.) |
| **Bremen** | SUKW / GDfB | WMS + Shapefile (nur Standorte) | Werte nur in Web-App (XHR) | EPSG:25832 [A] | Standorte CC-BY | **schwer** | **[V]** (neg.) |

---

## Baden-Württemberg — SCHWER (zurückstellen)

1. **Behörde:** LUBW (Landesanstalt für Umwelt BW); operative GW-Daten bei den Regierungspräsidien.
2. **Portal:** UDO – Umwelt-Daten und -Karten Online `https://udo.lubw.baden-wuerttemberg.de/public/`;
   Cadenza-Arbeitsmappe `https://umweltdaten.lubw.baden-wuerttemberg.de/w/grundwasser`.
3. **Zugang:** GIS-Portal **Disy Cadenza** [V] (Bundles unter `/public/bundles/*.js`), session-/
   POST-basierte XHR, keine dokumentierte REST-Ressource. `/public/api/` und `/rest` → **404** [V].
   ArcGIS-Server `rips-gdi.lubw.baden-wuerttemberg.de/arcgis/rest/services/wfs` listet nur
   Wasserschutzgebiet/Wasserkraft/OW-Körper — **kein Grundwasser-Layer** [V].
4. **Zeitreihe:** nur über UDO-UI (Diagramm/Tabelle, CSV/Excel-Export) [A]. Kein direkter Endpoint.
5. **Koordinaten:** CRS EPSG:25832 [V, Metadaten], aber Umkreissuche durch Zugriffsbeschränkung erschwert.
6. **Restriktion:** Datensatz „Grundwassermeßstelle des gewässerkundlichen Dienstes" ist per
   **INSPIRE Art. 13(1)(f)** (personenbezogene Daten) eingeschränkt [V] — Stationsdaten geschützt.
7. **Lizenz:** UIS-Nutzungsvertrag der LUBW; GW-Stationsdaten eingeschränkt, keine offene CC/DL-DE-Freigabe.
8. **Aufwand: schwer.** Kein WFS/REST, Cadenza ohne stabile API, Datenschutz-Restriktion auf
   Stationsebene. Realistisch nur fragiles Scraping. **Empfehlung: zurückstellen** oder maschinellen
   Zugang direkt bei LUBW anfragen.

---

## Bayern — MITTEL–SCHWER

1. **Behörde:** Bayerisches Landesamt für Umwelt (LfU); Messstellenbetrieb durch die Wasserwirtschaftsämter.
2. **Portal:** GKD Bayern `https://www.gkd.bayern.de/de/grundwasser/oberesstockwerk`
   (+ `.../tieferestockwerke`), ~620 Landesmessnetz-GW-Messstellen [V].
3. **Zugang:** GIS-/CMS-Portal mit XHR + Download-Center; **kein offenes REST/JSON**.
   - Stationsseiten mit festem URL-Muster [V]:
     `…/de/grundwasser/oberesstockwerk/{region}/{name}-{id}/messwerte` (aktueller Wert + Tabelle, HTML)
     und `…/{name}-{id}/download`.
   - CSV-Download via **AJAX-POST** an `https://www.gkd.bayern.de/de/downloadcenter/enqueue_download`
     (Felder `zr`=monat/jahr/gesamt, `beginn`, `ende`, `wertart`=`tmw` Tagesmittel, `f`=Messstellen-Token).
     Antwort JSON `{result:"success", deeplink:<URL>}` → Datei. Endpoint bestätigt (HTTP 200 JSON) [V],
     aber **`f`-Token-Format nicht geknackt** — braucht einmaliges Mitschneiden des Browser-XHR.
4. **Zeitreihe:** ja, nur über enqueue-Mechanismus [V-Mechanismus / A-Details]. Nur Tagesmittel online;
   Encoding ISO-8859-1.
5. **Koordinaten:** separat als **Shapefile** (LfU-Downloaddienst „Landesmessnetze Grundwasser und
   Quellen"), Atom-Feed `https://www.lfu.bayern.de/gdi/dls/landesmessnetze.xml`, CRS EPSG:25832 / 4258 [V].
   Koordinaten stehen zusätzlich in jedem CSV-Kopf.
6. **Auth/CORS:** kein Login; Session-Cookies + strenge CSP; Browser-UA empfehlenswert. Individuelle
   Zeiträume brauchen E-Mail, vorgegebene (Monat/Jahr/Gesamt) laden sofort [V].
7. **Lizenz:** CC BY 4.0 (Messwerte) bzw. CC BY-SA 4.0 (Messstellen-Geodatendienst) [V].
8. **Aufwand: mittel–schwer.** Koordinaten/Stationsliste leicht (Shapefile). Zeitreihen-Automatisierung
   erfordert Nachbau des `enqueue_download`-POST inkl. `f`-Token; alternativ HTML-Scraping der
   `…/messwerte`-Seite für den aktuellen Wert.

---

## Berlin — LEICHT (Quick Win)

1. **Behörde:** Senatsverwaltung für Mobilität, Verkehr, Klimaschutz und Umwelt (SenMVKU) [V].
2. **Portal:** `https://wasserportal.berlin.de/` (Thema Grundwasserstand = `gws`).
3. **Zugang:** REST-artige PHP-GET-Endpoints, ohne Login.
   - **Messstellenliste** (Umkreissuche-Quelle) [V]:
     `https://wasserportal.berlin.de/messwerte.php?anzeige=tabelle&thema=gws`
     → HTML-Tabelle (`id="pegeltab"`), **893 GW-Messstellen**, Spalten u.a. Nummer, Bezirk,
     Grundwasserleiter, „Grundwasserstand (m ü. NHN)", „Flurabstand (m u. GOK)", Datum, letzter Wert.
     Encoding ISO-8859-15.
   - **Stammdaten inkl. Koordinaten** [V]:
     `https://wasserportal.berlin.de/station.php?anzeige=i&thema=gws&station=<ID>`
     → „Rechtswert/Hochwert (UTM 33 N)" = EPSG:25833.
4. **Zeitreihe: ja** [V] — CSV-Download je Station:
   `https://wasserportal.berlin.de/station.php?anzeige=d&station=<ID>&thema=gws&exportthema=gw&sreihe=ew&smode=c&sdatum=DD.MM.YYYY&senddatum=DD.MM.YYYY`
   (verifiziert mit `station=15156`: Semikolon-CSV `Datum;GW-Stand (m ü. NHN)`, Tageswerte,
   Dezimal-Komma). `sreihe`= `w`/`ew` (Einzelwerte), `m` (Tages-), `j` (Monatswerte); `smode=c` (CSV).
5. **Koordinaten:** UTM 33N = EPSG:25833 [V] (Stammdaten- und CSV-Kopf).
6. **Auth/CORS:** kein Login/Token, Standard-UA genügt, keine erkennbaren Limits [V].
7. **Lizenz:** dl-de/by-2.0, Namensnennung „Wasserportal Berlin / <Messstellennummer>" [V].
8. **Aufwand: leicht.** Feste GET-URLs für Liste + Koordinaten + CSV-Zeitreihe. Einziger Aufwand:
   HTML-Tabellenparsing + Latin-1/Komma-Handling. Referenz: R-Paket `KWB-R/wasserportal` (GitHub).

---

## Bremen — SCHWER (zurückstellen)

1. **Behörde:** Senatorin für Umwelt, Klima und Wissenschaft (Werte); Landesamt GeoInformation Bremen
   (Geodienste); Geologischer Dienst für Bremen (GDfB, am MARUM). Netz >170 Stationen, 22 tagesaktuell online.
2. **Portal:** Info `umwelt.bremen.de/.../grundwasserstaende-2384530`; Web-App `www.umwelt.bremen.de/grundwasser`
   (22 Stationen, Ganglinie); Hydrogeologie-Karte `https://gdfbmapserver.marum.de/mapbender3/application/Hydrogeologie`.
3. **Zugang:** WMS + INSPIRE-Download (nur **Standorte**) [V]:
   WMS-Caps `http://geodienste.bremen.de/wms_grundwassermessstellen?REQUEST=GetCapabilities&SERVICE=WMS&VERSION=1.3.0`;
   Shapefile `https://gdi2.geo.bremen.de/inspire/download/Grundwassermessstellen/data/Grundwassermessstellen_HB_BHV.zip`.
   Kein WFS in den Metadaten. Werte nur in der 22-Stationen-Web-App (clientseitige XHR, nicht dokumentiert) [A].
   `https://portal.hydro-bremen.de/` (Gewässerkundlicher Landesdienst) ist **Login-geschützt** [V].
4. **Zeitreihe:** unklar/eher nein [V]; umwelt.info: Download „nicht vorhanden", maschinenlesbar „Nein".
5. **Koordinaten:** Standorte via WMS/Shapefile (i.d.R. EPSG:25832) [V].
6. **Auth/CORS:** WMS/Download offen; App-XHR-Endpoints unbekannt.
7. **Lizenz:** Standorte CC-BY; Werte-Lizenz unklar.
8. **Aufwand: schwer.** Standorte einfach, aber GW-Stand/Ganglinie nur über nicht-dokumentierte Web-App —
   müsste per DevTools/Headless-Browser reverse-engineert werden.

---

## Hamburg — LEICHT (Top Quick Win)

1. **Behörde:** BUKEA (Behörde für Umwelt, Klima, Energie und Agrarwirtschaft) [V].
2. **Portal/Metadaten:** `https://metaver.de/trefferanzeige?docuuid=05375E04-1DC2-4ADA-A08E-B92FC54542BD`.
3. **Zugang (alle ohne Login):**
   - **OGC API Features (JSON, empfohlen)** [V]:
     `https://api.hamburg.de/datasets/v1/grundwassermessstellen/collections/grundwassermessstellen/items?f=json&limit=2`
     → GeoJSON-Features mit **mehreren datierten Datensätzen je Messstelle** (echte Zeitreihe).
     `numberMatched` = 181.527 (Station-Tage). Standard-Filter `bbox=` (Umkreissuche) und
     Property-Filter (`messstellennummer`) + `datetime=`.
   - **WFS** [V]: `https://geodienste.hamburg.de/wfs_grundwassermessstellen?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`,
     Typename `de.hh.up:grundwassermessstellen`.
4. **Zeitreihe: ja** [V]. Felder: `messstellennummer`, `messstellenbezeichnung`, `gok`,
   **`wasserstand_mnhn`** (m ü. NHN), **`wasserstand_mugok`** (m unter GOK), `datum_as_date`,
   `anzahl_messwerte_pro_tag`, `klassifikation_gwstand`, `prz_referenzmonat`, `prz_hex`.
   Tagesmittel seit 03/2012. Verifiziert Station 2200: 2016-07-28/29 `wasserstand_mnhn` 14.98/14.99.
   Aktueller Wert = jüngstes `datum_as_date` je `messstellennummer`.
5. **Koordinaten:** WGS84 in der OGC-API (GeoJSON), z.B. Station 2200 `[9.9261, 53.5891]`; WFS in EPSG:25832 [V].
6. **Auth/CORS:** kein Login; Urban Data Platform auf Maschinenzugriff ausgelegt, CORS offen, Fair-Use [A].
7. **Lizenz:** **CC-Zero** (Namensnennung BUKEA erbeten) [V/A] — sehr permissiv.
8. **Aufwand: leicht.** Ein JSON-Dienst deckt Umkreissuche (bbox), Stationsliste, aktuellen Stand und
   Ganglinie ab; Einheiten m ü. NHN und m unter GOK direkt vorhanden.
   Hinweis: `iot.hamburg.de` (SensorThings v1.1) enthält **kein** Grundwasser [V] — nicht dieser Weg.

---

## Hessen — LEICHT (Top Quick Win)

1. **Behörde:** HLNUG (Hessisches Landesamt für Naturschutz, Umwelt und Geologie).
2. **Portal:** GruSchu / Wasserviewer `https://gruschu.hessen.de/` (SPA); Landesgrundwasserdienst.
3. **Zugang:** WFS **und** ArcGIS REST, beide öffentlich, verifiziert.
   - WFS 2.0.0 [V]: `https://www.geoportal.hessen.de/registry/wfs/269?service=WFS&request=GetCapabilities`
     → FeatureType `inspire_umweltueberwachung:Grundwassermessstellen`, Ausgabe u.a. GeoJSON.
   - **ArcGIS REST MapServer (empfohlen)** [V], Basis `https://geodienste-umwelt.hessen.de/arcgis/rest/services/`:
     - **Messstellen + Koordinaten:** `.../gruschu/gruschu_mst_ga/MapServer/0/query`
       (Felder `ID, MESSTELLENNAME, KURZNAME, MESSSTELLENART`, Punkt, EPSG:25832).
       Umkreissuche: `.../0/query?geometry=<x,y>&geometryType=esriGeometryPoint&distance=5000&units=esriSRUnit_Meter&inSR=25832&outFields=*&f=json`.
     - **Zeitreihe:** Service `wasserviewer/Auswertung/MapServer`,
       **Layer 22 `V_GWM_WASSERSTAND_NN`** (m ü. NN), **Layer 20 `V_GWM_WASSERSTAND_GOK`** (unter GOK),
       Felder `GWM_ID, MESSDATUM (Epoch ms), MESSWERT (Double)`.
       Verifiziert [V]: `.../wasserviewer/Auswertung/MapServer/22/query?where=GWM_ID%3D13466&outFields=*&returnGeometry=false&f=json`
       → 2625 Messwerte, z.B. MESSDATUM 264643200000 / MESSWERT 85.98.
       **Join:** `gruschu_mst_ga/…/0.ID` == `Auswertung/…/22.GWM_ID` [V].
4. **Zeitreihe: ja** [V] — volle Ganglinie (m NN und unter GOK).
5. **Koordinaten:** EPSG:25832 (Punktgeometrie ArcGIS/WFS) [V].
6. **Auth/CORS:** kein Login/Token; ArcGIS-Paging (`exceededTransferLimit` → `resultOffset`/`orderByFields`);
   curl ohne Browser-UA funktioniert [V].
7. **Lizenz:** CC BY 4.0 (offene Geodaten Hessen) [A, mehrfach bestätigt].
8. **Aufwand: leicht.** Saubere unauthentifizierte ArcGIS-REST-API mit Stationsliste, Koordinaten,
   Umkreisabfrage und echten Ganglinien. Ideal.

---

## Mecklenburg-Vorpommern — SCHWER (zurückstellen)

1. **Behörde:** LUNG M-V (Landesamt für Umwelt, Naturschutz und Geologie), Güstrow [V].
2. **Portal:** Umweltkarten MV `https://www.umweltkarten.mv-regierung.de/` (cardoMap/Grintec);
   `https://www.lung.mv-regierung.de/fachinformationen/wasser/grundwasser/`; Metadaten via `metaver.de`.
3. **Zugang:** WFS vorhanden, aber **kein GW-Stand-Layer**.
   - WFS Messnetze [V]: `https://www.umweltkarten.mv-regierung.de/script/mv_a3_messnetze_wfs.php?SERVICE=WFS&REQUEST=GetCapabilities`
     → FeatureTypes u.a. `t3_fisg_mn_chm_gw` (**Grundwasser-GÜTE**-Messstellen). **Kein Stand-/Mengen-Layer,
     keine Zeitreihen.**
   - WFS Hydrogeologie [V]: nur thematische Flächen/Isolinien (Flurabstand, GW-Höhengleichen), keine Punkte.
   - Landesmessnetz Grundwasserstand (2015: 610 Stellen) nur im cardoMap-Portal, nicht als Datendienst.
4. **Zeitreihe: nein** [V] — umwelt.info: MV *nicht maschinenlesbar*, Download *nicht vorhanden*.
5. **Koordinaten:** nur Güte-Messstellen (WFS), Default EPSG:5650, auch 25832/25833/4326 [V]. Stand-Messstellen
   nur im Portal.
6. **Auth/CORS:** WFS offen [A].
7. **Lizenz:** CC-BY-SA, © LUNG M-V [V].
8. **Aufwand: schwer.** Für GW-Stand + Zeitreihe kein offener Endpoint; nur cardoMap-Reverse-Engineering
   (unsicher, ob Ganglinien überhaupt als Daten ausgeliefert werden) oder Datenanfrage. **Zurückstellen.**

---

## Niedersachsen — LEICHT–MITTEL

1. **Behörde:** NLWKN (Nds. Landesbetrieb für Wasserwirtschaft, Küsten- und Naturschutz).
2. **Portal:** „Grundwasserstand Online" `https://www.grundwasserstandonline.nlwkn.niedersachsen.de/`
   (161 fernübertragene GW-Messstellen).
3. **Zugang:** REST/JSON-API [V]. Backend Azure API Management, Basis
   `https://bis.azure-api.net/PegelonlineNeu/REST/` mit im Client-JS eingebettetem Key
   `subscription-key=19094e54510d4e89b140ff2d3abf715f` (öffentlich, kein Login; Key theoretisch rotierbar).
4. **Zeitreihe:** teilweise verifiziert.
   - **Aktueller Wert: ja** [V] — `.../stammdaten/stationen/{STA_ID}?subscription-key=…`
     liefert `GWAktuellerMesswert` (m unter GOK), **`GWAktuellerMesswertNNM`** (m ü. NHN),
     `AktuellGrundwasserstandsklasse` (z.B. „sehr niedrig"), plus letzten Wert je Datenspur.
     Beispiel Station 14767010 „Barge I".
   - **Historie: unklar** — Endpoint `.../station/{STA_ID}/datenspuren/parameter/{PAT_ID}/tage/{n}/forecast/true`
     (`PAT_ID`=536 „Wasserstand mNHN") bekannt, in Tests kamen `Pegelstaende`-Arrays aber **leer** zurück.
     Schema bekannt, Rückgabe leer — ggf. anderer Parameter/Aggregation nötig.
5. **Koordinaten:** ja [V], `Latitude`/`Longitude` bzw. `WGS84Rechtswert`/`WGS84Hochwert` in WGS84.
   Achtung: im Testdatensatz war `Latitude` mit dem Längengrad belegt — beim Parsen prüfen.
6. **Auth/CORS:** kein User-Login, nur eingebetteter `subscription-key`; curl ohne Browser-UA [V].
   Azure-APIM-Rate-Limits möglich (nicht getestet).
7. **Lizenz:** nicht im Response bestätigt [A] (vermutlich DL-DE/NLWKN-Nutzungsbedingungen — vor
   Produktivnutzung klären).
8. **Aufwand: leicht–mittel.** Saubere JSON-API mit Koordinaten + aktuellem Stand (m NHN & GOK).
   Einschränkungen: (a) `stammdaten/stationen/All` liefert die OW-Pegelliste, **nicht** die GW-Stationen —
   die 161 GW-`STA_ID` müssen aus der server-gerenderten Tabelle `/Messwerte` extrahiert werden [V];
   (b) volle Ganglinie noch offen; (c) Abhängigkeit vom eingebetteten Key.

---

## Nordrhein-Westfalen — MITTEL (Bulk, kein Live)

1. **Behörde:** LANUK NRW (Landesamt für Natur, Umwelt und Klima, ehem. LANUV) [V].
2. **Portal:** ELWAS-WEB `https://www.elwasweb.nrw.de/` (interaktiv) und OpenGeodata
   `https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/grundwasser/hygrisc/` (Download).
   >2.300 landeseigene GW-Standmessstellen [V].
3. **Zugang:** Bulk-Download mit maschinenlesbarem JSON-Index (empfohlen) [V].
   - Datei-Index: `…/hygrisc/index.json` (alle Dateien mit Name/Größe/Timestamp).
   - Messstellen (Koordinaten): `…/hygrisc/OpenHygrisC_gw-messstelle_EPSG25832_CSV.zip` (~29 MB).
   - Zeitreihen: `…/hygrisc/OpenHygrisC_gw-wasserstand_2020-2029_EPSG25832_CSV.zip` (+ Dekaden 1900–2019, je ~190–350 MB).
   - ELWAS-WEB (JSF/con-terra) = live/XHR theoretisch, aber sitzungsbasiert und schwer [V, als schwer eingestuft].
   - Negativ geprüft: `wfs.nrw.de/umwelt/linfos` (nur Naturschutz, kein GW) [V].
4. **Zeitreihe:** ja, aber Bulk-Snapshot (jährlich, Timestamp 2025-01-01), **kein Echtzeit-Wert** [V].
5. **Koordinaten:** EPSG:25832 (Messstellen-CSV) [V].
6. **Auth/CORS:** kein Login, direkte HTTPS-Downloads, Standard-UA [V].
7. **Lizenz:** dl-de/zero-2.0 (uneingeschränkt) [V].
8. **Aufwand: mittel.** Saubere stabile URLs + JSON-Index → Messstellen leicht. Zeitreihen nur als große
   Dekaden-ZIPs (Vorverarbeitung nötig), kein Live-Wert. Für HA: Messstellen-CSV für Umkreissuche,
   Wasserstands-ZIP periodisch ziehen und je Messstellen-ID letzten Wert extrahieren.

---

## Rheinland-Pfalz — MITTEL (Stationen leicht, Zeitreihe schwer)

1. **Behörde:** LfU RLP / Wasserwirtschaftsverwaltung RLP [V].
2. **Portal:** `https://wasserportal.rlp-umwelt.de` (+ `geoportal-wasser.rlp-umwelt.de`); GeoServer
   `geodienste-wasser.rlp-umwelt.de`.
3. **Zugang:** WFS GeoServer **mit GeoJSON** (großer Vorteil) [V]:
   `https://geodienste-wasser.rlp-umwelt.de/geoserver/messstellen/grundwasser/wfs?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`
   → FeatureType `messstellen:grundwasser` (706 Brunnen/Pegel + 86 Quellen).
   Beispiel [V]: `.../wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=messstellen:grundwasser&count=1&outputFormat=application/json`
   → Properties `MESSST_BEZ, MESSST_ART, MESSST_ART_BEZ, ANZAHL_ANALYSEN, AMTL_NR`, Punkt EPSG:25832.
   **Kein aktueller Wert / Zeitreihen-Link im WFS.**
   Zeitreihe nur über Download-Assistent **AKSAM** `https://aksam-web.rlp-umwelt.de/aksam/index`
   (CSV-Export interaktiv, kein dokumentierter REST-Endpoint) [V].
4. **Zeitreihe:** nur manuell [V]; umwelt.info: Stationen maschinenlesbar, aber Zeitbezug „nicht vorhanden",
   kein automatisierter Download — Ganglinien nur via AKSAM (XHR-Reverse-Engineering nötig).
5. **Koordinaten:** EPSG:25832, GeoJSON direkt nutzbar [V].
6. **Auth/CORS:** WFS offen; AKSAM vermutlich session-basiert [A].
7. **Lizenz:** wahrscheinlich dl-de/by-2.0 (über open.rlp.de) [A].
8. **Aufwand: mittel.** Stationen/Umkreissuche sehr leicht (fertiges GeoJSON). Zeitreihe schwer —
   AKSAM-XHR muss per Browser-DevTools verifiziert werden.

---

## Saarland — SCHWER (zurückstellen)

1. **Behörde:** LUA (Landesamt für Umwelt- und Arbeitsschutz), „Grundwasser-Datenbank Saarland".
2. **Portal:** Geoportal Saarland (Mapbender); Info `saarland.de/mukmav/…/grundwasserueberwachung`.
   36 Stationen mit stündlicher Loggererfassung (laut Behörde).
3. **Zugang:** WFS nur **Standorte** [V]:
   `https://geoportal.saarland.de/arcgis/services/Internet/Wasser_WFS/MapServer/WFSServer?request=GetCapabilities&SERVICE=WFS&VERSION=1.1.0`
   → Typename `Wasser_WFS:Messstellen_Grundwasser` (ArcGIS-WFS, GML3, **keine Wasserstands-Attribute**).
   Messwerte nur über LUA-Grundwasser-Datenbank / öffentliches Formular.
4. **Zeitreihe: nein / nicht maschinenlesbar** [V] — umwelt.info: Download „nicht vorhanden",
   maschinenlesbar „Nein", Lizenz „other-closed".
5. **Koordinaten:** ja, WFS-Standortlayer, EPSG:25832 [V].
6. **Auth/CORS:** WFS offen; ArcGIS-WFS meist CORS-restriktiv (Server-Proxy einplanen) [A].
7. **Lizenz:** Standorte offen (GDI-SL), Messwerte other-closed.
8. **Aufwand: schwer.** Standorte gehen, aber der GW-Stand ist nicht ohne Login/Antrag maschinell
   abrufbar. Als Provider aktuell nur „Karte ohne Wert" — nicht sinnvoll. **Zurückstellen.**

---

## Sachsen — MITTEL–SCHWER (Stationen leicht, Werte schwer)

1. **Behörde:** Sächsisches Landesamt für Umwelt, Landwirtschaft und Geologie (LfULG); Betrieb durch BfUL.
2. **Portal:** iDA `https://www.umwelt.sachsen.de/umwelt/infosysteme/ida/p/grundwassermessstellen`;
   Geodaten-Hub LUIS `https://luis.sachsen.de/wasser/gw/gwmessstellen.html`.
3. **Zugang:** ArcGIS REST + WFS (nur Stammdaten), Werte via Cadenza.
   - **ArcGIS REST** [V]: `https://luis.sachsen.de/arcgis/rest/services/wasser/grundwassermessnetze/MapServer`,
     Layer 0 „Grundwassermessnetze", Punkt, Query aktiviert, wkid 25833.
     Umkreissuche: `.../MapServer/0/query?geometry={lon},{lat}&geometryType=esriGeometryPoint&inSR=4326&distance=5000&units=esriSRUnit_Meter&outFields=*&outSR=4326&f=geojson`.
   - **WFS 2.0.0** [V]: `https://luis.sachsen.de/arcgis/services/wasser/grundwassermessnetze/MapServer/WFSServer?service=WFS&request=GetCapabilities`,
     FeatureType `grundwassermessnetze:Grundwassermessnetze`, EPSG:25833.
   - **Werte/Zeitreihe:** nur über iDA = **Disy Cadenza** (session-basierte XHR, kein offener Endpoint).
4. **Zeitreihe:** eingeschränkt [V]. ArcGIS-Layer enthält **nur Stammdaten** (Felder `MKZG`, `MENA`,
   `MA`, `GISHOCH/GISRECHTS`, `MPH`, `GLH`, `HSYS`, `GANGLINIE`(Flag), `DATENSTAND`) — **kein Wasserstands-
   Feld**. Aktueller Wert + Ganglinie nur über iDA/Cadenza (Browser: CSV downloadbar).
5. **Koordinaten:** EPSG:25833 (WGS84 per `outSR=4326`) [V].
6. **Auth/CORS:** ArcGIS/WFS ohne Login; Cadenza-Werte session-gebunden.
7. **Lizenz:** dl-de/by-2.0 [V].
8. **Aufwand: mittel–schwer.** Umkreissuche/Koordinaten leicht (ArcGIS/WFS). Werte/Zeitreihe schwer
   (Cadenza-XHR reverse engineering, fragil). Ein reiner Messstellen-Provider wäre leicht.

---

## Sachsen-Anhalt — MITTEL–SCHWER

1. **Behörde:** Landesbetrieb für Hochwasserschutz und Wasserwirtschaft (LHW), Gewässerkundlicher
   Landesdienst (GLD).
2. **Portal:** GLD-Datenportal `https://gld.lhw-sachsen-anhalt.de/` (~1.200–1.300 GW-Messstellen).
   Backend: **KISTERS WISKI** [V, via MetaVer].
3. **Zugang:**
   - WFS `https://www.geodatenportal.sachsen-anhalt.de/wss/service/LHW_Gewaesserfachdaten_WFS/guest`
     enthält **kein Grundwasser** [V] (nur Einzugsgebiete, Fließgewässer, OW-Pegel, Deichlinien; EPSG:25832).
   - GLD-Portal: Download je Messstelle als CSV/XLSX/PDF/Shape [V] + interaktive Karte/Ganglinie.
     Ein öffentlicher **KiWIS**-REST-Endpoint (`…/KiWIS/KiWIS?service=kisters&type=queryServices&request=getStationList…`)
     **nicht bestätigt** [A] — muss per Netzwerk-Inspektion des gld-Portals ermittelt werden.
4. **Zeitreihe:** ja, nur per Download/Portal-XHR (CSV/XLSX ab 2007). Sauberer REST-Endpoint unklar.
5. **Koordinaten:** über Shapefile-Download [V], CRS vermutlich EPSG:25832 [A]. Kein WFS-Punktlayer für GW.
6. **Auth/CORS:** WFS teils INSPIRE-eingeschränkt; GLD-Downloads ohne Login.
7. **Lizenz:** „Nutzungsbestimmungen GLD" — nicht dl-de/by bestätigt.
8. **Aufwand: mittel–schwer.** Koordinaten via Shape-Import, Werte via Portal-XHR/KiWIS-Reverse-Engineering.
   **Falls ein öffentlicher KiWIS existiert** (getStationList + getTimeseriesValues als JSON) ⇒ sinkt auf
   leicht–mittel und wäre die sauberste Lösung — lohnt eine gezielte Portal-Netzwerkanalyse.

---

## Schleswig-Holstein — LEICHT–MITTEL (Quick Win)

1. **Behörde:** LfU SH (Landesamt für Umwelt SH), Abt. 4 Gewässer (früher LLUR).
2. **Portal:** Umweltportal SH `https://umweltportal.schleswig-holstein.de`; Open-Data
   `https://opendata.schleswig-holstein.de`.
3. **Zugang:** WFS (Stationen) + CSV (Werte).
   - **WFS 2.0.0** (deegree) [V]: `https://umweltgeodienste.schleswig-holstein.de/WFS_UWAT?SERVICE=WFS&REQUEST=GetCapabilities`
     → FeatureType **`app:gwmn`** = Landesmessstellen Grundwasserstand (733 Messstellen).
     Beispiel [V]: `.../WFS_UWAT?service=wfs&version=2.0.0&request=GetFeature&typeNames=app:gwmn&count=3`
     → je Station `Kurznummer`, `Messstellenname`, `Link`, `GEOM` (Punkt, EPSG:25832).
   - **Zeitreihe:** über `Link`-Attribut → Stationsseite, z.B.
     `https://umweltanwendungen.schleswig-holstein.de/db/dbnuis?thema=lgdms&ms_nr=10L59032001&ubs=ja&kopf` [V];
     GW-Stände als CSV über das Open-Data-Portal herunterladbar [V] (exakte CSV-URL noch per einmaliger
     Inspektion der Stationsseite abzuleiten).
4. **Zeitreihe: ja** [V] — umwelt.info bewertet SH als *maschinenlesbar* mit *„Ja (automatisiert)"*.
   7 Stationen Tages-Telemetrie, übrige alle 3–6 Monate geloggt.
5. **Koordinaten:** EPSG:25832 (Caps auch 4326/4258/31467) [V]. CRS-Umrechnung 25832→4326 nötig.
6. **Auth/CORS:** WFS offen, kein Login; liefert **GML** (kein natives GeoJSON — Parsing nötig).
7. **Lizenz:** dl-de/by-2.0 [V].
8. **Aufwand: leicht–mittel.** Umkreissuche: `app:gwmn` per WFS holen, GML parsen, 25832→WGS84.
   Fetch: pro Station CSV vom Open-Data-Portal. Reibung: GML statt GeoJSON und CSV-URL-Muster aus
   `Kurznummer`/`ms_nr` ableiten.

---

## Thüringen — SCHWER (zurückstellen)

1. **Behörde:** Thüringer Landesamt für Umwelt, Bergbau und Naturschutz (TLUBN).
2. **Portal:** „Kartendienst des TLUBN" = **antares / Disy Cadenza** `https://antares.thueringen.de/cadenza/`,
   GW-Seite `https://antares.thueringen.de/cadenza/p/wasser.4361` (Cadenza v9.7.146, servlet-basiert) [V].
3. **Zugang:** GIS-Portal Disy Cadenza [V]; ältere Servlet-XHR (`/cadenza/servlet/MapViewerServletNG`,
   jsessionid), reverse-engineerbar aber session-basiert und fragil.
   - WFS über `geoproxy.geoportal-th.de` hat **keinen GW-Messstellen-Layer** [V] (nur ALKIS/Kataster).
     Im Katalog nur Grundwasserflurabstand (Raster) + Grundwasserkörper (Polygone), keine Messstellen-Punkte.
   - Umweltportal Thüringen Open Data: nur Hochwasser/OW-Pegel, **kein GW-Open-Data** [V].
4. **Zeitreihe:** im Portal vorhanden (Cadenza-Ganglinie, Einzelwerte downloadbar), aber **kein
   öffentlicher/dokumentierter Endpoint** — nur Cadenza-XHR (session) [V/A].
5. **Koordinaten:** nur innerhalb Cadenza (kein offener WFS/REST-Punktlayer), CRS vermutlich 25832 [A].
6. **Auth/CORS:** Portal ohne Login, aber Abruf jsessionid-gebunden; teils CAPTCHA auf TLUBN-Seiten.
7. **Lizenz:** „offene Daten" laut Umweltportal, für GW konkret nicht verifiziert.
8. **Aufwand: schwer.** Weder Koordinaten- noch Zeitreihen-Provider haben einen offenen Endpoint;
   alles hängt an Cadenza-Reverse-Engineering (ältere Servlet-Version). **Zurückstellen.**

---

## Priorisierte Empfehlung — Quick Wins für die nächsten Provider

Rangfolge nach „Vollständigkeit des offenen Zugangs (Umkreissuche + Koordinaten + Zeitreihe) × geringster
Reverse-Engineering-Aufwand". Alle Top-5 sind **live per WebFetch verifiziert**.

1. **Hamburg (`bukea_hh`)** — *Top-Empfehlung.* **Ein** OGC-API-Features-JSON-Dienst
   (`api.hamburg.de/datasets/v1/grundwassermessstellen/…`) deckt Umkreissuche (`bbox`), Stationsliste,
   aktuellen Stand **und** komplette Ganglinie (m ü. NHN + m unter GOK) ab. Kein Login, CC-Zero,
   GeoJSON/WGS84 — kein CRS-Handling nötig. Geringste Reibung von allen 15 Ländern.

2. **Hessen (`hlnug_he`)** — Offene **ArcGIS-REST-API** mit Stationsliste + Koordinaten (`gruschu_mst_ga/…/0`)
   und **echten Ganglinien** (`wasserviewer/Auswertung/MapServer/22` = m NN, `20` = unter GOK), Join über
   `ID`==`GWM_ID`. ArcGIS-Umkreisabfrage (`distance`/`esriGeometryPoint`) direkt eingebaut. CC-BY 4.0,
   kein Token. Sehr solide, bewährtes ArcGIS-Muster.

3. **Berlin (`wasserportal_be`)** — Feste **GET-URLs** für Messstellenliste (`messwerte.php`), Stammdaten/
   Koordinaten (`station.php?anzeige=i`) und **CSV-Zeitreihe** (`station.php?anzeige=d…smode=c`) in m ü. NHN.
   dl-de/by-2.0. Einziger Aufwand: HTML-Tabellen- + Latin-1/Komma-CSV-Parsing; Referenz-Implementierung
   `KWB-R/wasserportal` existiert.

4. **Schleswig-Holstein (`lfu_sh`)** — **WFS `app:gwmn`** (733 Stationen, EPSG:25832) für Umkreissuche +
   pro Station **CSV** (automatisierbar, von umwelt.info bestätigt). dl-de/by-2.0. Leicht–mittel: GML-Parsing
   und das exakte CSV-URL-Muster (aus `Kurznummer`/`ms_nr`) noch einmalig festzuzurren.

5. **Niedersachsen (`nlwkn_ni`)** — Saubere **REST/JSON-API** (Azure APIM) mit Koordinaten (WGS84) und
   aktuellem Stand (m NHN & GOK) + **Niedrigwasserklasse** (passt konzeptionell zu NIWIS!). Leicht–mittel:
   Subscription-Key liegt offen im JS, GW-`STA_ID`-Liste muss aus `/Messwerte` extrahiert werden, und die
   volle Ganglinie (`datenspuren`-Array kam leer) ist noch zu klären — für einen ersten Wurf reicht der
   aktuelle Wert.

**Weitere, mit etwas mehr Aufwand (2. Welle):**
- **Rheinland-Pfalz** und **Sachsen** liefern Messstellen sehr leicht (RLP: GeoServer-**GeoJSON**;
  SN: ArcGIS-Query) — nur der Zeitreihen-Abruf ist schwer (RLP: AKSAM-XHR; SN: iDA/Cadenza-XHR). Gute
  Kandidaten für „Karte + Umkreissuche jetzt, Werte später".
- **Sachsen-Anhalt**: lohnt eine gezielte Prüfung, ob das WISKI-Backend einen **öffentlichen KiWIS**-JSON-
  Endpoint hat — dann schlagartig leicht (getStationList/getTimeseriesValues).
- **NRW**: sauberer Bulk-Zugang (OpenHygrisC + `index.json`, dl-de/zero), aber kein Live-Wert — eher
  periodischer Snapshot-Provider.
- **Bayern**: braucht das `enqueue_download`-`f`-Token (einmal Browser-XHR mitschneiden), sonst nur
  HTML-Scraping des aktuellen Werts.

**Vorerst zurückstellen (kein offener Zeitreihen-/Stand-Zugang):** Baden-Württemberg (Cadenza +
Datenschutz-Restriktion), Thüringen (Cadenza-Servlet), Mecklenburg-Vorpommern (kein Stand-Layer),
Saarland (Werte nur per Antrag), Bremen (Werte nur in Web-App).

---

*Alle mit [V] markierten Endpoints wurden am 2026-07-17 live abgerufen. CORS/Rate-Limits sind bei
Server-zu-Server-Abrufen aus Home Assistant i.d.R. unkritisch; ArcGIS-WFS (Saarland) kann jedoch
CORS-restriktiv sein. Lizenzen mit [A] vor kommerzieller/öffentlicher Weiterverbreitung final prüfen.*
