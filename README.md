# BOM Pricing Review Tool

> A browser-based BOM pricing tool that searches electronics distributors (via web scraping + local LLM or Mouser API) for component pricing, stock, and availability, and exports an enriched spreadsheet with per-line cost analysis.

A browser-based tool that takes an electronic Bill of Materials (BOM), searches distributor websites for pricing and availability, and outputs an enriched spreadsheet with pricing data.

Runs entirely in the browser — no server backend required. Uses a local LLM (via LM Studio) for web page analysis, or the Mouser API for direct structured queries.

## Files

| File | Description |
|------|-------------|
| `bom-pricing-tool.html` | Main application — BOM batch processor |
| `part-search-test.html` | Single-part search tool for testing and debugging |

## Search Methods

**Web Search (fetch + LLM)** — Fetches distributor search pages, LLM finds product URLs, fetches each product page, LLM verifies MPN and extracts pricing. Supports Octopart (default), DigiKey, Future Electronics, or custom URLs.

**Mouser API** — Direct REST API call. Returns structured JSON — no LLM needed. Requires a free API key from [mouser.com/api-hub](https://www.mouser.com/api-hub/).

**DuckDuckGo Agent** — Searches DuckDuckGo for the part, scores and filters up to 15 product page candidates, LLM visits each via tool-calling and extracts pricing. Requires a model with function-calling support (Qwen 2.5+, Llama 3.1+).

## Prerequisites

- **Chrome** with [Allow CORS](https://chromewebstore.google.com/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf) extension enabled
  - CORS settings: set Origin mode to ORIGIN (option 5)
- **LM Studio** at `127.0.0.1:1234` (configurable) with a model loaded (8B+ recommended, e.g. Qwen 3.5-9B)
  - Developer tab → Server settings → Enable CORS
  - Not needed for Mouser API method
  - For DuckDuckGo search: the model must support tool/function calling, and the [visit-website tool](https://lmstudio.ai/docs/features/tool-use) must be enabled in LM Studio
- Visit the distributor site once before searching (establishes cookies for Web Search method)

## How It Works

1. **Upload BOM** — drag/drop Excel (.xlsx) or CSV file
2. **Map columns** — Manufacturer, Part Number, Quantity, Description. Auto-detected from header names.
3. **Configure** — select search method, set build quantity
4. **Process** — searches each row, displays live results
5. **Export** — downloads enriched Excel file with original data plus pricing columns

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
- **JS-rendered sites** — Newark and Avnet product pages render via JavaScript; fetch gets empty content. Use Octopart or Mouser API instead.
- **Akamai-protected sites** — some Mouser product pages block CORS fetch requests. The Mouser API works fine.
- **Rate limiting** — Mouser API has a 1-second delay between requests with retry on 403. Large BOMs (50+ rows) may take a few minutes.
- **Sandbox restrictions** — the tool must run locally in a browser, not inside Claude artifacts or other sandboxed iframes.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK.** This tool is provided for informational and estimation purposes only. Pricing, stock availability, lead times, and all other data retrieved by this tool may be inaccurate, outdated, or incomplete. **Always verify pricing and availability directly with the distributor before placing orders.** The authors assume no responsibility for purchasing decisions made based on this tool's output.

This tool relies on third-party websites and APIs whose terms of service, availability, and data accuracy are outside our control. Web scraping results depend on page structure which can change without notice. LLM-extracted data is inherently probabilistic and may contain errors.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
