# Guardian Engine: `candidate_json` Schema

When calling the `verify_recipe` or `fix_recipe` tools, you must provide the recipe in a structured JSON format via the `candidate_json` argument (a JSON string or object; max 500 KB).

The engine uses this structured data to verify your recipe against a master spec — either a curated catalog master (`dish_name`) or your own house recipe/SOP (`master_json`, see below).

## Allowed Values & Taxonomies
For best results, use standard culinary terminology as shown below.

*   **Techniques**: Use standard, snake_case culinary techniques (e.g., `pan_frying`, `braising`, `steaming`).
*   **Mediums**: Use simple, base culinary mediums. The Engine supports standard base values (e.g., `water`, `olive_oil`, `stock`, `wine`, `steam`) and will automatically resolve common culinary aliases (e.g., mapping "duck fat" to `fat`).
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

## Bring Your Own Master: `master_json` Schema

`verify_recipe` and `fix_recipe` accept an optional `master_json` argument (JSON string or object; max 500 KB) — your own house recipe or SOP to verify against. When supplied, the bundled catalog is bypassed, `dish_name` may be omitted, and the response pins your spec via `master_hash` (sha256) and `master_source: "user"` so the verdict is replayable.

The schema is the same as catalog masters — **call `get_master` on any catalog dish for a complete live example.** The key fields:

```json
{
  "title": "String - Name of the master spec (e.g. 'House Carbonara v2')",
  "cuisine": "String - Optional cuisine classifier",
  "serves": "Integer - Number of servings the quantities are calibrated for",
  "ingredients": [
    {"name": "String", "quantity": "Number", "unit": "String (e.g. 'g', 'ml')"}
  ],
  "required_ingredients": [
    {
      "name": "String - The canonical ingredient (e.g. 'guanciale')",
      "substitutes": ["String - Acceptable alternatives"],
      "critical": "Boolean - true escalates a missing/substituted ingredient to CRITICAL",
      "reason": "String - Why this ingredient is required (returned in findings)",
      "quantity": "Number", "unit": "String",
      "ratio_to": "String - Optional ingredient to hold a ratio against",
      "ratio_range": "[min, max] - Acceptable ratio window"
    }
  ],
  "steps": [
    {
      "step_number": "Integer",
      "title": "String",
      "instruction_english": "String",
      "technique": "String (e.g. 'braising')",
      "cooking_medium": "String",
      "estimated_temperature_c": "Number or [min, max]",
      "duration_minutes": "Number or [min, max]"
    }
  ]
}
```

A malformed master returns a structured `INVALID_MASTER` error rather than a server error.

---

## Enhancing Precision with `original_prompt`

The `verify_recipe` tool accepts an optional `original_prompt` string argument. We **encourage** agents and developers to pass the **full** original user request that generated the recipe (e.g., *"Write me a classic carbonara recipe, but I want a vegan version"*).

*   **If provided**: Guardian additionally activates safety-context awareness (e.g., flagging honey for infants, raw egg for pregnant users) and personalises feedback to the user's stated dietary needs and flavour preferences.
*   **If omitted**: Guardian still returns the full `PASSED`/`FAILED` verdict and all findings, with specific ingredient names and technique details — enough to fix most recipes.

## Example Payload (`candidate_json`)

Here is an example of a well-structured `candidate_json` payload for a simplified Beef Rendang:

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
