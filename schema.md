# Guardian Engine: `candidate_json` Schema

When calling the `verify_recipe` tool, you must provide the recipe in a structured JSON format via the `candidate_json` argument.

The engine uses this structured data to verify your recipe against curated master recipes.

## Allowed Values & Taxonomies
For best results, use standard culinary terminology as shown below.

*   **Techniques**: Use standard, snake_case culinary techniques (e.g., `pan_frying`, `braising`, `steaming`).
*   **Mediums**: Use simple, base culinary mediums (e.g., `water`, `oil`, `stock`).
*   **Ingredients**: Always use singular, simple names (e.g., `salt`, `black_pepper`, `olive_oil`, `garlic`, `onion`).

---

## Schema Definition

```json
{
  "title": "String - The name of the dish (e.g. 'Beef Rendang')",
  "cuisine": "String - Optional cuisine classifier (e.g. 'Indonesian')",
  "serves": "Integer - Number of servings (e.g. 4)",
  "ingredients": [
    {
      "name": "String - The canonical ingredient name (e.g. 'coconut_milk')",
      "quantity": "String - The amount with unit (e.g. '400ml')"
    }
  ],
  "steps": [
    {
      "step_number": "Integer - Sequential step index (e.g. 1)",
      "title": "String - Short step description",
      "instruction_english": "String - Full natural language instruction",
      
      "technique": "String - A culinary technique (e.g. 'braising')",
      "cooking_medium": "String - Must be from allowed mediums list (e.g. 'sauce')",
      "estimated_temperature_c": "Number or Array - The applied heat. Can be exact (100) or a range ([90, 100])",
      "duration_minutes": "Number or Array - Time required. Can be exact (120) or a range ([90, 150])"
    }
  ]
}
```

---

## Enhancing Precision with `original_prompt` (Guided Oracle Mode)

While not strictly part of `candidate_json`, the `verify_recipe` tool accepts an optional `original_prompt` string argument. We **highly encourage** developers and agents to pass the **full** original user intent that generated the recipe (e.g., "Write me a classic carbonara recipe, but I want a vegan version of this").

*   **If provided (Guided Oracle Mode + Intent Spotlighting)**: Guardian uses the prompt to understand what the user wants (like specific flavors or dietary needs) and gives you exact, personalized tips to improve the recipe.
*   **If omitted (Strict Oracle Mode)**: To protect proprietary logic against scraping, Guardian only returns a high-level Pass/Fail verification of the recipe's basic structure without itemized feedback.

## Example Payload (`candidate_json`)

Here is an example of a perfectly structured `candidate_json` payload for a simplified Beef Rendang step.
*(Note: The temperatures and durations below are dummy values to illustrate the format. The true verified thresholds are proprietary.)*

```json
{
  "title": "Beef Rendang",
  "cuisine": "Indonesian",
  "serves": 4,
  "ingredients": [
    {"name": "beef_chuck", "quantity": "1kg"},
    {"name": "coconut_milk", "quantity": "400ml"},
    {"name": "rendang_paste", "quantity": "200g"}
  ],
  "steps": [
    {
      "step_number": 1,
      "title": "Sauté the aromatics",
      "instruction_english": "Heat oil in a pan and sauté the rempah (spice paste) until fragrant and oil separates.",
      "technique": "sautéing",
      "cooking_medium": "oil",
      "estimated_temperature_c": [100, 200],
      "duration_minutes": [5, 30]
    },
    {
      "step_number": 2,
      "title": "Slow Braise",
      "instruction_english": "Add the beef chuck and coconut milk. Turn heat to low and simmer very slowly until meat is tender.",
      "technique": "braising",
      "cooking_medium": "sauce",
      "estimated_temperature_c": [80, 110],
      "duration_minutes": [60, 300]
    }
  ]
}
```
