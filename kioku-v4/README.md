# KIOKU V6

KIOKU is an independent English-language reference catalogue for Japanese anime figure lines, with collector discovery and condition-note tools. Catalogue references do not imply physical stock, pricing, maker authorization, or checkout.

## Pages and features

- Home, Collection, Figure Finder, line reference detail, Condition Guide, Journal, and About.
- Search, maker and line filters, sorting, saved references, shareable filters, and comparison of up to three references.
- Three-question Finder, reference diagram zoom, and a private local condition-note tool with copy and text export.

## Source layout

The seven HTML entry points live in `pages/`. The site header, footer and search dialog live in `components/`. The build resolves those includes and writes the existing public HTML routes at the root of `dist/`.

`data/` reads page templates for the build and handles browser storage for saved references and comparison. The collector interactions remain in `features/`.

## Build

```sh
npm test
npm run build
npm run preview
```

The static build writes `dist/`. For a local HTTP preview, run `python3 -m http.server 8000 -d dist` and open `http://localhost:8000`. The standalone preview is written to `KIOKU-V6-Interactive-Website-Preview.html`.

The browser QA uses Playwright with Chromium and tests five viewport widths; it can also run against WebKit with `KIOKU_BROWSER=webkit npm run qa:browser`. It creates no screenshots.
