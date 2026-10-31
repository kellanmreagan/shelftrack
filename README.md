# ShelfTrack: Action Figure Collection Tracker (MVP)

Single-file web app: open `index.html` in any browser. No backend; all data lives in the browser's localStorage.

## What's in it
- Landing section: headline, 3 benefits, Free vs Pro ($4/mo) pricing, email waitlist (stored locally under `shelftrack.waitlist`).
- App: add/edit/delete figures (name, line/brand, year, condition, paid, estimated value, photo URL), wishlist with target price, totals (paid vs value, gain/loss), search + line/condition filters, CSV import/export.
- Pro teasers (locked): price alerts, value tracking.
- `test.py`: headless Playwright smoke test (`python3 test.py`), writes `screenshot.png`.

CSV columns: `list,name,line,year,condition,paid,value,target,photo` (`list` = `owned` or `wish`).

## Next steps to monetize
1. **Stripe Payment Link**: create a $4/month recurring product in Stripe, make a Payment Link, and point the Pro "Join waitlist" button at it (or email the link to waitlist signups).
2. **Real waitlist**: swap the localStorage waitlist for a free form backend (Netlify Forms, Formspree, or Tally) so emails actually reach you.
3. **Host it free**: drag the folder onto Netlify Drop, or `vercel deploy`. Buy a cheap domain (~$10/yr).
4. **Build Pro for real**: add accounts + cloud sync (Supabase free tier), then price alerts/value tracking from eBay sold listings (eBay Browse API).
5. **Find collectors** (read each sub's self-promo rules first; lead with a free tool, not a pitch): r/actionfigures, r/BlackSeries, r/StarWarsCollecting, r/transformers, r/mcufigures, r/MarvelLegends, r/MOTU, r/ActionFigureCollecting, r/funkopop, plus collector Facebook groups.
6. **Goal math**: 25 Pro users × $4 = $100/month.
