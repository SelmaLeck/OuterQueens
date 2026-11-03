# OuterQueens – Mod-Schnittstelle (Website-Patch)

Dieser ZIP ist **keine fertige Minecraft-Mod**. Er fügt deiner bestehenden Next.js-Website
sichere HTTP-Endpunkte für eine spätere Fabric-Client-Mod hinzu.

## Installation

1. Sicherheitskopie deines funktionierenden OuterQueens-Projektordners machen.
2. `app/api/mod`, `lib/mod-auth.ts` und `supabase/mod-integration.sql` in den vorhandenen Projektordner kopieren.
   **Nicht** das ganze Projekt austauschen; `.env` und `app/page.tsx` bleiben wie sie sind.
3. Supabase → SQL Editor: `supabase/mod-integration.sql` einmal ausführen.
4. `npm run build` lokal testen. Nur wenn der Build vollständig erfolgreich ist:
   `git add app/api/mod lib/mod-auth.ts supabase/mod-integration.sql`
   `git commit -m "Add OuterQueens mod bridge"`
   `git push`
5. Vercel muss dieselben zwei öffentlichen Supabase-Variablen haben wie die Webseite.
   **Niemals** den Service-Role-Key in der Client-Mod speichern.

## Endpunkte

- `POST /api/mod/session`: `{ "username": "Steve", "password": "..." }` → accessToken/refreshToken.
- `GET /api/mod/progress` mit `Authorization: Bearer <accessToken>` → Items + Fortschritt + Abgabekisten.
- `POST /api/mod/chests` mit Bearer: `{ "serverId":"example.net", "dimension":"minecraft:overworld", "x":10,"y":64,"z":15,"label":"Hauptabgabe" }` → chestId.
- `POST /api/mod/deliver` mit Bearer: `{ "eventId":"<random UUID>", "chestId":"<UUID>", "itemId":"<UUID aus progress>", "amount":64 }` → `recorded` / `already_recorded`.

## Wichtig zu korrektem Tracking

- Ein Retry **derselben eventId** zählt nicht doppelt.
- Neu erzeugte eventIds für dieselben Items können trotzdem doppelt zählen. Eine Client-Mod ohne Serverzugriff kann den Ursprung einzelner Items nicht beweisen.
- Spieler-Einlagerungen müssen clientseitig anhand der **serverbestätigten Inventaraktion** erfasst werden, nicht anhand eines rohen Maus-Klicks.
- Das Backend vertraut dem authentifizierten Client bei der Angabe, dass tatsächlich abgegeben wurde. Dies ist eine Team-Vertrauenslösung, keine serverseitig verifizierbare Anti-Cheat-Lösung.
- Eine echte Mod braucht außerdem Auth-Token-Refresh, sichere lokale Token-Aufbewahrung,
  Item-ID-Mapping (z.B. `minecraft:stone` → vorhandene items.id), Keybind/HUD,
  Chest-Erkennung sowie eine persistente Retry-Queue. All dies ist **noch nicht implementiert**.
- Es gibt kein lückenloses Tracking unbeobachteter Hopper-Transfers.
- Standardmäßig kann ein registrierter, angemeldeter Teamspieler Kisten registrieren. 
  Bei einem nicht vollständig vertrauenswürdigen Team sollten Adminrechte oder Freigaben ergänzt werden.
- Die bestehenden manuellen Eingaben funktionieren weiterhin.

## Sicherheit

Keine Zugangsdaten an andere Spieler schicken. Access-Tokens gehören nicht in Logs, GitHub oder Screenshots.
Die Route `/api/mod/session` sollte vor breiter Veröffentlichung mit einem Rate-Limit
und einem angemessenen Device-Login-Flow ergänzt werden. Login funktioniert nur
mit bestehenden OuterQueens-Spieler-Accounts.
