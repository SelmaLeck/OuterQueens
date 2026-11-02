import { createClient } from '@supabase/supabase-js';

const USERNAME_RE = /^[A-Za-z0-9_]{2,20}$/;
const INTERNAL_DOMAIN = 'players.blockforge.invalid';

export function identityFor(raw) {
  if (!USERNAME_RE.test(raw)) throw new Error('Username: 2–20 Zeichen, nur A–Z, 0–9 und _.');
  const username = raw.toLowerCase();
  return { username, email: `${username}@${INTERNAL_DOMAIN}` };
}

export function getAdminClient() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error('SUPABASE_URL und SUPABASE_SERVICE_ROLE_KEY fehlen in .env.admin.local.');
  return createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

// Prevent accidental printing of a friend's password in the terminal.
export async function askHidden(prompt) {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    throw new Error('Bitte in einem interaktiven VS-Code-Terminal starten.');
  }
  process.stdout.write(prompt);
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding('utf8');
  return new Promise((resolve, reject) => {
    let result = '';
    const cleanup = () => { process.stdin.off('data', onData); process.stdin.setRawMode(false); process.stdin.pause(); };
    const onData = (chunk) => {
      for (const char of chunk) {
        if (char === '\r' || char === '\n') {
          process.stdout.write('\n'); cleanup(); resolve(result); return;
        }
        if (char === '\u0003') {
          process.stdout.write('\n'); cleanup(); reject(new Error('Abgebrochen.')); return;
        }
        if (char === '\u007f' || char === '\b') {
          if (result.length) { result = result.slice(0, -1); process.stdout.write('\b \b'); }
        } else if (char >= ' ' && char !== '\u007f') {
          result += char;
          process.stdout.write('•');
        }
      }
    };
    process.stdin.on('data', onData);
  });
}

export async function askNewPassword() {
  const first = await askHidden('Neues Passwort (mind. 12 Zeichen): ');
  if (first.length < 12) throw new Error('Bitte mindestens 12 Zeichen verwenden.');
  const second = await askHidden('Passwort wiederholen: ');
  if (first !== second) throw new Error('Die Passwörter stimmen nicht überein.');
  return first;
}

export function exitOnError(e) { console.error('Fehler:', e instanceof Error ? e.message : e); process.exitCode = 1; }
