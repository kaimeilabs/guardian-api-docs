# Guardian Engine by Kaimei Labs - API & SDK

Welcome to the **Guardian Engine** public SDK and Agent Connection repository, built by **Kaimei Labs**.

> **Guardian is the symbolic verification layer for neuro-symbolic AI pipelines — catching recipe hallucinations before they reach the pan. LLMs generate, Guardian verifies.**

When AI agents generate recipes, they hallucinate. They set ovens to impossible temperatures, skip the Maillard reaction, substitute ingredients that break emulsions, and produce dishes that fail in the real kitchen. Guardian Engine models each recipe as a **directed acyclic graph (DAG)** of culinary state transformations — verifying temperatures, durations, techniques, and ingredient interactions against curated master recipes from professional kitchens. The result: a strict authenticity and physics verification score (0–100%).

## Connecting Your Agent (MCP)

Guardian provides a native **Model Context Protocol (MCP)** server via HTTPS. No API key required. By connecting your agent via MCP, it will automatically gain access to tools like `verify_recipe` and `list_dishes`.

> *Free during early access. No API key required. Fair use applies — see our [terms](https://kaimeilabs.dev) for details.*

**Endpoint URL**: `https://api.kaimeilabs.dev/mcp`
**Transport**: Streamable HTTP (`mcp.client.streamable_http`)

### Quickstart

1. Ensure you have Python 3.10+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the live integration test to confirm connection to the public API:
   ```bash
   python test_integration.py
   ```
4. Check out `client.py` to see how to pass a structured recipe payload for verification.

### Custom Agents (LangChain, LlamaIndex, etc.)
If you are building a custom agent, connect directly to the public endpoint using the official Python MCP SDK. See `client.py` for a minimal example, or `test_integration.py` for a full integration test.

## 🍳 Available Verification Targets

Guardian can currently verify AI-generated recipes against **15 master recipes** spanning 10 cuisines. Each master recipe encodes the physics constraints (temperatures, durations, techniques, required ingredients) that define an authentic version of the dish.

| Cuisine | Dishes |
|---------|--------|
| **French** | Confit de Canard · Cheese Soufflé · Crème Brûlée · French Onion Soup |
| **Chinese** | Kung Pao Chicken · Cantonese Steamed Fish |
| **Indonesian** | Beef Rendang |
| **British** | Beef Wellington |
| **Italian** | Pasta Carbonara |
| **Spanish** | Basque Cheesecake |
| **American** | Southern Fried Chicken · Texas Smoked Brisket |
| **Peruvian** | Ceviche |
| **European** | Florentine Biscuits |
| **Universal** | Roast Chicken |

> 📌 New recipes are added regularly. Use the `list_dishes` tool to always get the current catalog from the live API.

> 💡 **Try it:** Ask your AI agent to generate a Beef Rendang recipe, then pass it to `verify_recipe` — Guardian will catch hallucinated cooking mediums, missing required ingredients, and incorrect state transformations.

## Files in this Repository
- `client.py`: A minimal Python example demonstrating how to submit a JSON recipe for verification.
- `test_integration.py`: A live integration test verifying connection to the Guardian API.

---

## 📊 Data & Privacy

- All tool calls are logged for analytics and service improvement (dish name, latency, verdict, submitted recipes)
- **No PII collected** — no user names, emails, IP addresses, or API keys
- Fair use quotas enforced via compute limits during open beta

---

## Support & Contact

Whether you're building an AI cooking assistant, a smart kitchen platform, or an agentic food-tech product — we want to hear from you.

*   **Email**: `partners@kaimeilabs.dev`
*   **Website**: [https://kaimeilabs.dev](https://kaimeilabs.dev)
*   **GitHub**: [github.com/kaimeilabs](https://github.com/kaimeilabs)

## License

The client code in this SDK repository (`client.py`, `test_integration.py`, etc.) is released under the open-source **MIT License**, so you can freely embed it into your proprietary agents.

*Note: The core Guardian Engine verification logic, Knowledge Graphs, and Master Recipe datasets running on the backend API are proprietary and closed-source.*
