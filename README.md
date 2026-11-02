# BLOCKFORGE BLUE EDITION 💠
### Cinderella’s Castle — Minecraft Team-Dashboard

Ein Next.js/TypeScript-Projekt im dunkelblauen Electric-Blue-Design. Für VS Code → GitHub → Vercel vorbereitet, mit Supabase für gemeinsame Username/Passwort-Accounts, Materialfortschritt, Farmplanung, Litematica-Schematic-Uploads, Profilen und Leaderboards.

## Die echte Materialliste ist schon drin

- **317 übermittelte Material-Zeilen**, **316 zusammengefasste Items**, **146.527 Stück insgesamt**.
- Projekt: **Cinderella’s castle** (1 von 1 Litematica-Regionen).
- Alle Mengen starten als **0 gesammelt**. Sie sind echte Zielmengen aus deinen Screenshots und deinem Text, keine Demo-Daten.
- Alle Einträge mit Deutsch/Englisch, Stacks (individuelle Stackgrößen), Doppeltruhen mit **54 Slots** und vorhandenen Crafting-Hinweisen.
- **25 vorbereitete Farm-Planungsseiten** (soweit sinnvolle Verknüpfungen möglich). Diese enthalten noch **keine erfundenen Schematics oder Bau-Materiallisten**. Euer Team kann sie bei Bedarf ergänzen.
- Die im übermittelten Material doppelt enthaltene **„Eichenholzdruckplatte“** (46 + 2) wurde zu **48** zusammengeführt. Bei Bedarf in `data/cinderella-materials.tsv` anpassen.
- Manche komplexe Crafting-Rezepte sind bewusst noch **nicht** hinterlegt: Berechnet werden vor allem Treppen, Stufen und Mauern anhand der Crafting-Werkbank-Rezepte. Für Holztreppen werden auch grobe Holzstamm-Mengen angezeigt. Eine Steinsäge kann bei Steinrezepten günstiger sein.

### Wichtige Dateien

| Datei | Funktion |
|------|----------|
| `supabase/schema.sql` | Tabellen, Zugriffsschutz, Dateispeicher und sichere Beitragsfunktion |
| `supabase/seed-cinderella.sql` | **Alle 316 Items + 25 Farmen** automatisch in die Datenbank übertragen |
| `supabase/safe-contributions.sql` | Zusatzmigration für bestehende BLOCKFORGE-Datenbanken |
| `supabase/username-login-migration.sql` | Username-Login für bereits bestehende Datenbanken |
| `scripts/create-player.mjs` | Neue Spieler nur mit Minecraft-Username + Passwort anlegen |
| `scripts/reset-player-password.mjs` | Passwörter als Admin zurücksetzen |
| `data/cinderella-materials.csv` | Lesbare Materialliste, z. B. in Excel öffnen |
| `data/cinderella-materials.json` | Strukturierte Items/Farmen/Rezepte |
| `data/cinderella-materials.tsv` | Ursprüngliche Material-Zeilen aus deinem Post |
| `scripts/build_seed.py` | SQL-/JSON-Dateien nach TSV-/Übersetzungsänderungen neu erzeugen |

## A — Supabase: Datenbank + individuelle Logins einrichten

1. Lege ein Projekt auf https://supabase.com an.
2. Öffne im Projekt den **SQL Editor**.
3. Bei einer **ganz neuen** Datenbank: `supabase/schema.sql` komplett kopieren und **einmal** ausführen.
4. **Danach** `supabase/seed-cinderella.sql` im SQL Editor ausführen. Damit erscheinen die Items und Farmen auf der Website. Das Seed-Skript kann erneut ausgeführt werden, ohne neue Duplikate dieser Start-Items zu erzeugen. Achtung: Es setzt die Start-Zielmengen wieder auf die Dateienwerte (nicht aber Spielerbeiträge) zurück.
5. Unter **Authentication → Providers/Signups** die öffentliche Registrierung **deaktivieren**. Es gibt auf der Website absichtlich kein Registrierungsformular.
6. Aus den Supabase-Einstellungen die **Project URL** und den **publishable/anon key** kopieren. Nur diese beiden öffentlichen Werte gehören in die Website (siehe B).
7. **Spieler anlegen, ganz ohne ihre E-Mail-Adresse:** Siehe Abschnitt **„Spieler-Accounts erstellen“**. Du brauchst nur Minecraft-Namen und Passwort.

**Falls du die alte BLOCKFORGE-Version schon in Supabase installiert hast:** Führe **nicht nochmal** `schema.sql` aus, weil bestehende Policies schon vorhanden sein können. Stattdessen zuerst `supabase/safe-contributions.sql`, danach `supabase/username-login-migration.sql` und schließlich (falls noch nicht erledigt) `supabase/seed-cinderella.sql` ausführen.

## Spieler-Accounts erstellen – Username + Passwort, ohne echte E-Mail

Die Website fragt **nur Username + Passwort** ab. Die Mitspieler müssen **keine E-Mail angeben oder besitzen**. Intern verwendet Supabase Auth technisch E-Mail/Passwort; BLOCKFORGE bildet `Steve123` automatisch auf einen **nicht zustellbaren, reservierten Platzhalter** `steve123@players.blockforge.invalid` ab. Das ist **keine echte E-Mail** und dient nur zur internen Anmeldung. Entsprechend gibt es **keine Passwort-zurücksetzen-per-Mail-Funktion** – das machst du als Admin.

### Einmalige Admin-Einrichtung (nur auf deinem PC)

1. `npm install` im VS-Code-Terminal ausführen.
2. Im Projektordner `.env.admin.example` kopieren und die Kopie **`.env.admin.local`** nennen.
3. In `.env.admin.local` **SUPABASE_URL** (Project URL) und **SUPABASE_SERVICE_ROLE_KEY** (im Supabase Dashboard unter Project Settings → API Keys → Legacy service_role / Secret Key) eintragen. **Dieser Schlüssel ist extrem mächtig: ausschließlich lokal für die Admin-Skripte! Niemals in Vercel, ein öffentliches Repository, den Browser oder einen Screenshot kopieren.** `.gitignore` schützt die Datei vor normalem Git-Commit.
4. Für jeden Freund den Befehl aufrufen:

   ```bash
   npm run player:add -- Steve123
   ```

   Das Skript fragt **zweimal verdeckt** nach dem neuen Passwort (mindestens 12 Zeichen), legt den Spieler in Supabase Auth an und hinterlegt das Profil. Der Username ist nicht groß-/kleinschreibungssensitiv und besteht aus 2–20 Zeichen (Buchstaben, Zahlen, `_`). **Als Admin zuerst auch deinen eigenen Account anlegen.**

5. Deine Freunde besuchen die Vercel-Website und melden sich mit `Steve123` + Passwort an. **Kein E-Mail-Feld, keine Registrierung.**

### Passwort vergessen?

Im VS-Code-Terminal als Admin:

```bash
npm run player:password -- Steve123
```

Das Passwort wird verdeckt eingegeben und mit Supabase Auth geändert.

### Bereits bestehende Account-Daten behalten

Wenn du vor der Umstellung bereits E-Mail-Accounts für Freunde angelegt hast, **nicht löschen** (sonst gehen möglicherweise verknüpfte Beiträge verloren). Führe zuerst `supabase/username-login-migration.sql` aus und nutze für jeden bestehenden Account die **User-ID aus Supabase → Authentication → Users**:

```bash
npm run player:convert -- 00000000-0000-0000-0000-000000000000 Steve123
```

Die User-ID durch die echte UUID ersetzen. Das bestehende Passwort und die gesammelten Beiträge bleiben erhalten. Erst danach mit dem Username anmelden.

**Hinweis:** Weil die technischen Identifikatoren keine echten Mailadressen sind, kannst du weder E-Mail-Verifizierung noch Passwort-Reset-Mails verwenden. Achte deshalb auf starke Passwörter und sichere Admin-Schlüssel.

## B — Website lokal in VS Code starten

Voraussetzung: **Node.js 20.9+**, npm und VS Code.

```bash
npm install
```

Erstelle im Projektordner aus `.env.example` eine Datei `.env.local` mit:

```env
NEXT_PUBLIC_SUPABASE_URL=https://DEIN-PROJEKT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=DEIN-PUBLISHABLE-ODER-ANON-KEY
```

**Das sind öffentliche Client-Schlüssel**, keine Passwort-/Server-Geheimnisse. Anschließend:

```bash
npm run dev
```

Dann http://localhost:3000 öffnen, mit deinem Minecraft-Username + Passwort einloggen (siehe Spieler-Accounts).

## C — GitHub und Vercel

1. In VS Code ein Terminal öffnen: `git init`, `git add .`, `git commit -m "Blockforge Cinderella blue"`.
2. Auf https://github.com ein **privates Repository** erstellen. Dessen URL als Git-Remote hinterlegen und pushen:

   ```bash
   git branch -M main
   git remote add origin https://github.com/DEIN-USERNAME/DEIN-REPO.git
   git push -u origin main
   ```

3. Auf https://vercel.com → **Add New → Project** → Repository auswählen.
4. **Nur** die beiden `NEXT_PUBLIC_...`-Umgebungsvariablen in Vercel eintragen (Production, ggf. Preview). **Nicht** `SUPABASE_SERVICE_ROLE_KEY` hochladen.
5. Deploy durchführen. Für spätere Updates genügt ein GitHub-Push.

## Benutzung

- **MAIN BUILDING**: Items nach Deutsch/Englisch suchen. Je Item zeigen Karten Soll/Ist, verbleibende Items, Stacks, Doppelchests, Crafting-Hinweis, passende Farm (wenn vorhanden) und zuständige Spieler. „Übernehmen“ trägt **dich** ein; „Hinzufügen“ verbucht deinen gesammelten Beitrag.
- **FARMEN**: Farm-Planung, Status, Baumaterialliste, zuständige Spieler und `.litematic`/`.schem`/`.schematic`-Schematic hochladen (bis 10 MB). Über Item-Link direkt zur Farm springen.
- **TEAM**: Alle Profile sehen, eigenes Profil mit Anzeigenamen/Avatarfarbe bearbeiten.
- **STATISTIKEN**: Top-Sammler, spezialisierte Sammler, Team-Fortschritt. Der Fortschrittsbalken ist unten sichtbar. Aktualisierung alle 10 Sekunden (Polling, nicht WebSocket-Echtzeit).

## Sicherheit und Grenzen

- Nur eingeloggte Username/Passwort-Accounts dürfen Daten sehen oder ändern; Supabase Row Level Security ist eingeschaltet. **Alle Teammitglieder** dürfen jedoch Items/Farmen pflegen. Es gibt noch keine getrennte Admin-Rolle für das Board.
- Eingetragene gesammelte Items werden als nicht editierbares Beitragsprotokoll gespeichert. Die Datenbankfunktion sperrt parallele Einträge für dasselbe Item kurzzeitig und verhindert damit Überschreitung der Sollmenge.
- Farm-Schematic-Dateien liegen in einem **öffentlich lesbaren** Supabase Storage-Bucket (über die bekannte öffentliche URL). Keine privaten Dateien hochladen.
- Der importierte Text-/Screenshot-Export wurde manuell übertragen. **Bitte prüfe besonders seltene Items und die doppelte Eichenholzdruckplatte**, da Bildabschriften einzelne Tippfehler enthalten können.
- Eine automatisch aus `.litematic` extrahierte Materialliste gibt es nicht; das vorliegende Projekt benutzt den bereits übermittelten Material-Export.
- In dieser Umgebung konnte kein `npm install`/Live-Build mit Datenbankverbindung durchgeführt werden. Vor der Veröffentlichung bitte lokal `npm install` und `npm run build` ausführen.
