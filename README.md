# Guardian Engine — API & MCP Integration Guide

> **Deterministic verification infrastructure for AI agent outputs.** Guardian Engine catches hallucinated temperatures, missing techniques, wrong ingredients, and impossible cooking steps before they reach the pan. Recipes are the first vertical — the same deterministic approach generalises to any procedural domain where correctness matters.

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
> - **Allergens are not guaranteed.** Allergen warnings come from an automated knowledge base that
>   may be incomplete or wrong. A `PASSED` verdict is **NOT** a guarantee that a recipe is free of
>   any allergen or safe for any individual. **Never** rely on Guardian to decide whether a food is
>   safe for someone with a food allergy or intolerance — always verify against the actual
>   ingredient/product labelling and consult a qualified professional.
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

### `verify_recipe`

Verify a candidate recipe against a Guardian master recipe. Returns a structured report with a `PASSED`/`FAILED` verdict and detailed findings (each citing the rule it violated).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dish` | string | Yes | Name or alias of the dish (e.g. `"carbonara"`, `"rendang"`, `"kung-pao"`, `"bourguignon"`) |
| `candidate_json` | string | Yes | Full recipe as a JSON string — see [schema.md](schema.md) |
| `original_prompt` | string | No | The user's original request that generated the recipe |
| `response_format` | string | No | `"text"` (default) or `"json"`. Use `"json"` for machine-actionable patches in agentic self-correction loops |

**Tip — include the original prompt for personalised feedback:** When you include `original_prompt` (e.g. *"Make a spicy vegan rendang"*), Guardian matches findings to the user's stated dietary needs and flavour preferences (e.g. flagging which specific issue conflicts with a "vegan" or "spicy" intent), and activates audience-sensitive safety checks (e.g. flagging honey in recipes for infants, raw egg for pregnant users). Without it, Guardian still returns the full verdict and all findings.

### `list_dishes`

List all master recipes Guardian can verify against.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cuisine_filter` | string | No | Filter by cuisine (e.g. `"french"`, `"chinese"`, `"thai"`) |

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

What does a Guardian verification report actually look like? Here's the response structure when an AI agent submits a recipe with authenticity issues:

```json
{
  "verdict": "FAILED",
  "response_format_version": "v3",
  "findings": [
    {
      "issue": "MISSING_REQUIRED_INGREDIENT",
      "severity": "CRITICAL",
      "justification": "This ingredient provides a signature flavour component essential to the dish's identity."
    },
    {
      "issue": "WRONG_COOKING_MEDIUM",
      "severity": "WARNING",
      "justification": "Cooking medium fundamentally affects texture and flavour."
    }
  ],
  "allergen_warnings": ["milk", "eggs"],
  "summary": {"INFO": 1, "WARNING": 1, "CRITICAL": 2}
}
```

Each finding includes a `severity` and a `justification` grounded in culinary science — letting the agent fix only what's wrong instead of guessing.

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
