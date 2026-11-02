import { identityFor, getAdminClient, askNewPassword, exitOnError } from './_admin.mjs';

async function main() {
  const displayName = process.argv[2];
  if (!displayName) throw new Error('Aufruf: npm run player:add -- MinecraftName');
  const { username, email } = identityFor(displayName);
  const client = getAdminClient();
  const password = await askNewPassword();
  const { error } = await client.auth.admin.createUser({
    email, password, email_confirm: true,
    user_metadata: { username, display_name: displayName },
  });
  if (error) throw error;
  console.log(`✓ Spieler ${displayName} angelegt. Login: ${displayName} + Passwort.`);
  console.log('Keine echte E-Mail-Adresse erforderlich.');
}
main().catch(exitOnError);
