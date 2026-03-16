import { makeVar } from '@apollo/client';

export const USER_STORAGE_KEY = 'relaycrm-user-id';

function readInitialUserId() {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.localStorage.getItem(USER_STORAGE_KEY);
}

export const selectedUserIdVar = makeVar<string | null>(readInitialUserId());

export function persistSelectedUserId(nextUserId: string | null) {
  if (typeof window !== 'undefined') {
    if (nextUserId) {
      window.localStorage.setItem(USER_STORAGE_KEY, nextUserId);
    } else {
      window.localStorage.removeItem(USER_STORAGE_KEY);
    }
  }

  selectedUserIdVar(nextUserId);
}

export function reloadPage() {
  if (typeof window !== 'undefined') {
    window.location.reload();
  }
}
