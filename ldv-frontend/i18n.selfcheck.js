// Run: node ldv-frontend/i18n.selfcheck.js
// Asserts every DICT key in i18n.js exists in both `en` and `id`.
// Pure Node — requires i18n.js directly (no eval / new Function / string
// interpolation of file contents; i18n.js guards its browser-only globals
// so it's safe to require() outside a browser).
const { DICT } = require("./i18n.js");

const enKeys = new Set(Object.keys(DICT.en));
const idKeys = new Set(Object.keys(DICT.id));

const missingInId = [...enKeys].filter(function (k) { return !idKeys.has(k); });
const missingInEn = [...idKeys].filter(function (k) { return !enKeys.has(k); });

if (missingInId.length || missingInEn.length) {
  if (missingInId.length) console.error("Missing Indonesian translation for:", missingInId);
  if (missingInEn.length) console.error("Missing English translation for:", missingInEn);
  process.exit(1);
}

console.log("OK: " + enKeys.size + " keys, EN/ID parity confirmed.");
