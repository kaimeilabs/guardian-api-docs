# Guardian Engine by Kaimei Labs - API & SDK

Welcome to the **Guardian Engine** public SDK and Agent Connection repository, built by **Kaimei Labs**.

> **Guardian verifies AI-generated recipes against curated master recipes from professional kitchens — catching hallucinations before they reach the pan. LLMs generate, Guardian verifies.**

When AI agents generate recipes, they hallucinate. They set ovens to impossible temperatures, skip critical cooking steps, substitute ingredients that break emulsions, and produce dishes that fail in the real kitchen. Guardian Engine verifies each recipe against curated master standards from professional kitchens, checking temperatures, durations, techniques, and ingredient correctness. The result: a strict authenticity and verification score.

## Connecting Your Agent (MCP)

Guardian provides a native **Model Context Protocol (MCP)** server via HTTPS. No API key required. By connecting your agent via MCP, it will automatically gain access to tools like `verify_recipe` and `list_dishes`.

> *Free during early access. No API key required. Fair use applies — see our [terms](https://kaimeilabs.dev/terms) for details.*

**One-Click Install**: [![Install with Smithery](https://smithery.ai/install-badge.svg)](https://smithery.ai/servers/kaimeilabs/guardian-engine)

**Endpoint URL**: `https://api.kaimeilabs.dev/mcp`
**(Note to Smithery users: The default Smithery proxy URL `guardian-engine--kaimeilabs.run.tools` does not support Streaming HTTP. Please use `https://api.kaimeilabs.dev/mcp` directly).**
**Transport**: Streamable HTTP (`mcp.client.streamable_http`)

### Tools Provided

1. **`verify_recipe`**: Verify a candidate recipe against a Guardian master recipe.
2. **`list_dishes`**: List all available master recipes that Guardian can verify against.

### Quickstart (Python)

Evaluator agents and Python developers can connect via the official `mcp` SDK using `StreamableHttpClient`:

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import StreamableHttpClient

async def main():
    async with StreamableHttpClient("https://api.kaimeilabs.dev/mcp") as http_client:
        async with ClientSession(http_client) as session:
            # Initialize connection
            await session.initialize()

            # Call the tool
            result = await session.call_tool(
                "list_dishes",
                arguments={"cuisine_filter": "french"}
            )
            print("Response:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

1. Ensure you have Python 3.10+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the live integration test to confirm connection to the public API:
   ```bash
   python test_integration.py
   ```
4. Check out `client.py` for a full JSON recipe payload example.

### Custom Agents (LangChain, LlamaIndex, etc.)
If you are building a custom agent, connect directly to the `https://api.kaimeilabs.dev/mcp` endpoint using the official Python MCP SDK. See `client.py` for a minimal example, or `test_integration.py` for a full integration test.


## 🍳 Available Verification Targets

Guardian can currently verify AI-generated recipes against **17 master recipes** spanning 11 cuisines. Each master recipe encodes the culinary standards that define an authentic version of the dish.

| Cuisine | Dishes |
|---------|--------|
| **French** | Confit de Canard · Cheese Soufflé · Crème Brûlée · French Onion Soup · Coq au Vin |
| **Chinese** | Kung Pao Chicken · Cantonese Steamed Fish |
| **Indian** | Chicken Tikka Masala |
| **Indonesian** | Beef Rendang |
| **British** | Beef Wellington |
| **Italian** | Pasta Carbonara |
| **Spanish** | Basque Cheesecake |
| **American** | Southern Fried Chicken · Texas Smoked Brisket |
| **Peruvian** | Ceviche |
| **European** | Florentine Biscuits |
| **Universal** | Roast Chicken |

> 📌 New recipes are added regularly. Use the `list_dishes` tool to always get the current catalog from the live API.

> 💡 **Try it:** Ask your AI agent to generate a Beef Rendang recipe, then pass it to `verify_recipe` — Guardian will catch hallucinated cooking methods, missing required ingredients, and incorrect techniques.

> 🗣️ **Send the Prompt:** We highly encourage you to pass the user's explicit request to `verify_recipe` via the optional `original_prompt` argument (e.g. `original_prompt="Make it extremely spicy and low-sodium"`). Doing so allows the Guardian engine to account for specific dietary or flavor intent, granting your agent much higher precision and fewer false-positive failures!

## Files in this Repository
- `schema.md`: Complete documentation of the `candidate_json` structure required by the `verify_recipe` tool.
- `client.py`: A minimal Python example demonstrating how to submit a JSON recipe for verification.
- `test_integration.py`: A live integration test verifying connection to the Guardian API.

---

## 📊 Data & Privacy

- **No PII collected** — we do not store user names, emails, or API keys in our application logs. Underlying cloud infrastructure may temporarily process IP addresses for routing and security.
- **Data for Compute Exchange** — the free early-access Service is provided in exchange for usage data. Submitted recipes are used to train models, improve verification accuracy, and create derived datasets. All external data products are anonymized. See our [Terms of Service](https://kaimeilabs.dev/terms) for full details.
- **Do not include PII** in your recipe payloads (e.g., author names, email addresses). You are responsible for ensuring submitted content is free of personal data.
- Fair use quotas enforced via compute limits during early access.

> ⚠️ **Disclaimer**: Guardian verification results, including safety-related findings such as cooking temperatures and allergen warnings, are automated and informational only. They should not be relied upon as professional food safety, health, or culinary advice.

---

## Support & Contact

Whether you're building an AI cooking assistant, a smart kitchen platform, or an agentic food-tech product — we want to hear from you.

*   **Email**: `partners@kaimeilabs.dev`
*   **Website**: [https://kaimeilabs.dev](https://kaimeilabs.dev)
*   **GitHub**: [github.com/kaimeilabs](https://github.com/kaimeilabs)

## License

The client code in this SDK repository (`client.py`, `test_integration.py`, etc.) is released under the open-source **MIT License**, so you can freely embed it into your proprietary agents.

*Note: The core Guardian Engine verification logic and Master Recipe datasets running on the backend API are proprietary and closed-source.*
