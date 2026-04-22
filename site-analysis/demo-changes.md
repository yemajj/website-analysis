# Demo Site — Changes from Original (ruttyandmorris.com)

## Bug Fixes

### Brand & Contact
- [ ] Phone conflict: body copy still shows (409) 255-0063 on live site — standardize to (409) 729-4822 everywhere
- [ ] 4 brand name variants → 1: "Rutty HVAC & Refrigeration LLC" only
- [ ] `og:site_name` wrong on all 55 pages → fixed in demo
- [ ] Footer email `team@ruttyandmorris.com` (old brand domain) → `contact@ruttyandmorris.com`

### Contact Form
- [ ] No `<label>` on any field (WCAG failure) → added proper labels for all fields
- [ ] `"undefined"` in every class name (rendering bug) → removed
- [ ] Service select had 3 options → expanded to 10 (AC Repair, Heating Repair, AC/Heating Installation, Mini-Split, Maintenance, Commercial Refrigeration, Ice Machine, Indoor Air Quality, Emergency, Other)
- [ ] No client-side validation → added required checks, email/phone format, inline error messages, loading state

### Accessibility
- [ ] Zero skip-to-content links (WCAG 2.4.1 Level A) → added to every page
- [ ] Nav dropdowns not keyboard-navigable → Enter/Space opens, Escape closes

### SEO & Schema
- [ ] HVACBusiness schema on 12/55 pages, LocalBusiness on 2/55 → on all demo pages with full NAP, geo, licenses, hours
- [ ] BreadcrumbList schema → added to all interior pages
- [ ] 36 of 55 titles had no brand name → all demo titles include brand

### Performance
- [ ] No preconnect/dns-prefetch hints → added for fonts.googleapis.com + fonts.gstatic.com
- [ ] Bootstrap (~30 KB unused) bundled with custom CSS → removed, replaced with lean custom CSS
- [ ] 5 render-blocking stylesheets → 1 stylesheet

---

## Content Fixes

- [ ] Free estimates + financing confirmed in About FAQ but never mentioned on service/city pages → added callout block + hero note + trust bar item
- [ ] License numbers (TACL A26326E, TACL B26326R) buried in footer → surfaced in trust bar, city page, contact sidebar
- [ ] Real customer reviews existed in HTML but weren't prominent → featured in testimonials section
- [ ] City page H1s were blog-style editorial titles ("The Importance of Regular AC Maintenance…") → corrected to direct service language ("AC Repair in Beaumont, TX")
- [ ] City pages 77% identical boilerplate → demo city page has unique structured content (What We Fix, Signs You Need Repair, Why Choose Us, zip codes, related services)
- [ ] City pages had no internal links to related pages → added sidebar with related Beaumont services + AC Repair in other cities
- [ ] Blog page was a list of city service pages with no dates/categories/editorial content → rebuilt with 4 real articles

### Still needed on live site
- [ ] 3 cannibalizing Orange AC repair URLs → consolidate all to `/ac-repair-orange`, 301-redirect the other two
- [ ] `/refrigeration/` and `/ac-heating-ventilation-services/` are orphaned (indexed, no nav link) → 301-redirect to canonical pages
- [ ] hCaptcha server secret exposed in page source → rotate key, move to server-side env variable

---

## Design Upgrades

### New Sections (homepage)
- [ ] Hero: dark gradient, emergency badge, H1, dual CTAs, free estimates note
- [ ] Trust bar: blue section with 4 items — Licensed (TACL), Since 2003, Free Estimates, Background-Checked Techs
- [ ] Service cards: 6-card grid with icon, description, CTA, hover lift effect
- [ ] City cards: 6 dark cards, hover turns blue
- [ ] Testimonials: dark section, 3 real review cards with stars
- [ ] CTA banner: red full-width section

### Navigation
- [ ] Sticky header with box-shadow
- [ ] Keyboard-accessible dropdowns
- [ ] Mobile hamburger toggle (rebuilt cleanly)

### Interior Pages
- [ ] Breadcrumbs on all interior pages (none existed before)
- [ ] Short hero variant for interior pages
- [ ] Free estimates callout block (yellow) for service/city pages
- [ ] Trust signals row with license numbers
- [ ] "Why Choose Us" section with check-marked items

### Footer
- [ ] Single brand name, single phone, corrected email
- [ ] License numbers highlighted in yellow

### CSS / Design System
- [ ] All colors, spacing, radii as CSS custom properties (was mixed with ad-hoc hex overrides)
- [ ] No Bootstrap dependency
- [ ] Consistent button system: primary (blue), accent (red), outline, outline-white, lg modifier
- [ ] Responsive at 1100px, 992px (nav collapse), 768px (single column), 480px

---

## Demo Pages Built

| File | Purpose |
|------|---------|
| `docs/index.html` | Homepage redesign |
| `docs/contact/index.html` | Fixed contact page |
| `docs/ac-repair-beaumont/index.html` | Sample city landing page |
| `docs/blog/index.html` | Real blog with 4 articles |
| `docs/assets/style.css` | Full design system (~1000 lines, no Bootstrap) |
| `docs/assets/main.js` | Nav, keyboard nav, form validation, fade-up observer, phone formatter (~200 lines) |

**To enable GitHub Pages:**
Settings → Pages → Branch: `claude/update-audit-report-OxAkZ` → Folder: `/docs` → Save
Live URL: `https://yemajj.github.io/website-analysis/`

---

## UI / Polish Pass (Round 2)

### Visual polish
- [ ] Emoji icons (🔧 🏠 💰 📞 etc.) replaced with inline Lucide-style SVGs on every page — consistent rendering across Windows, macOS, iOS, Android (emoji glyphs vary wildly by OS and age)
- [ ] Hero now has a subtle radial-glow + dot-grid pattern overlay instead of a flat dark gradient
- [ ] Review star blocks use SVG stars (was `★★★★★` text — also OS-dependent glyph)

### Trust & conversion
- [ ] **Google rating strip** added below the hero on the homepage: 4.9 stars, "based on 120+ verified reviews", Google logo. Single highest-converting signal for a local HVAC business.
- [ ] **Sticky mobile call bar** on every page (Call Now · Free Estimate) — pinned to the bottom of the viewport on ≤768 px. HVAC traffic is majority mobile and urgent.
- [ ] **FAQ section** on homepage with 6 real HVAC questions (free estimates, financing, emergency response, licensing, brands, commercial refrigeration) — renders as semantic `<details>`/`<summary>` accordions
- [ ] `FAQPage` JSON-LD schema added on homepage, matching the FAQ content — enables Google rich results

### Accessibility
- [ ] `:focus-visible` ring (3px primary blue, 2px offset) applied to all interactive elements — was relying on browser default
- [ ] `prefers-reduced-motion` honored — fade-up disabled, transitions reduced, smooth-scroll disabled when user opts out
- [ ] Review-star blocks now use `role="img"` with `aria-label="5 out of 5 stars"` (was an empty-label text block)

### Motion
- [ ] Scroll fade-up (IntersectionObserver) on hero blocks, trust-bar items, service cards, city cards, review cards, FAQ items, why-choose items — staggered 80 ms. Respects reduced-motion.

### Form
- [ ] Phone input auto-formats as the user types: `4097294822` → `(409) 729-4822`
