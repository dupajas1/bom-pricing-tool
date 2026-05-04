# BOM Pricing Review Tool

> A browser-based BOM pricing tool that searches electronics distributors (via direct APIs or web scraping + local LLM) for component pricing, stock, and availability, and exports an enriched spreadsheet with per-line cost analysis.

A browser-based tool that takes an electronic Bill of Materials (BOM), searches distributor websites for pricing and availability, and outputs an enriched spreadsheet with pricing data.

Runs entirely in the browser — no server backend required. Supports direct distributor APIs (Mouser, DigiKey, Octopart/Nexar) that require no LLM or CORS extension, as well as LLM-based web scraping via LM Studio or OpenRouter.

## Files

| File | Description |
|------|-------------|
| `bom-pricing-tool.html` | Main application — BOM batch processor |

## Search Methods

**Mouser API** — Direct REST API call. Returns structured JSON — no LLM or CORS needed. Supports USD, CAD, EUR, GBP. Free API key from [mouser.com/api-hub](https://www.mouser.com/api-hub/).

**DigiKey API** — OAuth 2.0 client credentials flow. Returns structured JSON — no LLM or CORS needed. Supports US, Canada, Europe, and UK pricing. Free credentials from [developer.digikey.com](https://developer.digikey.com/).

**Octopart (Nexar) API** — GraphQL API aggregating pricing across multiple distributors. No LLM or CORS needed. Returns best available offer per part with pricing, stock, datasheet URL, and lifecycle status. Free credentials from [nexar.com/api](https://nexar.com/api).

**Web Search (fetch + LLM)** — Fetches distributor search pages, LLM finds product URLs, fetches each product page, LLM verifies MPN and extracts pricing. Supports Future Electronics or custom URLs. Requires Allow CORS extension and LM Studio.

**DuckDuckGo Agent** — Searches DuckDuckGo for the part, scores and filters up to 15 product page candidates, LLM visits each via tool-calling and extracts pricing. Requires a model with function-calling support (Qwen 2.5+, Llama 3.1+). Because pages are fetched by LM Studio (not the browser), bot-protected sites like DigiKey and Mouser are often accessible.

## Prerequisites

### API methods (Mouser, DigiKey, Octopart) — no LLM or CORS needed
- API credentials for the chosen service (see links above)

### Web Search and DuckDuckGo Agent
- **Chrome** with [Allow CORS](https://chromewebstore.google.com/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf) extension enabled
  - CORS settings: set Origin mode to ORIGIN (option 5)
- **LM Studio** at `127.0.0.1:1234` (configurable) with a model loaded (8B+ recommended, e.g. Qwen 2.5-9B)
  - Developer tab → Server settings → Enable CORS
  - For DuckDuckGo: model must support tool/function calling; enable the [visit-website tool](https://lmstudio.ai/docs/features/tool-use) in LM Studio
- Visit the distributor site once before searching (establishes cookies — Web Search method only)
- Alternatively, use **OpenRouter** as the LLM provider (no local LM Studio required)

## How It Works

1. **Upload BOM** — drag/drop Excel (.xlsx) or CSV file; the results table appears immediately showing all rows before processing starts
2. **Map columns** — Manufacturer, Part Number, Quantity, Description. Auto-detected from headers; LLM-assisted fallback. Changing a column dropdown updates the table preview instantly.
3. **Configure** — select search method, set build quantity, enter API credentials if needed
4. **Process** — searches each row, displays live results. Re-running only re-processes failed/unprocessed rows (green rows are skipped).
5. **Reset row** — click any row's `#` number to clear its result and force a re-scan on the next run
6. **Save Datasheets** — bulk-download all datasheet PDFs named `Manufacturer_PartNumber (Description).pdf`. In Chrome, saves files directly to a chosen folder (File System Access API). In Firefox/Safari, downloads a ZIP file instead. Any entries that fail to download (CORS, network error, or missing URL) are listed in a `_failed_links_TIMESTAMP.html` report with clickable URLs for manual download.
7. **Export** — downloads enriched Excel file with original data plus pricing columns

## Output Columns

| Column | Description |
|--------|-------------|
| Price Each | Unit price at the applicable quantity tier |
| Currency | USD, CAD, EUR, etc. |
| Price Extended | Price Each × line quantity |
| Min Buy Qty | Distributor's minimum order quantity |
| Stock Qty | Available stock (number, "In Stock", or "—") |
| Part Status | Active, Obsolete, NRND, EOL, etc. |
| Lead Time | Manufacturing lead time (in weeks) |
| Price Link | URL to the product page |
| Datasheet Link | URL to datasheet PDF |
| Part Description | Description from the distributor |
| Comments | Source, manufacturer mismatches, min qty adjustments, errors |

## Pricing Logic

- **Build qty × line qty** determines which price tier is used
- **Price Extended = Price Each × line qty** (not × build qty)
- Example: qty 1, build qty 1000 → uses the 1000-unit price tier, extended = price × 1

### Fractional Quantities (min buy qty > 1)

When a quantity contains a decimal point (e.g. `1.0`, `0.001`), it indicates the portion of a minimum-buy package used per unit. The tool:

- Calculates total components needed: qty × min_buy × build_qty
- Determines boxes needed: ceil(total / min_buy)
- Spreads total cost across all units
- Adds a comment showing box count and total min qty cost

Detection: Excel cells formatted with decimal places (e.g. format `0.00` showing `1.00`) are treated as fractional. Integer values (`1`) are treated as actual component counts.

### Prioritization

Results are prioritized by: stock availability (numeric > vague "in stock") → distributor min qty fits the need → lowest extended price → shortest lead time.

## Column ID Prefix

When running the tool multiple times with different sources, use the Column ID prefix (1–10) to namespace the output columns. For example, prefix `1` produces "1 - Price Each", "1 - Currency", etc. — allowing side-by-side comparison in the exported spreadsheet.

## HTML Cleaning Pipeline

The tool includes an HTML cleaning pipeline optimized for electronics distributor pages:

- Extracts `<main>` content or strips nav/header/footer
- Removes scripts, styles, SVGs, forms, inputs
- Strips bulk attributes (data-*, style, class, aria-*)
- Preserves button content (sort headers like "Stock", "1", "10")
- Converts HTML tables to pipe-delimited text (preserves column alignment for empty cells)
- Preserves PDF/datasheet URLs before stripping tags
- Strips long tracking URLs (>150 chars) except PDF/datasheet links
- Cuts at junk sections ("You May Also Like", "Related Products", etc.)

## Known Limitations

- **LLM accuracy** — smaller models (< 8B) may misread complex multi-distributor tables. 9B+ recommended.
- **JS-rendered sites** — Newark and Avnet product pages render via JavaScript; direct fetch gets empty content. Use an API method or DuckDuckGo agent instead.
- **Bot-protected sites (Web Search)** — DigiKey.com blocks browser-based CORS fetch requests. Use the DigiKey API or DuckDuckGo agent instead (LM Studio's visit_website tool bypasses browser fingerprinting).
- **Rate limiting** — API methods (Mouser, DigiKey, Octopart) apply a 1-second delay between requests with retry on 403/429. Large BOMs (50+ rows) may take a few minutes.
- **Octopart API offer selection** — returns the best single offer across all distributors; does not return per-distributor breakdowns.
- **Sandbox restrictions** — the tool must run locally in a browser, not inside Claude artifacts or other sandboxed iframes.
- **Save Datasheets** — uses Chrome's File System Access API to save files into a chosen folder; falls back to a ZIP download in Firefox and Safari. When the Allow CORS extension is disabled (or a URL is missing), the affected entries appear in a `_failed_links_TIMESTAMP.html` report rather than silently failing.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK.** This tool is provided for informational and estimation purposes only. Pricing, stock availability, lead times, and all other data retrieved by this tool may be inaccurate, outdated, or incomplete. **Always verify pricing and availability directly with the distributor before placing orders.** The authors assume no responsibility for purchasing decisions made based on this tool's output.

This tool relies on third-party websites and APIs whose terms of service, availability, and data accuracy are outside our control. Web scraping results depend on page structure which can change without notice. LLM-extracted data is inherently probabilistic and may contain errors.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
