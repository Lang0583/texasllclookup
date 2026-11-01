# Texas LLC Lookup (texasllclookup.com)

Static directory of Texas entities built from the Texas Comptroller "Active Franchise Tax Permit Holders" open dataset (data.texas.gov `9cir-efmm`). Not a government agency.

Stack: Namecheap (domain/DNS) · GitHub Pages (hosting, built by GitHub Actions) · GoHighLevel (opt-in forms/CRM via inbound webhook) · n8n (automation).

- `generator/normalize_api.py` – merges Socrata API CSV pages into the portal export format.
- `generator/build.py <csv> <outdir>` – builds the site (city hubs, county hubs, guides indexable; business pages noindex), sitemap.xml, robots.txt, llms.txt, CNAME.
- `.github/workflows/build-deploy.yml` – downloads data, builds, deploys to Pages on push and weekly. Raw data is never committed.

Signup: GoHighLevel embedded form (GHL_FORM in build.py).
