# tinyheadlines.live

Static one-page site around the 24/7 live stream. Served by GitHub Pages from the repo
`yeikiu/tinyheadlines.live` (branch `main`, root), custom domain in `CNAME`.

The source of truth is this folder (`web/`) of the Tiny Headlines repo. To publish a change:

    git subtree split --prefix web -b web-pages
    git push https://github.com/yeikiu/tinyheadlines.live.git web-pages:main --force

The live player is the YouTube "live_stream?channel=" embed, which always points at the current broadcast.
It fills the first viewport; the Unmute button drives it through `postMessage` (no extra script).

No build step: one `index.html` with inline CSS and JS. Assets:

- `assets/fonts/bricolage-grotesque.woff2` — Bricolage Grotesque (variable, latin), SIL Open Font License 1.1.
- `assets/d-*.webp` — stills of dioramas that aired (crops of `docs/review/elaborate/*-after.png`).
- `assets/logo.webp` — the logo, lighter copy of `assets/logo.png`.

Google Analytics 4: set the Measurement ID in the `GA_ID` constant at the top of `<head>` in `index.html`.
While it is the placeholder `G-XXXXXXXXXX` nothing is loaded. Consent Mode v2 starts with everything denied;
`gtag.js` is fetched only after the visitor presses Accept in the cookie banner (choice kept in
`localStorage` under `th-consent`; "Cookie settings" in the footer reopens it).
