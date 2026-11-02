// Supabase Auth requires email or phone for password login.
// Players only use a username: map it deterministically to an internal, non-deliverable identifier.
// This is NOT a real email address; never use password-reset emails with these accounts.
export const USERNAME_PATTERN = /^[A-Za-z0-9_]{2,20}$/;
export const INTERNAL_LOGIN_DOMAIN = 'players.blockforge.invalid';
export function usernameLoginEmail(value: string): string | null {
  const username = value.trim();
  return USERNAME_PATTERN.test(username)
    ? `${username.toLowerCase()}@${INTERNAL_LOGIN_DOMAIN}`
    : null;
}
