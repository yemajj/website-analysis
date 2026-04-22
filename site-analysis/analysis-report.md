# Site Analysis Report — ruttyandmorris.com

**Subject:** Rutty HVAC & Refrigeration LLC  
**Date:** 2026-04-22  
**Scope:** Design, UX, accessibility, performance, SEO  
**Pages analyzed:** 57 (all pages in crawl snapshot)  
**Method:** Observation-only crawl; no authentication, no form submission, no exploitation

---

## 1. Information Architecture & Navigation

**Page inventory:**
- Core service pages: `/hvac-services`, `/mini-split-systems`, `/indoor-air-quality`, `/maintenance-program`, `/refrigeration-services`, `/refrigeration`, `/ac-heating-ventilation-services`
- Support pages: `/about`, `/contact`, `/blog`, `/service-areas`, `/sitemap`, `/thank-you`, `/privacy-policy`, `/terms-of-service`, `/cookies`
- City-specific pages: 30+ across 6 cities (Beaumont, Lumberton, Orange, Groves, Port Arthur, Nederland) × 5 service types (AC repair, AC service, HVAC contractor, commercial refrigeration, ice machine repair, heating-and-cooling)

**Main nav structure:**
- HVAC Services → AC/Heating Repair, Installation, Mini-Split Systems, Indoor Air Quality
- Maintenance Program → Residential / Commercial / Industrial
- Refrigeration → Comprehensive Refrigeration, Ice Machine, Commitment to Quality
- About Us → Gallery, FAQs
- Service Areas

**Issues:**
- `/refrigeration/` and `/ac-heating-ventilation-services/` are indexed (status 200) but not in the main nav — orphaned pages that split link equity.
- `/reliable-ac-repair-in-orange-for-efficient-cooling-and-comfort/` is a long auto-generated URL with no apparent nav or footer link — orphan.
- No breadcrumb navigation visible on any page; users cannot orient themselves in the site hierarchy.
- City pages are siloed — they do not link to each other or back to related service pages, limiting internal link flow.

---

## 2. Design System

**Color palette (from CSS):**

| Role | Value | Usage |
|------|-------|-------|
| Primary | `#2e96d1` | Buttons, links, hover states |
| Accent/CTA | `#e01d29` | Secondary CTA highlights |
| Dark bg (darkest) | `#0b1527` | Footer, hero overlays |
| Dark bg (mid) | `#141F33` / `#192740` | Section backgrounds |
| Body text | `#404856` | Paragraphs |
| Light bg | `#F0F6FE` | Alternating sections |
| Border/muted | `#DEE0E2` | Dividers |
| Highlight | `#FFCA63` | Accent callouts |
| White | `#FFFFFF` | Text on dark, card backgrounds |

**Typography:**
- 9 WOFF2 font files preloaded via Next.js static media (family names not exposed in CSS variable names)
- Font weights: 500 (buttons), 600 (headings)
- Heading scale:

| Tag | Desktop | Mobile |
|-----|---------|--------|
| H2 | 52px | 34px |
| H3 | 42px | 26px |
| H4 | 32px | 22px |
| H5 | 24px | 18px |
| H6 | 18px | 16px |

- Body: `.body_l` / `.body_s` classes, line-height 1.2–1.3

**Spacing:** Consistent increments — padding 24/32/48/54/64px; gap 6/10/12/24/30/68px; border-radius 4/8/16/20px.

**Components:**
- Buttons: 64px tall desktop, 56px mobile. Three variants: primary (`#2e96d1`), secondary, white. Hover darkens via `color-mix(in srgb, currentColor 10%, black)`.
- Hero: full-viewport-height banner with embedded contact form on dark overlay (padding 54px 48px, border-radius 20px).
- Nav dropdown: nested `<ul>` / `<li>` structure.

**Token consistency:** Mixed. CSS custom properties exist (`--primary_color`, `--white_color`, etc.) but some individual elements override inline with raw hex values. Bootstrap CSS is bundled and then partially overridden — unnecessary weight.

---

## 3. Content Quality

**Brand name inconsistency (critical):**
- Homepage `<title>`: "Rutty HVAC & Refrigeration LLC | Formerly Rutty and Morris LLC"
- City page titles: often omit brand name entirely (e.g., "AC Repair Beaumont" only)
- `<meta property="og:site_name">`: still "Rutty and Morris LLC" (old name) on most pages
- About page: correctly uses new name

**Thin / duplicated city pages:**
~70% of content on city pages is boilerplate. The footer paragraph — "Providing expert air conditioning, ventilation, and refrigeration services across Southeast Texas since 2003" — is identical across all 30+ city pages. Intro paragraphs swap city names but follow the same template structure. This is the largest single SEO risk on the site.

**Missing content:**
- No pricing or cost estimates on any page
- No team member profiles, photos, or individual credentials on About
- No explicit certifications listed (EPA 608, NATE, HVACR licensing numbers)
- No service guarantees or warranty information
- No testimonials visible in crawled server-side HTML (may be client-rendered)

**Tone:** Professional and accessible. Heading copy on city pages reads like blog posts, not service page copy ("Why DIY AC Repairs Can Be Risky" — appropriate for a blog, odd as a service area landing page).

---

## 4. UX & Usability

**Click depth to key actions:**
- Phone call: 0 clicks (header button `Call (409) 729-4822` always visible)
- Contact form: 1 click from homepage (scroll) or 1 nav click to `/contact`
- Quote request: merged into contact form — no dedicated quote flow

**Mobile responsiveness:**
- Viewport meta: `<meta name="viewport" content="width=device-width, initial-scale=1"/>` ✓
- CSS breakpoints: 1199px, 991px, 575px, 400px
- Images: Next.js srcset at 640w / 750w / 828w / 1080w / 1200w / 1920w / 2048w / 3840w ✓

**Contact form (on `/contact`):**
- Fields: Name, Email (type="email"), Phone (type="tel"), Message (textarea)
- Submits → `/thank-you` page
- No visible required-field indicators, inline validation, or loading state on submit
- No spam protection visible in server-rendered HTML (hCaptcha integration exists but exposes the server secret — see `security-findings.txt`)

**Navigation clarity:**
- Service grouping in nav is clear
- However, "AC Service" vs "AC Repair" pages are indistinguishable in intent — both exist per city, both target the same user need

**Confusing patterns:**
- Long editorial-style H1s on city pages ("The Benefits of a Programmable Thermostat | Heating and Cooling Lumberton") read as blog posts, not service pages
- Footer links and main nav links partially overlap but don't fully align

---

## 5. Accessibility

**Image alt text:**
- Logo: `alt="RUTTY_NEW_LOGO"` — passes, slightly machine-y
- Gallery images: `alt="Gallery Section Image 1"` etc. — present but generic; not descriptive for screen readers
- Hero images: Next.js Image component; alt attributes present in sampled pages
- No `alt=""` decorative images found in sampled pages ✓

**Heading hierarchy:** H1 appears once per page; H1 → H2 → H3 → H4 order is respected in sampled pages ✓

**Interactive elements:** Proper `<button>` and `<a href>` elements used — no `<div onClick>` pattern observed ✓

**Color contrast:**
- Primary button `#2e96d1` on white: passes WCAG AA ✓
- Body text `#404856` on white: passes WCAG AA ✓
- No obvious contrast failures from CSS values

**ARIA:** 56 aria-/role/tabindex instances identified across the site; mobile nav toggle uses role/aria attributes. Coverage is reasonable but not comprehensive (no `aria-label` on icon-only links spotted in sampling).

---

## 6. Performance

**JavaScript:**
- 17 Next.js chunks, ~800 KB total uncompressed
- Two large chunks: `315-8e243165532a3251.js` (~166 KB), `559-990fc2169d096384.js` (~352 KB)
- All scripts load with `async=""` ✓
- No evidence of route-level code splitting for city pages

**CSS:**
- 4 stylesheets: `ba0e13ae2b49b4be.css`, `42ad67716ae75d64.css`, `969563ea15b6f69b.css`, `de5fed9b6164026f.css`
- All loaded as `<link rel="stylesheet">` (render-blocking)
- Bootstrap bundled alongside custom CSS — adds ~30 KB of unused rules

**Images:**
- 127 images served as JPEG/PNG — no WebP or AVIF detected in crawled assets
- `loading="lazy"` on Next.js images ✓
- 9 WOFF2 font files preloaded ✓

**Total assets:** 213 (9 fonts, 4 CSS, 17 JS, 127 images, misc)

---

## 7. SEO

**Title tags:**
- Homepage: "Rutty HVAC & Refrigeration LLC | Formerly Rutty and Morris LLC" (58 chars) ✓
- Service pages: "[Service] | Rutty HVAC & Refrigeration LLC | Nederland, TX" ✓
- City pages: "[Blog-style title] | [Service] [City]" — keyword present but editorial framing is unusual for a landing page

**Meta descriptions:** Present on all sampled pages, 90–150 chars ✓

**Canonical tags:** Implemented on all pages ✓

**Structured data:**
- JSON-LD present: `WebPage`, `BreadcrumbList`, `WebSite` with `SearchAction`
- **Missing:** `LocalBusiness` / `Organization` with address, phone, hours, geo coordinates, and `AggregateRating` — the most impactful schema for a local service business

**Internal linking:**
- Nav provides 6 primary + 7 footer links per page
- City pages have minimal contextual links to related services or other cities
- Overall internal link density: low (~10–15 per page)

**Cannibalization risk:**
- `/ac-repair-[city]` and `/ac-service-[city]` target overlapping keywords for every city
- All 30+ city pages target "HVAC [city]" / "AC repair [city]" clusters with near-identical content
- Without clear content differentiation, Google may collapse rankings or choose a single low-quality representative

---

## 8. Top 10 Issues (Prioritized)

### Critical

**1. Thin/duplicate city pages**
- 30+ city pages share ~70% boilerplate content. Identical footer paragraphs, templated body, city name swapped in. High risk of Google ranking penalties and indexation demotion.
- Fix: Consolidate to 6 genuine city landing pages with location-specific content (local testimonials, neighborhood references, area photos). Redirect thin duplicates.

**2. Brand name inconsistency across SEO properties**
- `og:site_name` still says "Rutty and Morris LLC" (old name); title tags mix old and new names; some city page titles omit brand name entirely.
- Fix: Audit and standardize every `<title>`, `<meta name="description">`, `og:site_name`, and JSON-LD `name` field to "Rutty HVAC & Refrigeration LLC".

**3. AC Repair vs AC Service keyword cannibalization**
- Both `/ac-repair-[city]` and `/ac-service-[city]` pages exist for all 6 cities with overlapping keyword intent. They split ranking authority.
- Fix: Pick one primary URL per city/service. 301-redirect the other. If both pages must exist, give them clearly differentiated content (emergency repair vs. scheduled maintenance).

### Major

**4. No LocalBusiness schema markup**
- Schema only includes `WebPage` and `BreadcrumbList`. No address, phone, hours, or ratings in structured data.
- Fix: Add `LocalBusiness` JSON-LD with full NAP (Name/Address/Phone), service area, business hours, and geo coordinates to every page via a shared layout component.

**5. Missing pricing and service scope information**
- No pricing, service tiers, or estimate information on any page. Increases lead friction and reduces self-qualification.
- Fix: At minimum, add "Free Estimates Available" with a prominent CTA. Optionally add a pricing or service tier page.

**6. Large unoptimized JS bundles**
- `559-990fc2169d096384.js` is 352 KB; `315-8e243165532a3251.js` is 166 KB. No visible route-level splitting for city pages. Total ~800 KB JS.
- Fix: Run `webpack-bundle-analyzer` on the Next.js build. Split chunks by route. Lazy-load non-critical UI (testimonials, map embeds, form libraries). Target <250 KB total.

**7. No WebP/AVIF image delivery**
- All 127 images are JPEG/PNG. Next.js Image optimization is configured but WebP/AVIF generation should be verified end-to-end.
- Fix: Confirm `next.config.js` includes `formats: ['image/avif', 'image/webp']`. Audit actual response headers to confirm format negotiation is working.

### Moderate

**8. No team credentials or certifications on About page**
- Mentions "factory-trained technicians" and "background checks" but has no staff profiles, certification badges (EPA 608, NATE, HVACR), or license numbers.
- Fix: Add a team section with 3–5 technician profiles (photo, name, certifications). Add a credentials section with EPA/NATE badge images.

**9. Orphaned pages not in navigation**
- `/refrigeration/`, `/ac-heating-ventilation-services/`, and `/reliable-ac-repair-in-orange-for-efficient-cooling-and-comfort/` are indexed but unlinked.
- Fix: 301-redirect each to the canonical equivalent (`/refrigeration-services`, `/hvac-services`, `/ac-repair-orange`). Remove from robots/sitemap if not redirecting.

**10. Contact form lacks validation and spam protection**
- No visible required-field indicators, inline validation errors, or submit loading state. hCaptcha integration is broken (secret key exposed in page source — see `security-findings.txt`).
- Fix: Add HTML5 `required` + `pattern` attributes, visible error states, button loading state. Rotate hCaptcha secret key immediately; move to server-side environment variable.

---

## Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Information architecture | 6/10 | Logical structure, orphan pages, no breadcrumbs |
| Design consistency | 6/10 | Token system exists, Bootstrap bloat, ad-hoc overrides |
| Content quality | 4/10 | Thin city pages, brand inconsistency, missing trust signals |
| UX / usability | 7/10 | Phone CTA excellent, form gaps, redundant page types |
| Accessibility | 7/10 | Semantic HTML, decent alt text, minor ARIA gaps |
| Performance | 5/10 | Next.js helps, large JS bundles, no WebP confirmed |
| SEO | 5/10 | Good structure, cannibalization risk, missing local schema |
| Trust signals | 4/10 | No team bios, no certs, no visible testimonials, broken captcha |

**Overall:** The site has a solid technical foundation (Next.js, responsive, canonical tags, meta descriptions) but is being held back by a content strategy that mass-produces near-duplicate city pages and has not been updated to reflect the company's rebrand. The two highest-leverage fixes before any visual redesign are: (1) consolidate city pages and (2) add LocalBusiness schema.
