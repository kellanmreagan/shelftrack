# ShelfTrack: Action Figure Collection Tracker

Live: https://kellanmreagan.github.io/shelftrack/

Single-file web app: open `index.html` in any browser. No backend; collection data lives in the browser's localStorage.

## What's in it
- Landing section: headline, "Start tracking free" CTA, 3 benefits, Free vs Pro ($4/mo, coming soon) pricing, Pro waitlist form in the Pro card.
- App: add/edit/delete figures (name, line/brand, year, condition, paid, estimated value, photo URL), wishlist with target price, totals (paid vs value, gain/loss), search + line/condition filters, CSV import (Merge or Replace, duplicates skipped, prices sanitized) and export.
- Pro teasers (locked): price alerts, value tracking.
- `robots.txt`, `sitemap.xml`, `og.png` (1200x630 social preview), inline SVG favicon.
- `test.py`: headless Playwright smoke test (`python3 test.py`): core tracker, import/export, waitlist (empty and mocked endpoint), and a 390px mobile check. Writes `screenshot.png`, `mobile.png`, `mobile-modal.png`.

CSV columns: `id,list,name,line,year,condition,paid,value,target,photo` (`list` = `owned` or `wish`; `id` is optional and used for de-duplication).

## Turning on the waitlist (Formspree)
Right now `WAITLIST_ENDPOINT` is empty, so the form shows "Waitlist opening soon. Use Start free in the meantime." and collects nothing. To collect real signups:
1. Create a free account at https://formspree.io and make a new form. Copy its endpoint, e.g. `https://formspree.io/f/abcdwxyz`.
2. In `index.html`, find the `CONFIG` block at the top of the `<script>` and set:
   ```js
   const WAITLIST_ENDPOINT = 'https://formspree.io/f/abcdwxyz';
   ```
3. Commit and push. The form POSTs `{"email": "...", "source": "shelftrack"}` as JSON with `Accept: application/json`. It shows "You're on the list!" only on a 2xx response, and an error message otherwise.
4. Submit a test email on the live site and confirm it appears in Formspree (the first submission may ask you to confirm the form by email).

Any service that accepts a JSON POST and returns 2xx works the same way (Buttondown, ConvertKit, a Google Apps Script, etc.).

## Next steps to monetize
1. **Stripe Payment Link**: create a $4/month recurring product in Stripe, make a Payment Link, and email it to waitlist signups when Pro is ready.
2. **Build Pro for real**: add accounts + cloud sync (Supabase free tier), then price alerts/value tracking from eBay sold listings (eBay Browse API).
3. **Find collectors** (read each sub's self-promo rules first; lead with a free tool, not a pitch): r/actionfigures, r/BlackSeries, r/StarWarsCollecting, r/transformers, r/mcufigures, r/MarvelLegends, r/MOTU, r/ActionFigureCollecting, r/funkopop, plus collector Facebook groups.
4. **Goal math**: 25 Pro users × $4 = $100/month.
