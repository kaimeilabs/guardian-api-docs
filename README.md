# Guardian Engine — API & MCP Integration Guide

> **LLMs generate, Guardian verifies.** Deterministic recipe verification for AI agents — catches hallucinated temperatures, missing techniques, wrong ingredients, and impossible cooking steps before they reach the pan.

[![Install with Smithery](https://smithery.ai/install-badge.svg)](https://smithery.ai/servers/kaimeilabs/guardian-engine)

**Endpoint**: `https://api.kaimeilabs.dev/mcp`  
**Transport**: [Streamable HTTP (MCP)](https://modelcontextprotocol.io)  
**Auth**: None — free during early access (fair use applies)

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

> **(Note to Smithery users: The default Smithery proxy URL `guardian-engine--kaimeilabs.run.tools` does not support Streaming HTTP. Use `https://api.kaimeilabs.dev/mcp` directly.)**

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

Verify a candidate recipe against a Guardian master recipe. Returns a structured report with verdict, score, and detailed findings.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dish` | string | Yes | Name or alias of the dish (e.g. `"carbonara"`, `"rendang"`, `"kung-pao"`, `"bourguignon"`) |
| `candidate_json` | string | Yes | Full recipe as a JSON string — see [schema.md](schema.md) |
| `original_prompt` | string | No | The user's original request that generated the recipe |

**Tip — pass the prompt for better feedback:** When you include `original_prompt` (e.g. *"Make a spicy vegan rendang"*), Guardian activates **Guided Oracle Mode**: it reads the user's intent and returns specific, actionable improvement hints tailored to their request. Without it, Guardian returns only a Pass/Fail verdict and score.

### `list_dishes`

List all master recipes Guardian can verify against.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cuisine_filter` | string | No | Filter by cuisine (e.g. `"french"`, `"chinese"`, `"thai"`) |

---

## Available Recipes (20 dishes, 12 cuisines)

| Cuisine | Dishes |
|---------|--------|
| **French** | Confit de Canard · Cheese Soufflé · Crème Brûlée · French Onion Soup · Coq au Vin · Beef Bourguignon |
| **Chinese** | Kung Pao Chicken · Cantonese Steamed Fish |
| **Thai** | Thai Green Curry |
| **Indian** | Chicken Tikka Masala |
| **Indonesian** | Beef Rendang |
| **British** | Beef Wellington |
| **Italian** | Pasta Carbonara · Risotto alla Milanese |
| **Spanish** | Basque Cheesecake |
| **American** | Southern Fried Chicken · Texas Smoked Brisket |
| **Peruvian** | Ceviche |
| **European** | Florentine Biscuits |
| **Universal** | Roast Chicken |

All recipes accept multiple aliases (e.g. `"gong-bao"`, `"tikka"`, `"risotto"`, `"bourguignon"`). Use `list_dishes` for the full live catalog — new dishes are added regularly.

---

## Files in This Repository

| File | Purpose |
|------|---------|
| `schema.md` | Complete `candidate_json` structure required by `verify_recipe` |
| `client.py` | Python example: submit a recipe for verification |
| `test_integration.py` | Live connectivity test against the public API |
| `smithery.yaml` | Smithery MCP registry configuration |

---

## Data & Privacy

- **No PII collected** — we do not store user names, emails, or API keys. Underlying cloud infrastructure may temporarily process IP addresses for routing.
- **Data for Compute Exchange** — the free service is provided in exchange for usage data. Submitted recipes are used to improve verification accuracy and create anonymized derived datasets. See our [Terms of Service](https://kaimeilabs.dev/terms).
- **Do not include PII** in recipe payloads.
- Fair use quotas enforced via compute limits.

> ⚠️ **Disclaimer**: Verification results, including safety-related findings such as cooking temperatures and allergen warnings, are automated and informational only. They should not be relied upon as professional food safety, health, or culinary advice.

---

## Support & Contact

Building an AI cooking assistant, smart kitchen platform, or agentic food-tech product? We'd love to hear from you.

- **Email**: partners@kaimeilabs.dev
- **Website**: [kaimeilabs.dev](https://kaimeilabs.dev)
- **GitHub**: [github.com/kaimeilabs](https://github.com/kaimeilabs)

## License

Client code in this repository (`client.py`, `test_integration.py`) is released under the **MIT License**. The Guardian Engine verification logic and master recipe datasets are proprietary.
