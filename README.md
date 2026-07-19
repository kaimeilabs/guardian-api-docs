# Guardian Engine — API & MCP Integration Guide

> **A deterministic oracle inside your agent's generate→verify loop.** Your LLM authors the recipe; Guardian judges it. Guardian Engine catches hallucinated temperatures, missing techniques, wrong ingredients, and impossible cooking steps before they reach the pan — and returns machine-actionable patches so your agent can fix exactly what's wrong. Recipes are the first vertical — the same deterministic approach generalises to any procedural domain where correctness matters.

**Why an oracle instead of another LLM critique?** An LLM critique is a *sample* — it misses differently on every run. Guardian's symbolic engine makes guarantees a generative model structurally cannot:

- **Exhaustive checking** — every rule is evaluated on every call, not a sample of them.
- **Certified negatives** — "no EU Annex II allergen source detected" is an absence claim an LLM cannot make.
- **Replayable verdicts** — same input + same spec + same knowledge-base version → byte-identical output. Every response pins `kb_version_hash` and `master_hash` so any verdict is reproducible as an audit record.
- **Machine-actionable repair** — findings come with structured `patches` (and `fix_recipe` can apply them deterministically); your agent authors the rest and re-verifies.
- **Bring your own spec** — verify against *your* house recipe or SOP via `master_json`, not just the bundled catalog.

[![Official MCP Registry](https://img.shields.io/badge/MCP%20Registry-Official-blue?logo=github)](https://registry.modelcontextprotocol.io/v0.1/servers/dev.kaimeilabs%2Fguardian-engine/versions/latest) [![Install with Smithery](https://smithery.ai/install-badge.svg)](https://smithery.ai/servers/kaimeilabs/guardian-engine) [![Glama.ai MCP Server](https://glama.ai/mcp/servers/badge)](https://glama.ai/mcp/servers/kaimeilabs/guardian-engine)

**Endpoint**: `https://api.kaimeilabs.dev/mcp`  
**Transport**: [Streamable HTTP (MCP)](https://modelcontextprotocol.io)  
**Auth**: None — free during early access (fair use applies)

---

> ## ⚠️ Safety & Liability Notice
>
> Guardian Engine is an **automated, informational** recipe-verification tool. It is **not** a
> food-safety, medical, nutritional, or regulatory-compliance authority, and its output is **not**
> professional advice.
>
> - **Allergens are not guaranteed.** Allergen warnings (including `check_safety`,
>   `check_allergens`, and the `allergens` field of every verification response) come from an
>   automated knowledge base that may be incomplete or wrong. A `PASSED` verdict or an empty
>   allergen list is **NOT** a guarantee that a recipe is free of any allergen or safe for any
>   individual. **Never** rely on Guardian to decide whether a food is safe for someone with a
>   food allergy or intolerance — always verify against the actual ingredient/product labelling
>   and consult a qualified professional.
> - **Dietary and religious claims are not certifications.** `verify_dietary_claim` results
>   (vegan, vegetarian, gluten-free, dairy-free, nut-free, halal, kosher) are automated
>   ingredient-level checks — they are **not** a substitute for certification by a recognised
>   dietary or religious authority.
> - **Repaired recipes are not certified safe.** `fix_recipe` output must be reviewed by a human
>   before being cooked, served, or published; allergen findings are never auto-fixed and a
>   repaired recipe may still fail verification.
> - **Cooking-safety findings are informational** and must not replace certified guidance (e.g.
>   USDA, EU FIC, or your local food-safety authority).
> - **No warranty.** The Service is provided "AS IS", without warranty of any kind. To the maximum
>   extent permitted by law, Kaimei Labs accepts no liability for any loss, injury, or damage
>   arising from use of, or reliance on, Guardian output.
>
> Use of the API constitutes acceptance of the full [Terms of Service](https://kaimeilabs.dev/terms)
> (warranty disclaimer, limitation of liability, indemnification).

---

## Connect Your Agent

Guardian is a hosted MCP server. No install, no API key, no Docker. Pick your client and paste the config.

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "guardian": {
      "url": "https://api.kaimeilabs.dev/mcp",
      "transport": "streamable-http"
    }
  }
}
```

Restart Claude Desktop. Ask: *"List the available dishes in Guardian Engine"* to confirm.

### Cursor

Open **Settings → MCP Servers → Add new MCP server**, then paste:

```json
{
  "guardian": {
    "url": "https://api.kaimeilabs.dev/mcp",
    "transport": "streamable-http"
  }
}
```

### VS Code (GitHub Copilot)

Add to your `.vscode/mcp.json` (or user `settings.json` under `"mcp"`):

```json
{
  "servers": {
    "guardian": {
      "type": "http",
      "url": "https://api.kaimeilabs.dev/mcp"
    }
  }
}
```

### Windsurf

Add to your Windsurf MCP config:

```json
{
  "mcpServers": {
    "guardian": {
      "serverUrl": "https://api.kaimeilabs.dev/mcp"
    }
  }
}
```

### Smithery (One-Click)

[![Install with Smithery](https://smithery.ai/install-badge.svg)](https://smithery.ai/servers/kaimeilabs/guardian-engine) — auto-configures Claude Desktop, Cursor, and more.

> [!WARNING]
> **Smithery Proxy Limitation:** The default Smithery proxy URL (`guardian-engine--kaimeilabs.run.tools`) **does not support Streaming HTTP** and will silently fail. You MUST edit your MCP config after installation to use the direct endpoint: `https://api.kaimeilabs.dev/mcp`.

### Glama.ai

Guardian Engine is also listed on **[Glama.ai](https://glama.ai/mcp/servers/kaimeilabs/guardian-engine)** — discover and connect to MCP servers from the Glama directory.

### Any MCP Client (Python SDK)

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from httpx import AsyncClient

async def main():
    async with AsyncClient(timeout=30.0) as http:
        async with streamable_http_client("https://api.kaimeilabs.dev/mcp", http_client=http) as streams:
            read_stream, write_stream, _ = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool("list_dishes", arguments={"cuisine_filter": "french"})
                print(result)

asyncio.run(main())
```

```bash
pip install mcp>=1.2.1 httpx>=0.27.0
```

---

## Tools

The MCP server exposes seven tools. `verify_recipe` is the core loop; the rest support the compare → verify → repair cycle and master-independent safety checks.

### `verify_recipe`

Verify a candidate recipe against a Guardian master spec. Returns a structured report with a strict `PASSED`/`FAILED` verdict (no scores) and detailed findings, each citing the rule it violated. The verdict is policy-driven: any `CRITICAL` finding fails the recipe; more than 5 `WARNING`s also fail.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dish_name` | string | Yes* | Name or alias of the dish (e.g. `"carbonara"`, `"rendang"`, `"kung-pao"`, `"bourguignon"`). `dish` is accepted as a backward-compatible alias. *Optional when `master_json` is supplied |
| `candidate_json` | string \| object | Yes | Full recipe as JSON — see [schema.md](schema.md). Max 500 KB |
| `master_json` | string \| object | No | **Bring your own master** — your house recipe/SOP to verify against, using the same schema as catalog masters. Bypasses the bundled catalog; the response pins your spec via `master_hash` (sha256) and `master_source: "user"` |
| `original_prompt` | string | No | The user's original request that generated the recipe |
| `response_format` | string | No | `"text"` (default) or `"json"`. Use `"json"` for machine-actionable patches in agentic self-correction loops |
| `session_id` | string | No | Track an agent's improvement loop across multiple attempts |
| `operator_id` | string | No | Audit identifier tagged into the verification log and compliance record (letters, digits, hyphens; max 64 chars) |

**Tip — include the original prompt for personalised feedback:** When you include `original_prompt` (e.g. *"Make a spicy vegan rendang"*), Guardian matches findings to the user's stated dietary needs and flavour preferences, and activates audience-sensitive safety checks (e.g. flagging honey in recipes for infants, raw egg for pregnant users). Without it, Guardian still returns the full verdict and all findings.

**Unknown dish?** If the dish isn't in the catalog, the `UNKNOWN_DISH` error carries a `safety_fallback` verdict — the master-independent safety layer (poultry temperature + allergen scan) still runs, so your agent always leaves with deterministic value.

**Field audience:** `issue` is a machine-readable code for programmatic handling — don't show it to end users. Use `title` and `suggested_correction` as the user-facing fields.

### `fix_recipe`

Deterministically repair a candidate recipe against a master spec. Verifies, applies every machine-actionable patch the symbolic engine produced (missing ingredients, quantities, temperatures, durations, cooking media, substitutions), then re-verifies. **No LLM is involved** — the repair is a deterministic function of the candidate and the ruleset.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dish_name` | string | Yes* | Dish to repair against (`dish` alias accepted). *Optional when `master_json` is supplied |
| `candidate_json` | string \| object | Yes | Same schema as `verify_recipe` |
| `master_json` | string \| object | No | BYO master to repair against; patches (including `suggested_step` templates) are built from *your* spec |
| `original_prompt` | string | No | Used only for safety-context awareness during verification |
| `response_format` | string | No | `"text"` (default) or `"json"` — use `"json"` to receive the full `fixed_recipe` object |

The response reports `verdict_before` → `verdict_after`, `fully_fixed`, `patches_applied`, `patches_skipped`, `unresolved_findings`, and the `fixed_recipe`. Changes that need recipe-authoring judgement (adding a whole cooking phase, rewriting instructions, ratio rebalancing) are **not** auto-applied — they're returned under `patches_skipped`, with `add_step` patches carrying a `suggested_step` template from the master for *your* agent to author in the recipe's own voice and re-verify. **Allergen findings are never auto-fixed.** Do not assume a fixed recipe will pass — check `verdict_after`.

### `list_dishes`

List all master recipes Guardian can verify against, with rich metadata (slug, title, cuisine, region, aliases, complexity).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cuisine_filter` | string | No | Case-insensitive cuisine filter (e.g. `"french"`, `"chinese"`, `"thai"`) |

### `get_master`

Return the canonical master recipe for a dish — a pure knowledge-base lookup, no LLM. Enables **compare-then-verify** loops: fetch the master, diff it against your recipe, then call `verify_recipe` instead of verifying blind. Master content is transparent by default: exact temperatures, timings, and EU FIC 1169/2011 allergen codes are returned verbatim. Also the live reference for the `master_json` schema when bringing your own master.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dish_name` | string | Yes | Name or alias of the dish |
| `response_format` | string | No | `"json"` (default) or `"text"` |

### `check_safety`

Master-independent safety checks for **any** recipe — no dish resolution or master spec required. Checks poultry internal-temperature safety (≥ 74 °C) and scans all ingredients against the 14 EU FIC 1169/2011 Annex II allergen groups. Use it when `verify_recipe` has no matching master.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `candidate_json` | string | Yes | Full candidate recipe as a JSON string |

### `check_allergens`

Check an ingredient list for EU FIC 1169/2011 allergen presence, with a detailed audit trace mapping each ingredient to its Annex II allergen group (entry numbers and labels included).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ingredients` | list[string] | Yes | Ingredient names, freeform or canonical (e.g. `["butter", "wheat_flour", "peanut_butter"]`) |
| `restrictions` | list[string] | No | Allergen group IDs to check against user restrictions: `gluten`, `crustaceans`, `eggs`, `fish`, `peanuts`, `soy`, `dairy`, `tree_nuts`, `celery`, `mustard`, `sesame`, `sulphites`, `lupin`, `molluscs` |
| `dish_name` | string | No | Reporting context |
| `check_all_eu_allergens` | boolean | No | `true` scans for all 14 Annex II groups regardless of `restrictions` — use for labelling-style "declare everything detected" checks |
| `response_format` | string | No | `"text"` (default) or `"json"` |

### `verify_dietary_claim`

Verify that a recipe satisfies a dietary claim, returning a structured verdict with the specific offending ingredients — never a vague paraphrase.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `candidate_json` | string | Yes | Recipe JSON (only the ingredient list is required) |
| `claim` | string | Yes | One of: `vegan`, `vegetarian`, `gluten_free`, `dairy_free`, `nut_free`, `halal`, `kosher` |
| `response_format` | string | No | `"text"` (default) or `"json"` |

---

## Bring Your Own Master (`master_json`)

The bundled catalog is a reference library — the primary production pattern is verifying against **your own spec**: a house recipe, a franchise SOP, a test kitchen's canonical version. Pass `master_json` to `verify_recipe` or `fix_recipe` (same schema as catalog masters — call `get_master` for a live example: `title`, `serves`, `ingredients[]`, `required_ingredients[]` with substitute tiers, `steps[]` with technique/temperature/duration/medium).

- When `master_json` is supplied, `dish_name` may be omitted and the catalog is bypassed entirely — the candidate is checked against *your* spec.
- The response pins the spec: `master_source: "user"` and `master_hash` (sha256 over the canonical master). Together with `kb_version_hash`, this makes every verdict **replayable**: anyone holding the same candidate, spec, and KB version reproduces the byte-identical result.
- Malformed masters return a structured `INVALID_MASTER` error, not a server error. Max 500 KB.

---

## Available Recipes (161 dishes, 5 regions)

| Region | Dishes |
|--------|--------|
| **Europe** | Basque Cheesecake · Beef Bourguignon · Beef Wellington · Butternut Squash Soup · Cacio e Pepe · Caprese Salad · Cassoulet · Cheese Soufflé · Chicken Cacciatore · Chicken Marsala · Chicken Piccata · Chocolate Soufflé · Confit de Canard · Coq au Riesling · Coq au Vin · Crème Brûlée · Crêpes · Fettuccine Alfredo · Fish & Chips · Florentine Biscuits · Focaccia Barese · French Omelette · French Onion Soup · Frittata · Gazpacho · Gnocchi di Patate · Goulash · Greek Salad · Köttbullar · Mille-Feuille · Minestrone · Niçoise Salad · Osso Buco · Pasta alla Norma · Pasta Carbonara · Pasta Pomodoro · Patatas Bravas · Penne alla Vodka · Pesto alla Genovese · Pierogi · Pissaladière · Potato-Leek Soup · Ratatouille · Risotto alla Milanese · Roast Chicken · Sauerbraten · Shepherd's Pie · Spanakopita · Spaghetti Aglio e Olio · Spaghetti all'Amatriciana · Spaghetti Bolognese · Spanish Paella · Steak Frites · Stollen · Tarte Tatin · Tiramisu · Tomato Soup · Tortilla Española |
| **Asia & Southeast Asia** | Banh Mi · Beef Rendang · Biryani · Bulgogi · Butter Chicken · Cantonese Steamed Fish · Char Kway Teow · Chicken Tikka Masala · Chow Mein · Dan Dan Noodles · Jianbing · Khao Soi · Kimchi Fried Rice · Kung Pao Chicken · Laksa · Lo Mein · Massaman Curry · Nasi Goreng · Nasi Lemak · Okonomiyaki · Pad See Ew · Pad Thai · Palak Paneer · Rogan Josh · Som Tum · Sushi Rice · Sweet & Sour Chicken · Teriyaki Chicken · Thai Green Curry · Tonkatsu · Tonkotsu Ramen · Yakisoba |
| **Middle East & North Africa** | Falafel · Hummus · Koshary · Lentil Soup · Moroccan Lamb Tagine · Mutabal · Pita Bread · Shakshuka · Shish Taouk · Tabbouleh |
| **Americas** | Angel Food Cake · Baked Potato · Baked Salmon · Baked Ziti · Banana Bread · BBQ Ribs · Biscuits & Gravy · Buttermilk Pancakes · Caesar Salad · Carnitas · Ceviche · Cheese Quesadilla · Chicken Fajitas · Chicken Noodle Soup · Chicken Parmesan · Chili con Carne · Chocolate Chip Cookies · Classic Chocolate Cake · Cobb Salad · Crab Cakes · Creamed Spinach · Eggs Benedict · Fish Tacos · French Dip Sandwich · French Toast · Fudge Brownies · Garlic Butter Shrimp · Ground Beef Tacos · Italian-American Meatballs · Jerk Chicken · Key Lime Pie · Lobster Roll · Lomo Saltado · Macaroni & Cheese · Mashed Potatoes · Mole Poblano · Pan-Seared Pork Chops · Pan-Seared Scallops · Pão de Queijo · Pastel de Choclo · Pecan Pie · Philly Cheesesteak · Pot Roast · Pozole · Pulled Pork · Roasted Brussels Sprouts · Roasted Cauliflower · Sautéed Mushrooms · Shrimp Scampi · Southern Fried Chicken · Tamales · Texas Smoked Brisket · Turkey Meatballs · Vanilla Cupcakes · Vegetable Fried Rice · Waldorf Salad |
| **Africa** | Bunny Chow · Efo Riro · Melktert · Muamba de Galinha · Suya |

All recipes accept multiple aliases (e.g. `"rendang"`, `"tikka-masala"`, `"risotto"`, `"bourguignon"`, `"carbonara"`). Use `list_dishes` for the full live catalog.

### Missing a Dish?
The catalog is regularly expanding. If your agent requires verification for a dish not currently supported, please **[open an issue on GitHub](https://github.com/kaimeilabs/guardian-api-docs/issues)** to request it. We prioritize additions based on developer demand.

---

## Example Verification Output

What does a Guardian verification report actually look like? Here's the (abridged) `response_format: "json"` structure when an agent submits a carbonara made with bacon, cream, and an overheated pan:

```json
{
  "api_version": "0.7.1",
  "schema_version": "1.0",
  "response_format_version": "v3",
  "kb_version_hash": "7dda40a3b646",
  "verdict": "FAILED",
  "matched_against": "Pasta alla Carbonara (Master)",
  "master_source": "catalog",
  "master_hash": "3357e0929021c0003fea0b79015e2c53cf9ef50d70f0d507605788ad9741fd29",
  "coverage_percentage": 100.0,
  "summary": {"CRITICAL": 4, "WARNING": 0, "INFO": 3},
  "findings": [
    {
      "step_index": 2,
      "issue": "TEMPERATURE_MISMATCH",
      "severity": "critical",
      "justification": "Temperature is significantly outside the required range.",
      "title": "rendering",
      "details": {"expected": "100.0-130.0", "observed": "180"},
      "dimension": "temperature"
    },
    {
      "step_index": null,
      "issue": "INGREDIENT_SUBSTITUTED",
      "severity": "critical",
      "justification": "'bacon' is in the same group ('cured_pork') as 'guanciale' but is not the canonical ingredient for this recipe.",
      "title": "You used bacon, expected guanciale",
      "details": {"expected": "guanciale", "observed": "bacon"},
      "dimension": "ingredients"
    }
  ],
  "allergens": [
    "Allergen detected: Pork-derived ingredients (halal/kosher compliance)",
    "Allergen detected: Milk and products thereof (including lactose)",
    "Allergen detected: Cereals containing gluten (wheat, rye, barley, oats, spelt, kamut)"
  ],
  "patches": [
    {"action": "set_temperature", "step_index": 2, "value": "100.0-130.0"},
    {"action": "replace_ingredient", "remove": "bacon", "add": "guanciale"}
  ]
}
```

Each finding carries a `severity`, a `justification` grounded in culinary science, and machine-readable `details` — and the `patches` array tells your agent *exactly* what change would resolve each fixable finding, so it repairs only what's wrong instead of regenerating and guessing. `kb_version_hash` + `master_hash` pin the exact knowledge-base and spec versions the verdict was computed against, making the result replayable as an audit record.

Patch actions: `add_ingredient`, `replace_ingredient`, `set_quantity`, `adjust_quantity`, `set_temperature`, `set_duration`, `set_medium`, and `add_step` (which includes a `suggested_step` template for your agent to author, then re-verify).

---

## Files in This Repository

| File | Purpose |
|------|---------|
| `schema.md` | Complete `candidate_json` structure required by `verify_recipe` |
| `client.py` | Python example: submit a recipe for verification |
| `test_integration.py` | Live connectivity test against the public API |
| `smithery.yaml` | Smithery MCP registry configuration |
| `glama.json` | Glama.ai MCP server claim configuration |

---

## Data & Privacy

- **No PII collected** — we do not store user names, emails, or API keys. Underlying cloud infrastructure may temporarily process IP addresses for routing.
- **Data for Compute Exchange** — the free service is provided in exchange for usage data. Submitted recipes are used to improve verification accuracy and create anonymized derived datasets. See our [Terms of Service](https://kaimeilabs.dev/terms).
- **Do not include PII** in recipe payloads.
- Fair use quotas enforced via compute limits.

> [!CAUTION]
> **Not a Substitute for Food Safety Knowledge**  
> While Guardian Engine catches explicitly dangerous AI hallucinations (like serving poultry below safe temperatures), it cannot guarantee a recipe is 100% safe to consume. Pathogen destruction relies on variables (time, mass, equipment) that text-based AI models cannot perfectly control. Verification results are informational and must always be paired with human common sense and standard kitchen safety practices.

---

## Support & Contact

Building an AI cooking assistant, smart kitchen platform, or agentic food-tech product? We'd love to hear from you.

- **Email**: partners@kaimeilabs.dev
- **Website**: [kaimeilabs.dev](https://kaimeilabs.dev)
- **GitHub**: [github.com/kaimeilabs](https://github.com/kaimeilabs)

## License

Client code in this repository (`client.py`, `test_integration.py`) is released under the **MIT License**. The Guardian Engine verification logic and master recipe datasets are proprietary.
