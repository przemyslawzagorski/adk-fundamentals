// NotebookLM Cookie Exporter — background service worker (v3 CLIPBOARD)
// Enterprise blokuje fetch do localhost → używamy schowka systemowego
// Python czyta schowek przez powershell Get-Clipboard

let sent = false;

async function copyToClipboard(reason) {
  if (sent) return;

  const [googleCookies, nlmCookies] = await Promise.all([
    chrome.cookies.getAll({ domain: ".google.com" }),
    chrome.cookies.getAll({ domain: "notebooklm.google.com" }),
  ]);
  const all = [...googleCookies, ...nlmCookies];
  if (all.length === 0) { console.log("[CookieExporter] No cookies yet"); return; }

  // Próba 1: fetch do localhost (może działać jeśli enterprise nie blokuje)
  try {
    const resp = await fetch("http://localhost:8765/cookies", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(all),
    });
    if (resp.ok) {
      console.log(`[CookieExporter] ✅ Sent via HTTP (${reason}), ${all.length} cookies`);
      sent = true;
      return;
    }
  } catch (_) { /* fallback to clipboard */ }

  // Próba 2: schowek systemowy (fallback)
  const payload = "NLMCOOKIES:" + JSON.stringify(all);
  try {
    // Otwórz offscreen document żeby mieć dostęp do clipboard API
    await chrome.offscreen.createDocument({
      url: chrome.runtime.getURL("offscreen.html"),
      reasons: ["CLIPBOARD"],
      justification: "Export cookies to clipboard",
    }).catch(() => {}); // może już istnieć
    // Wpisz do active tab via content script clipboard write
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      await chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        func: (data) => {
          navigator.clipboard.writeText(data).catch(() => {
            // Fallback: document.execCommand
            const el = document.createElement("textarea");
            el.value = data;
            document.body.appendChild(el);
            el.select();
            document.execCommand("copy");
            document.body.removeChild(el);
          });
        },
        args: [payload],
      });
      console.log(`[CookieExporter] ✅ Copied to clipboard (${reason}), ${all.length} cookies`);
      sent = true;
    }
  } catch (e) {
    console.error("[CookieExporter] Clipboard failed:", e.message);
  }
}

// 1. Kliknięcie ikony — GŁÓWNY TRIGGER (user activation → clipboard działa)
chrome.action.onClicked.addListener(async (tab) => {
  console.log("[CookieExporter] Icon clicked on:", tab.url);
  await copyToClipboard("icon_click");
});

// 2. Nowe taby NotebookLM
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete") return;
  if (!tab.url?.startsWith("https://notebooklm.google.com/")) return;
  copyToClipboard("tab_updated");
});

// 3. Już otwarte taby + polling
chrome.runtime.onInstalled.addListener(async () => {
  await new Promise(r => setTimeout(r, 3000));
  let tries = 0;
  const iv = setInterval(async () => {
    if (sent || ++tries > 30) { clearInterval(iv); return; }
    const tabs = await chrome.tabs.query({ url: "https://notebooklm.google.com/*" });
    if (tabs.length > 0) await copyToClipboard(`poll_${tries}`);
  }, 5000);
});
