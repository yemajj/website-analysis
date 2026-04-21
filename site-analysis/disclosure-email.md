# Responsible-disclosure email — hCaptcha secret key leaked in page HTML

Send to a contact on ruttyandmorris.com (footer email, contact form, or
whichever point of contact is most likely to reach a technical decision-maker).
Fill in the bracketed items before sending.

---

**Subject:** Security issue on ruttyandmorris.com — hCaptcha server secret
exposed in page source

Hi [Name / Rutty & Morris team],

I'm reaching out in good faith to flag a security issue I noticed on your
website while doing a public-facing design review.

**What I found**

The server-side secret key for your hCaptcha integration is embedded in the
HTML source of at least two pages on ruttyandmorris.com. This key is the
credential that should stay on your backend and that you use to call
hCaptcha's `/siteverify` endpoint — it should never be sent to browsers.

Affected pages (publicly viewable — just use "View Page Source" in any
browser to confirm):

- `https://www.ruttyandmorris.com/heating-and-cooling-beaumont/` — around line 90
- `https://www.ruttyandmorris.com/heating-and-cooling-lumberton/` — around line 90

I am **not** including the key itself in this email. You can locate it in the
page source yourself; I'd rather you see it than me circulate it further.

**Why it matters**

With the server secret, anyone can call hCaptcha's `siteverify` API as if they
were your site — which lets them forge successful captcha results against your
own forms, potentially bypassing the protection you added to your contact /
request-service flows. It can also be used to rack up usage against your
hCaptcha account.

**What I recommend**

1. Rotate the secret in the hCaptcha dashboard
   (https://dashboard.hcaptcha.com/sites). That invalidates the exposed value
   immediately.
2. Move the secret to server-side configuration (environment variable,
   secret manager, etc.) — only the *site key* (different value, safe to
   expose) should ever appear in client HTML.
3. Audit whoever maintains the site for similar mistakes (Stripe, Mailchimp,
   SMTP creds, etc.); the same template or plugin that injected the hCaptcha
   secret may have leaked others.

**Scope of my work**

I discovered this while running a polite crawl (rate-limited, respecting
robots.txt) of your public pages for a design review. I did not attempt to
use the key, access any restricted area, or test your systems in any way.
No copy of the raw key has been published; any working notes I've kept
replace it with a redacted placeholder.

Happy to answer questions or help you verify the fix once you've rotated.
If you already have a security contact or a preferred disclosure channel,
please let me know and I'll route this there.

Best,
[Your name]
[Optional: contact details — reply-to email is fine]

---

## Send checklist

- [ ] Replace `[Name / Rutty & Morris team]` and `[Your name]` placeholders.
- [ ] Confirm the two URLs still contain the secret before sending
      (so the email is accurate on arrival).
- [ ] Send from an email you monitor — they may reply with questions.
- [ ] Save a copy (dated) in case you need a disclosure timeline later.
- [ ] Give them a reasonable window to fix before publishing any report that
      names specific URLs (30–90 days is common; the severity and ease of
      exploitation here argues for the shorter end — e.g., 30 days or
      "as soon as you've rotated").
