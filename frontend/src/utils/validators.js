/**
 * Email and Form Validation Utilities
 */

// Comprehensive RFC 5322 compatible regex requiring legitimate domain structure and minimum 2-char TLD
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

// Common legitimate email providers and domains
export const COMMON_EMAIL_DOMAINS = [
  'gmail.com',
  'googlemail.com',
  'yahoo.com',
  'ymail.com',
  'outlook.com',
  'hotmail.com',
  'live.com',
  'msn.com',
  'icloud.com',
  'me.com',
  'proton.me',
  'protonmail.com',
  'zoho.com',
  'aol.com',
  'mail.com',
  'gmx.com'
];

/**
 * Validates if an email address is properly formed and legitimate.
 * Rejects invalid syntax, missing/single-character TLDs, consecutive dots, and obvious junk inputs.
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const trimmed = email.trim().toLowerCase();

  // Basic regex check
  if (!EMAIL_REGEX.test(trimmed)) return false;

  // Reject consecutive dots
  if (trimmed.includes('..')) return false;

  const parts = trimmed.split('@');
  if (parts.length !== 2) return false;

  const [local, domain] = parts;
  if (!local || !domain) return false;

  // Local part cannot start or end with a dot or special char
  if (local.startsWith('.') || local.endsWith('.')) return false;

  // Domain must contain at least one dot separating domain and TLD
  const domainParts = domain.split('.');
  if (domainParts.length < 2) return false;

  // Each domain label must be alphanumeric or hyphen, but not starting/ending with hyphen
  for (const part of domainParts) {
    if (!part || part.length === 0) return false;
    if (part.startsWith('-') || part.endsWith('-')) return false;
    if (!/^[a-z0-9-]+$/.test(part)) return false;
  }

  // TLD must be purely alphabetical and between 2 and 24 characters
  const tld = domainParts[domainParts.length - 1];
  if (!/^[a-z]{2,24}$/.test(tld)) return false;

  // Disallow obvious bogus domains like test, localhost, bar, xyz, asdf
  const junkLabels = ['localhost', 'bar', 'xyz', 'asdf', 'fake', 'invalid'];
  const domainName = domainParts[0];
  if (junkLabels.includes(domainName)) return false;
  if (junkLabels.includes(tld)) return false;

  return true;
}

/**
 * Returns a human-friendly validation error message for an email input.
 * Returns null if valid.
 */
export function getEmailValidationError(email) {
  if (!email || !email.trim()) {
    return 'Please enter your email address.';
  }
  const trimmed = email.trim();
  if (!trimmed.includes('@')) {
    return 'Email address must include an "@" symbol (e.g. name@gmail.com).';
  }
  const parts = trimmed.split('@');
  if (parts.length > 2) {
    return 'Email address can only contain one "@" symbol.';
  }
  if (!parts[0]) {
    return 'Please enter the username portion before the "@" symbol.';
  }
  if (!parts[1] || !parts[1].includes('.')) {
    return 'Please include a valid domain extension like @gmail.com or @college.edu.';
  }
  const tld = parts[1].split('.').pop();
  if (!tld || tld.length < 2) {
    return 'Email domain must have a valid extension (e.g. .com, .edu, .org, .net).';
  }
  if (!isValidEmail(trimmed)) {
    return 'Please enter a legitimate email address (e.g. name@gmail.com, student@college.edu).';
  }
  return null;
}
