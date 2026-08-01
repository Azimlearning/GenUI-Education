/**
 * Per-tab anonymous session id, held in memory only.
 * No localStorage/sessionStorage (TECHNICAL.md frontend conventions);
 * a page reload simply starts a fresh anonymous session.
 */
let sessionId: string | null = null;

export function getSessionId(): string {
  if (!sessionId) {
    sessionId = `sess_${crypto.randomUUID()}`;
  }
  return sessionId;
}
