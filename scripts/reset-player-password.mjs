import { identityFor, getAdminClient, askNewPassword, exitOnError } from './_admin.mjs';

async function main() {
  if (!process.argv[2]) throw new Error('Aufruf: npm run player:password -- MinecraftName');
  const { username } = identityFor(process.argv[2]);
  const client = getAdminClient();
  const { data, error } = await client.from('profiles').select('id').eq('username', username).maybeSingle();
  if (error) throw error;
  if (!data) throw new Error('Spieler nicht gefunden.');
  const password = await askNewPassword();
  const result = await client.auth.admin.updateUserById(data.id, { password });
  if (result.error) throw result.error;
  console.log(`✓ Neues Passwort für ${username} gespeichert.`);
}
main().catch(exitOnError);
