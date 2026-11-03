-- OuterQueens: einmal in Supabase SQL Editor ausführen.
-- Bestehende Accounts, Beiträge und Mod-Tabellen bleiben erhalten.
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS team_role text NOT NULL DEFAULT 'farmer';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS is_admin boolean NOT NULL DEFAULT false;
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_team_role_check;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_team_role_check CHECK (team_role IN ('builder','farmer'));
-- Ersetze DEIN_USERNAME mit deinem aktuellen OuterQueens-LOGIN-Username (nicht Anzeigename).
UPDATE public.profiles SET is_admin = true WHERE lower(username) = lower('DEIN_USERNAME');
-- Nur Anzeigename und Farbe sind für gewöhnliche Profile direkt veränderbar.
REVOKE UPDATE ON public.profiles FROM authenticated;
GRANT UPDATE (display_name, avatar_color) ON public.profiles TO authenticated;
-- Neue Profilfelder sind durch vorhandene SELECT-Policy für eingeloggte Spieler lesbar.
