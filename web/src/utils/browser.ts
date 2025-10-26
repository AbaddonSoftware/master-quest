export function isEmbeddedBrowser(): boolean {
  if (typeof navigator === "undefined") {
    return false;
  }
  const ua = navigator.userAgent ?? "";
  return /AdobeAcrobat|; wv\)|\bWebView\b|FBAN|FBAV|Instagram|LinkedInApp|WhatsApp|WAWebClient|Twitter|Line\/|MicroMessenger|GSA/i.test(
    ua
  );
}
