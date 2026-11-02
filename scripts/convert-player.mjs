import { identityFor, getAdminClient, exitOnError } from './_admin.mjs';

async function main() {
  const id = process.argv[2], displayName = process.argv[3];
  if (!id || !displayName) throw new Error('Aufruf: npm run player:convert -- AUTH-USER-UUID MinecraftName');
  if (!/^[0-9a-fA-F-]{36}$/.test(id)) throw new Error('Ungültige Auth-User-ID.');
  const { username, email } = identityFor(displayName);
  const client = getAdminClient();
  const existing = await client.auth.admin.getUserById(id);
  if (existing.error || !existing.data.user) throw existing.error || new Error('Account nicht gefunden.');
  const match = await client.from('profiles').select('id').eq('username', username).maybeSingle();
  if (match.error) throw match.error;
  if (match.data && match.data.id !== id) throw new Error('Dieser Username ist schon vergeben.');
  const { error } = await client.auth.admin.updateUserById(id, {
    email, email_confirm: true,
    user_metadata: { ...(existing.data.user.user_metadata || {}), username },
  });
  if (error) throw error;
  const changed = await client.from('profiles').update({ username }).eq('id', id);
  if (changed.error) throw changed.error;
  console.log(`✓ Bestehender Account umgestellt: ${displayName} + bisheriges Passwort.`);
  console.log('Alle bisherigen Beiträge bleiben dem Account zugeordnet.');
}
main().catch(exitOnError);
