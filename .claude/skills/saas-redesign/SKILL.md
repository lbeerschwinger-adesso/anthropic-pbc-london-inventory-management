---
name: saas-redesign
description: Drives a full modern-SaaS UI redesign of this Vue 3 app — replaces the top nav with a left sidebar, introduces a CSS design-token system, and restyles all views for a polished professional look. Use when asked to redesign, modernize, or overhaul the app's UI / give it a SaaS look / add a sidebar.
---

# Modern SaaS UI Redesign

This skill drives a full UI overhaul of the Factory Inventory Management app: it replaces the
horizontal top nav bar with a **left vertical sidebar**, extracts a **CSS design-token system**, and
restyles every view for a consistent, polished, modern-SaaS look.

You are the **orchestrator**. You do not edit `.vue` files or `client/src/*.js` yourself — you
delegate every client-side change to the **vue-expert** subagent and verify the result with
**Playwright MCP**. Work through the phases in order. Create a TodoWrite item per phase and per view.

## Purpose & When to Use

Invoke this skill when the user asks to redesign, modernize, or overhaul the app's interface; give it
a "SaaS look"; add a sidebar; or improve visual consistency/polish.

Locked design decisions (do not revisit — they were chosen by the user):

- Top nav bar → **left vertical sidebar** (sidebar is nav-only).
- **Light** sidebar: white background, slate text, subtle right border; active item = light-blue
  background + blue text + a left accent bar.
- Sidebar nav items get **inline SVG icons** (icon + label). **No new npm dependency.**
- **Full design-system overhaul**: a CSS-variable token system + consistent spacing + restyled
  cards/tables/badges across all views — not just the nav.

## Hard Rules (read first)

1. **All `.vue` and `client/src/*.js` edits go through `vue-expert`** via the Task tool. The root
   `CLAUDE.md` mandates this for any `.vue` change; for consistency, route `main.js` and locale `.js`
   edits through vue-expert too. The orchestrator only reads, orchestrates, and verifies.
2. **Inline SVG icons only — no new npm dependency.** Do not add an icon or component library. This
   matches the repo's "custom SVG" convention.
3. **Manage servers with the `start`/`stop` skills.** Verify everything with **Playwright MCP** against
   `http://localhost:3000` (frontend) and `http://localhost:8001` (API).
4. **Preserve behavior.** Every delegated change must keep existing data bindings, props, events,
   `v-for` keys (never use `index` as a key — use `sku`, `month`, route path, etc.), and
   loading→error→render states.
5. **Never touch SVG chart geometry.** Charts in Dashboard/Reports/Spending/Demand use `viewBox`,
   coordinate math, scales, and data bindings. Only recolor strokes/fills (via tokens) and adjust the
   surrounding container spacing. Do not change `viewBox`, coordinates, scales, or `:key`s.

## Target Architecture

End-state `App.vue` is a CSS-grid app shell: a fixed-width sidebar column plus a main area that holds a
topbar and the scrollable content.

```vue
<div class="app-shell">                       <!-- grid: var(--sidebar-w) 1fr; min-height: 100vh -->
  <Sidebar />                                 <!-- NEW: the only nav; full height -->
  <div class="app-main">                      <!-- flex column; min-width: 0 (prevents grid overflow) -->
    <TopBar @show-profile-details="..." @show-tasks="..." />  <!-- NEW: FilterBar + LanguageSwitcher + ProfileMenu -->
    <main class="main-content"><router-view /></main>
  </div>
  <ProfileDetailsModal ... />                 <!-- stays at root (fixed overlay) -->
  <TasksModal ... />                          <!-- stays at root (fixed overlay) -->
</div>
```

**New components (created via vue-expert):**

- `client/src/components/Sidebar.vue` — logo + the 6 nav `<router-link>`s with inline SVG icons.
  Replaces the entire `<header class="top-nav">` block.
- `client/src/components/TopBar.vue` — composes `FilterBar` + `LanguageSwitcher` + `ProfileMenu`, and
  **re-emits** `show-profile-details` / `show-tasks` from the nested `ProfileMenu` up to `App.vue` so
  the root-level modals still open.

**Relocations:**

- The 6 `<router-link>`s + `.logo` → `Sidebar.vue`.
- `LanguageSwitcher`, `ProfileMenu`, `FilterBar` → `TopBar.vue`.
- The global `<style>` block stays in `App.vue`, but `.top-nav`/`.nav-tabs` rules are removed and
  remaining hardcoded hex values become `var(--token)` references.
- `ProfileDetailsModal` / `TasksModal` stay at the App root (they are `position: fixed` overlays). Only
  the event source (`ProfileMenu`) moves, so App passes the handlers down through `TopBar`.

## The Design Token System

Create **`client/src/styles/tokens.css`** with a `:root` block and import it once in
`client/src/main.js` (`import './styles/tokens.css'` near the top). Custom properties pierce scoped
styles, so every view can consume these tokens — this is the mechanism that makes the per-view restyle
work. Values are derived from the existing palette so the redesign refines the look rather than
recoloring it.

```css
:root {
  /* surfaces & text */
  --color-bg:#f8fafc; --color-surface:#ffffff; --color-surface-alt:#f8fafc;
  --color-text:#0f172a; --color-text-muted:#64748b; --color-text-subtle:#94a3b8;
  --color-border:#e2e8f0; --color-border-strong:#cbd5e1; --color-hover-bg:#f1f5f9;
  /* brand */
  --color-primary:#2563eb; --color-primary-hover:#1d4ed8; --color-primary-bg:#eff6ff; --color-primary-text:#2563eb;
  /* status fg/bg/text */
  --color-success:#059669; --color-success-bg:#d1fae5; --color-success-text:#065f46;
  --color-warning:#ea580c; --color-warning-bg:#fed7aa; --color-warning-text:#92400e;
  --color-danger:#dc2626;  --color-danger-bg:#fecaca;  --color-danger-text:#991b1b;
  --color-info:#2563eb;    --color-info-bg:#dbeafe;    --color-info-text:#1e40af;
  --color-stable-bg:#e0e7ff; --color-stable-text:#3730a3;
  /* spacing (4px base) */
  --space-1:.25rem; --space-2:.5rem; --space-3:.75rem; --space-4:1rem;
  --space-5:1.25rem; --space-6:1.5rem; --space-8:2rem; --space-10:2.5rem;
  /* radius */
  --radius-sm:6px; --radius-md:10px; --radius-lg:14px; --radius-full:9999px;
  /* shadow */
  --shadow-xs:0 1px 2px 0 rgba(0,0,0,.04); --shadow-sm:0 1px 3px 0 rgba(0,0,0,.05);
  --shadow-md:0 4px 12px rgba(0,0,0,.06); --shadow-lg:0 10px 24px rgba(0,0,0,.08);
  /* typography */
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --text-xs:.75rem; --text-sm:.875rem; --text-base:.938rem; --text-lg:1.125rem;
  --text-xl:1.375rem; --text-2xl:1.875rem; --text-3xl:2.25rem;
  --font-medium:500; --font-semibold:600; --font-bold:700;
  --leading-tight:1.2; --leading-normal:1.5;
  /* layout */
  --sidebar-w:250px; --topbar-h:64px; --content-max:1600px;
}
```

## The Sidebar Spec

`client/src/components/Sidebar.vue`:

- **Dimensions:** width `var(--sidebar-w)` (250px); `position: sticky; top: 0; height: 100vh`; flex
  column — logo block at top, nav list below.
- **Light styling:** `background: var(--color-surface)`; `border-right: 1px solid var(--color-border)`.
- **Default item:** `color: var(--color-text-muted)`; transparent bg; `border-radius: var(--radius-sm)`;
  `padding: var(--space-3) var(--space-4)`; icon↔label `gap: var(--space-3)`;
  `font-size: var(--text-base)`; `font-weight: var(--font-medium)`; `position: relative`.
- **Hover:** `background: var(--color-hover-bg)`; `color: var(--color-text)`.
- **Active:** `background: var(--color-primary-bg)`; `color: var(--color-primary-text)`;
  `font-weight: var(--font-semibold)`; + a 3px **left accent bar** via `::before`
  (absolute, `left: 0`, full height, `background: var(--color-primary)`).
- **Icons:** inline `<svg width="20" height="20" stroke="currentColor" fill="none">` so they inherit
  the link color and recolor on hover/active. No icon library.
- **Logo:** stacked — `t('nav.companyName')` (bold, `--text-lg`) above `t('nav.subtitle')`
  (muted, `--text-xs`). A vertical stack reads better in a narrow column than the old horizontal logo.
- **Nav items** as a data array, `v-for`'d with `:key="item.to"` (never index). Preserve the existing
  order and routes:

  | Order | Route | i18n label | Icon (line/feather-style inline SVG) |
  |---|---|---|---|
  | 1 | `/` | `nav.overview` | grid / dashboard squares |
  | 2 | `/inventory` | `nav.inventory` | box / package |
  | 3 | `/orders` | `nav.orders` | clipboard-list |
  | 4 | `/spending` | `nav.finance` | dollar / banknote |
  | 5 | `/demand` | `nav.demandForecast` | trending-up |
  | 6 | `/reports` | `nav.reports` **(NEW key — see Phase 4)** | bar-chart |

  For the root link use `:class="{ active: $route.path === '/' }"` (or `exact-active-class`) so `/` is
  not always-active. Other links can use `router-link-active`.

## The Topbar Spec

`client/src/components/TopBar.vue`:

- Holds `<FilterBar />`, `<LanguageSwitcher />`, and `<ProfileMenu />`.
- `position: sticky; top: 0; z-index` above content; `background: var(--color-surface)`;
  `border-bottom: 1px solid var(--color-border)`; height ~`var(--topbar-h)`; horizontal flex with
  filters on the left and language/profile on the right.
- Re-emits `show-profile-details` and `show-tasks` from the nested `ProfileMenu` up to `App.vue`.
- `FilterBar.vue` keeps its structure but its sticky `top` (currently hardcoded `70px` for the old
  header) must be re-derived for the new layout (see Risks).

## Procedure (execute in order)

### Phase 0 — Prep & servers
1. Run the `start` skill (backend :8001, frontend :3000). Confirm both respond.
2. With Playwright MCP, navigate to each route and capture a **baseline screenshot**:
   `/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`.
3. Re-read the current `App.vue`, `components/FilterBar.vue`, `main.js`, and the 6 views so the
   briefings to vue-expert are accurate.

### Phase 1 — Design tokens (1 vue-expert task)
4. Delegate: create `client/src/styles/tokens.css` (the `:root` block above) and add
   `import './styles/tokens.css'` to `client/src/main.js`. No visual change expected.
5. Verify with Playwright: app still loads, zero console errors.

### Phase 2 — Shell, Sidebar, Topbar (vue-expert)
6. Delegate creation of `Sidebar.vue` and `TopBar.vue`, plus the `App.vue` rewrite to the `.app-shell`
   grid: remove `.top-nav`/`.nav-tabs`, move `LanguageSwitcher`/`ProfileMenu`/`FilterBar` into TopBar,
   keep modals at root and pass the `show-profile-details`/`show-tasks` handlers down through TopBar,
   and convert App.vue's remaining hex values to tokens. Fix `FilterBar.vue`'s sticky `top`.
7. Add the `nav.reports` key to `en.js` and `ja.js` (can also be done in Phase 4, but doing it now lets
   the sidebar render correctly).
8. Verify with Playwright: sidebar renders, all 6 links navigate, active state + left accent bar shows,
   topbar holds filters + language + profile, both modals still open/close. Screenshot.

### Phase 3 — Per-view restyle (one vue-expert task per view, sequential)
9. Restyle in this order (smallest/lowest-risk first, Dashboard last): **Orders → Inventory → Demand →
   Reports → Spending → Dashboard.** For each view, delegate vue-expert to: replace hardcoded hex with
   tokens; align or remove local redefinitions of shared classes (`.card`, `.stat-card`, `.badge`,
   `.card-title`, `.card-header`, table styles) so they match the polished global look; apply the
   `--space-*` scale consistently; and restyle cards/tables/badges to the SaaS spec. After each view:
   Playwright navigate + screenshot + console-error check before moving on.
10. **Dashboard.vue (~1271 lines, many SVG charts) is incremental.** Split into sub-steps and verify
    after each: KPI/stat cards → card containers & section spacing → tables → badges → recolor chart
    strokes/fills only. Explicitly instruct vue-expert: **do not change chart `viewBox`, coordinates,
    scales, or data bindings** — only colors/spacing/container styling.

### Phase 4 — i18n & cleanup
11. Confirm `nav.reports` exists in both `en.js` and `ja.js`. Use Playwright + LanguageSwitcher to
    confirm all 6 nav labels translate.
12. **Skip the unrouted `Backlog.vue`** — it is not in `main.js` routes or the nav. Do not add it to the
    sidebar. (Optionally token-align it for consistency, but do not wire it into nav.)

## Delegating to vue-expert

For **every** Task call to vue-expert, include:

- (a) the exact file(s) to create/edit;
- (b) the specific token names to use (reference the token block above);
- (c) "use inline SVG only — no new npm dependencies";
- (d) "preserve all existing data bindings, props, events, `v-for` keys (no index keys),
  loading/error states, and SVG chart geometry (`viewBox`/coordinates/scales)";
- (e) "follow the patterns in `client/CLAUDE.md` and your own recipes";
- (f) "report back which files you changed."

The orchestrator NEVER edits `.vue` or `client/src/*.js` directly — all such edits go through
vue-expert (root `CLAUDE.md` mandatory rule).

## Verification

Use Playwright MCP against `http://localhost:3000`; manage servers with `start`/`stop`.

1. **Servers up:** `http://localhost:3000` and `http://localhost:8001/docs` respond.
2. **Per-route pass:** navigate to `/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`.
   For each: screenshot; assert the sidebar is present with the correct active item highlighted
   (left accent bar + blue); assert primary content rendered (not stuck on loading/error).
3. **Console errors:** capture console messages per route; assert **zero** errors (missing i18n key,
   undefined component, or router warnings count as failures).
4. **Interactions:** click each sidebar item → URL + active state update; open ProfileMenu → trigger
   "show profile details" and "show tasks" → both modals open and close; change a FilterBar select →
   data still updates (filters not broken by the move).
5. **Language switch:** toggle to `ja` → all 6 nav labels + content translate, including `nav.reports`.
6. **Responsive:** resize the viewport (e.g. 1280px and ~1024px) → the grid holds, content doesn't
   overflow horizontally (depends on `.app-main { min-width: 0 }`), and the sidebar stays fixed-width.
7. **Before/after:** compare Phase 0 baselines with the final screenshots to confirm the redesign
   applied to every view (no view left with old top-nav-era styling or stray hardcoded colors).
8. Optionally run `stop` when done.

## Risks & Edge Cases

- **Scoped styles defeat tokens (biggest risk).** ~92 hardcoded hex values live in the 6 views' scoped
  styles, and several views **redefine** shared classes (`.card`, `.stat-card`, `.badge`,
  `.card-title`, `.card-header`, tables — e.g. Reports.vue). Defining tokens globally will NOT recolor
  these — each view must be edited to consume `var(--token)`. Phase 3 is mandatory, not optional polish.
- **Unrouted `Backlog.vue`.** Exists (~152 lines) but is not routed or in nav. Skip it; don't add it to
  the sidebar or waste verification cycles on it.
- **Sticky positioning.** `FilterBar.vue` is `position: sticky; top: 70px` (the old header height).
  After moving into the topbar this is wrong — re-derive it (e.g. topbar sticky at `top: 0`, FilterBar
  below it, or FilterBar non-sticky inside a sticky topbar). Re-establish z-index stacking
  (sidebar / topbar / modals) so modals stay on top.
- **i18n nav-label gap.** `nav.reports` does not exist; App.vue hardcodes "Reports". Add `nav.reports`
  to **both** `en.js` and `ja.js`, or the `ja` UI breaks/falls back.
- **Don't break SVG charts.** Dashboard/Reports/Spending/Demand contain custom SVG charts. Change only
  colors (stroke/fill → tokens) and container spacing — never `viewBox`, coordinates, scales, or keys.
- **Grid overflow.** `.app-main` needs `min-width: 0` or wide Dashboard tables/charts blow out the
  layout and break the fixed sidebar width.
- **`max-width: 1600px` changes meaning.** The old `.main-content` centered within the full viewport;
  now content sits inside the `1fr` column right of the sidebar. Re-evaluate centering via
  `--content-max`.
- **Profile/Tasks event hop.** Moving `ProfileMenu` into TopBar adds an event hop
  (ProfileMenu → TopBar → App). If the re-emit is missed, the modals silently stop opening
  (verification step 4 catches this).
- **No new npm dependency** — inline SVG only.
- **`main.js` edits via vue-expert too** — keep the "all client/src changes via vue-expert" rule
  consistent.

## Done Criteria

- Sidebar replaces the top nav on all routes; active item highlighted with the left accent bar + blue.
- `tokens.css` imported and consumed — no raw hex left in App.vue's global styles or in the restyled
  view rules.
- All 6 routes render with **zero console errors**.
- Modals, filters, and language switching all work; `nav.reports` translates in both locales.
- Dashboard charts visually intact (geometry untouched, recolored only).
- Layout holds at 1280px and ~1024px with no horizontal overflow.
