# Site Analysis Report — ruttyandmorris.com

**Subject:** Rutty HVAC & Refrigeration LLC  
**Date:** 2026-04-22  
**Scope:** Design, UX, accessibility, performance, SEO  
**Pages analyzed:** 55 (all pages in crawl snapshot)  
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
- Three separate URLs target "Orange AC repair" and directly cannibalize each other: `/ac-repair-orange`, `/ac-repair-in-orange`, and `/reliable-ac-repair-in-orange-for-efficient-cooling-and-comfort/`. The last is a long auto-generated URL with no nav or footer link.
- No breadcrumb navigation visible on any page; users cannot orient themselves in the site hierarchy.
- City pages are siloed — they do not link to each other or back to related service pages, limiting internal link flow.
- `/blog` contains no blog posts. It is a list of city service pages styled to look like blog post cards (same template, city names as post titles). There is no editorial content. The page is essentially empty from an SSR content perspective.

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

**Phone number conflict (critical):**
- The header CTA button on every page shows **(409) 729-4822**.
- Body copy and section CTAs on many pages show **(409) 255-0063**.
- Every visitor sees two different phone numbers. One is likely wrong or unmonitored. This erodes trust and guarantees some calls go unanswered.

**Brand name inconsistency (critical):**
- At least **four distinct name variants** appear across page titles: "Rutty HVAC & Refrigeration LLC", "Rutty and Morris LLC", "Rutty & Morris Air Conditioning", and "Rutty & Morris LLC".
- Homepage `<title>`: "Rutty HVAC & Refrigeration LLC | Formerly Rutty and Morris LLC"
- **36 of 55 pages** have no brand name in the `<title>` at all (e.g., "AC Repair Beaumont" only).
- `<meta property="og:site_name">`: still "Rutty and Morris LLC" (old name) on **all 55 pages** — not just most.
- Footer contact email is **team@ruttyandmorris.com** — an old-brand domain, inconsistent with the rebranded company name.
- About page: correctly uses new name in body copy.

**Thin / duplicated city pages:**
Text similarity analysis confirms **77% similarity** between same-service city pages. The footer paragraph — "Providing expert air conditioning, ventilation, and refrigeration services across Southeast Texas since 2003" — is identical across all 30+ city pages. Intro paragraphs swap city names but follow the same template structure. This is the largest single SEO risk on the site.

**Missing content:**
- No pricing or cost estimates on any page
- No team member profiles, photos, or individual credentials on About
- HVACR license numbers **are** present — buried in the footer (TACL A26326E, TACL B26326R) — but not surfaced on service or About pages where they build trust
- The About page FAQ states that **free estimates and financing are available**, but neither is advertised on any service page or city landing page — a significant conversion opportunity being missed
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
- Fields: Name, Email (type="email"), Phone (type="tel"), Service (select — lists only 3 options), Message (textarea)
- Submits → `/thank-you` page
- **Accessibility failure:** All fields use placeholder text only — no `<label>` elements present. Screen readers and autofill cannot identify fields.
- **Rendering bug:** Literal `"undefined"` appears in element class names, indicating a template variable that failed to resolve.
- **Honeypot field** present in form HTML (hidden spam-trap input) — this is a deliberate anti-spam technique and is fine, but was unaccounted for in previous analysis.
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

**Skip links:** Zero skip-to-content links exist anywhere on the site. Keyboard and screen-reader users must tab through the entire nav on every page before reaching main content — a WCAG 2.4.1 (Level A) failure.

**Image alt text:**
- Logo: `alt="RUTTY_NEW_LOGO"` — passes, slightly machine-y
- Gallery images: `alt="Gallery Section Image 1"` etc. — present but generic; not descriptive for screen readers
- Hero images: Next.js Image component; alt attributes present in sampled pages
- No `alt=""` decorative images found in sampled pages ✓

**Heading hierarchy:** H1 appears once per page; H1 → H2 → H3 → H4 order is respected in sampled pages ✓

**Forms:** Contact form uses placeholder text as the sole field label — no `<label>` elements. This fails WCAG 1.3.1 (Info and Relationships) and 3.3.2 (Labels or Instructions).

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
- 5 stylesheets: `ba0e13ae2b49b4be.css`, `42ad67716ae75d64.css`, `969563ea15b6f69b.css`, `de5fed9b6164026f.css`, `fe5ed1f4af4d2619.css`
- All loaded as `<link rel="stylesheet">` (render-blocking)
- Bootstrap bundled alongside custom CSS — adds ~30 KB of unused rules

**Images:**
- 127 images served as JPEG/PNG — no WebP or AVIF detected in crawled assets
- `loading="lazy"` on Next.js images ✓
- 9 WOFF2 font files preloaded ✓

**Resource hints:** No `<link rel="preconnect">` or `<link rel="dns-prefetch">` hints present. Third-party origins (Google Fonts, analytics, hCaptcha) are connected cold on every page load, adding latency.

**Service worker:** None. No offline capability, no cache-first strategy for returning visitors.

**Total assets:** 213 (9 fonts, 5 CSS, 17 JS, 127 images, misc)

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
- `HVACBusiness` schema exists on **12 pages**; `LocalBusiness` schema exists on **2 pages** — not entirely absent as previously noted, but inconsistently deployed
- Schema is missing from 43 of 55 pages; where present, it lacks address, phone, hours, geo coordinates, and `AggregateRating` — all critical for local pack eligibility

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
- 30+ city pages share ~77% boilerplate content (text-similarity confirmed). Identical footer paragraphs, templated body, city name swapped in. High risk of Google ranking penalties and indexation demotion.
- Fix: Consolidate to 6 genuine city landing pages with location-specific content (local testimonials, neighborhood references, area photos). Redirect thin duplicates.

**2. Brand name inconsistency + phone conflict across all pages**
- Four distinct brand name variants appear in page titles: "Rutty HVAC & Refrigeration LLC", "Rutty and Morris LLC", "Rutty & Morris Air Conditioning", "Rutty & Morris LLC". `og:site_name` is the old brand on all 55 pages. 36 of 55 titles contain no brand name at all. The footer contact email (team@ruttyandmorris.com) is also on the old-brand domain.
- Additionally, two different phone numbers appear on every page: (409) 729-4822 in the header, (409) 255-0063 in body copy. This inconsistency directly costs calls and undermines local SEO NAP consistency.
- Fix: Standardize every `<title>`, `og:site_name`, JSON-LD `name`, footer email, and phone number to a single canonical brand and contact point.

**3. Keyword cannibalization — especially severe for Orange**
- Both `/ac-repair-[city]` and `/ac-service-[city]` pages exist for all 6 cities. For Orange specifically, there are **three** competing URLs: `/ac-repair-orange`, `/ac-repair-in-orange`, and `/reliable-ac-repair-in-orange-for-efficient-cooling-and-comfort/`. All target the same search intent and split ranking authority three ways.
- Fix: Pick one canonical URL per city/service. 301-redirect all variants. For Orange, consolidate all three into `/ac-repair-orange`. If repair vs. service must be distinguished, differentiate content explicitly (emergency repair vs. scheduled maintenance).

### Major

**4. Incomplete and inconsistent structured data**
- `HVACBusiness` schema exists on 12 pages; `LocalBusiness` on 2 pages; the remaining 43 pages have no local business schema at all. Where schema is present, it lacks NAP (Name/Address/Phone), business hours, geo coordinates, and `AggregateRating`.
- Fix: Deploy `HVACBusiness` (subtype of `LocalBusiness`) via a shared layout component so it appears on all 55 pages. Populate with full NAP, service area, hours, geo coordinates. Add `AggregateRating` once review data is available.

**5. Free estimates and financing not advertised on service pages**
- The About page FAQ confirms that free estimates and financing are available — but neither is mentioned on any service page or city landing page. Visitors making a purchase decision never see this information where it matters.
- Fix: Add a "Free Estimates + Financing Available" callout block to every service and city page, linking to the About FAQ for details. This is a no-code content change with immediate conversion impact.

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

**9. Blog page contains no blog content**
- `/blog` renders as a list of city service pages styled as blog post cards. There are no articles, no editorial content, no dates — it is a mislabeled page index. A blog link in the nav that leads to non-blog content confuses users and wastes a crawl slot.
- Fix: Either populate the blog with genuine articles (highest SEO value) or remove the blog link from the nav and redirect `/blog` to `/service-areas` or the homepage.

**10. Contact form: accessibility failures and rendering bug**
- Form inputs use placeholder text only — no `<label>` elements. This fails WCAG 1.3.1 and 3.3.2 and breaks screen readers and browser autofill.
- Literal `"undefined"` appears in element class names, indicating an unresolved template variable — a visible rendering bug.
- The service `<select>` lists only 3 options, which likely does not cover all offered services.
- hCaptcha integration is broken (secret key exposed in page source — see `security-findings.txt`).
- Note: a honeypot anti-spam field is present and working as intended.
- Fix: Add `<label>` elements for every input, fix the undefined class name bug, expand the service dropdown, rotate hCaptcha secret key immediately and move to a server-side environment variable.

---

## Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Information architecture | 5/10 | Orphan pages, 3 cannibalizing Orange URLs, fake blog page, no breadcrumbs |
| Design consistency | 6/10 | Token system exists, Bootstrap bloat, ad-hoc overrides |
| Content quality | 3/10 | 77% duplicate city pages, 4 brand variants, dual phone numbers, free estimates/financing buried |
| UX / usability | 6/10 | Header phone CTA good; form rendering bug, undefined class names, select limited to 3 services |
| Accessibility | 5/10 | Zero skip links, no form labels (both WCAG A failures), otherwise decent semantic HTML |
| Performance | 5/10 | Next.js helps, large JS bundles, no WebP confirmed, no preconnect hints, no service worker |
| SEO | 5/10 | Schema partial (12/55 pages), severe Orange cannibalization, og:site_name wrong on all 55 pages |
| Trust signals | 5/10 | Licenses in footer (good), no team bios/certs on About, broken captcha, financing not surfaced |

**Overall:** The site has a solid technical foundation (Next.js, responsive, canonical tags, meta descriptions) but is undermined by a rebrand that was applied inconsistently — four brand name variants still exist, two phone numbers appear on every page, and the old brand's email domain is in the footer. Content strategy mass-produces near-duplicate city pages (77% similarity confirmed) and a blog page that contains no blog posts. The three highest-leverage fixes are: (1) resolve the phone number and brand name conflicts site-wide, (2) consolidate city pages with genuine local content, and (3) deploy complete HVACBusiness schema to all pages.
