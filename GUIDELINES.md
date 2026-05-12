# GUIDELINES.md — Guidelines Data
## Copy each JSON block into the corresponding file in `data/`

---

## Sources

| File | Source |
|---|---|
| `brand_guidelines.json` | Inferred from iams.com, pedigree.com, and official retailer brand pages + AAFCO + FTC |
| `amazon_rules.json` | Amazon Seller Central G200390640 + January 2025 title policy update |
| `walmart_rules.json` | Official Walmart retailer content guidelines document (Mars Petcare team) |
| `rufus_criteria.json` | Amazon Rufus documented behaviour — genrise.ai, pacvue.com |
| `sparky_criteria.json` | Walmart Sparky documented behaviour — envisionhorizons.com, code3.com |

---

## `data/brand_guidelines.json`

```json
{
  "brand_naming": {
    "IAMS": {
      "correct_spelling": "IAMS",
      "capitalisation": "ALL CAPS — exception to title-case rule on all retailers",
      "prohibited_variations": ["Iams", "iams"]
    },
    "Pedigree": {
      "correct_spelling": "Pedigree",
      "capitalisation": "Title case only",
      "prohibited_variations": ["PEDIGREE", "pedigree"]
    }
  },
  "approved_claims": {
    "iams_minichunks": [
      "Real chicken is the #1 ingredient",
      "Veterinarians recommend IAMS",
      "No artificial flavors or preservatives",
      "Supports healthy digestion with prebiotics and natural fiber",
      "L-Carnitine supports fat metabolism and healthy weight",
      "100% complete and balanced for adult maintenance",
      "AAFCO complete and balanced for adult dogs",
      "Omega-6 and Omega-3 fatty acids support healthy skin and coat",
      "Enriched with antioxidants to support immune system",
      "Supports strong muscles with protein from chicken and egg",
      "No fillers",
      "Made with wholesome grains for healthy energy"
    ],
    "iams_largebreed": [
      "Real chicken is the #1 ingredient",
      "Veterinarians recommend IAMS",
      "No artificial flavors or preservatives",
      "100% complete and balanced for adult maintenance",
      "AAFCO complete and balanced for adult dogs",
      "Supports healthy digestion with prebiotics",
      "Supports strong muscles with protein from chicken and egg",
      "Formulated for large breed adult dogs",
      "Supports bone and joint health",
      "0% fillers"
    ],
    "pedigree_compnutr": [
      "100% complete and balanced for adult dogs",
      "36 vitamins, minerals, and amino acids",
      "Prebiotic fiber to support healthy digestion",
      "Omega-6 Fatty Acid and Zinc to help nourish healthy skin and coat",
      "No high fructose corn syrup",
      "No artificial flavors",
      "No added sugar",
      "Made in the USA",
      "Supports everyday health and natural vitality",
      "Antioxidants, vitamins, and minerals to help maintain a healthy lifestyle",
      "Crunchy kibble helps clean teeth"
    ]
  },
  "prohibited_claims_all_brands": [
    "Best dog food", "Superior to", "Better than", "Clinically proven",
    "Cures", "Prevents disease", "Guaranteed results", "World's best", "Award winning"
  ],
  "regulatory_rules": [
    {
      "rule_id": "aafco_growth_language",
      "rule": "No growth language in adult food",
      "description": "The word 'growth' in an adult dog food violates AAFCO life stage definitions. Growth is reserved for puppy formulas. Adult food must use 'adult maintenance' language.",
      "severity": "critical",
      "source": "AAFCO Dog Food Nutrient Profiles"
    },
    {
      "rule_id": "aafco_natural_definition",
      "rule": "Natural claim accuracy",
      "description": "Cannot claim 'natural' alongside synthetic artificial colours or preservatives without a qualifying disclaimer.",
      "severity": "high",
      "source": "AAFCO natural definition"
    },
    {
      "rule_id": "vet_recommended_substantiation",
      "rule": "Vet recommendation must be substantiated",
      "description": "IAMS has documented basis for vet recommendation claim. Pedigree does not — this claim must not appear on Pedigree listings.",
      "severity": "high",
      "source": "FTC advertising substantiation guidelines"
    },
    {
      "rule_id": "ingredient_transparency",
      "rule": "No misleading omission of controversial ingredients",
      "description": "Content must not be misleading about ingredient composition. Controversial ingredients present in formula (BHA, artificial colours) must not be concealed by content claiming only natural ingredients.",
      "severity": "critical",
      "source": "FTC deceptive advertising guidelines"
    }
  ]
}
```

---

## `data/amazon_rules.json`

```json
{
  "retailer": "Amazon",
  "ai_assistant": "Rufus",
  "title": {
    "max_characters": 200,
    "recommended_max": 150,
    "rules": [
      "Must include brand name and product size",
      "Sentence case — not all caps except brand names designed as all caps",
      "Same word may not appear more than twice (prepositions, articles, conjunctions excepted)",
      "No promotional language"
    ],
    "prohibited_characters": ["!", "$", "?", "_", "{", "}", "^", "¬", "¦"],
    "allowed_separators": ["|", "-"],
    "prohibited_terms": [
      "Best Seller", "Top Quality", "Free Shipping", "#1 rated",
      "Amazing", "Sale", "Limited Time", "Buy Now", "100% Guarantee"
    ]
  },
  "bullets": {
    "recommended_count": 5,
    "max_count": 5,
    "max_characters_per_bullet": 200,
    "rules": [
      "Lead with a benefit or key feature",
      "No pricing, promotional claims, or competitor mentions",
      "No ALL CAPS text",
      "No abbreviations",
      "No hyphens or exclamation points",
      "No shipping or seller information",
      "No vague statements without specificity"
    ],
    "prohibited_promotional_words": [
      "easy", "safe", "effective", "amazing", "incredible", "best",
      "great tasting", "guaranteed", "proven", "revolutionary",
      "premium", "world's finest", "superior"
    ]
  },
  "description": {
    "min_characters": 100,
    "max_characters": 2000,
    "rules": [
      "Plain text or basic HTML",
      "No bullet points within description",
      "No pricing claims"
    ]
  },
  "prohibited_language": {
    "superlatives": ["world's finest", "world's best", "finest ingredients", "greatest", "unmatched"],
    "subjective": ["great tasting", "delicious", "amazing", "incredible"],
    "promotional": ["on sale", "limited time", "buy now", "free shipping"]
  },
  "general_rules": [
    "No false product identification information",
    "No misleading content",
    "Product content must accurately represent the product"
  ]
}
```

---

## `data/walmart_rules.json`

```json
{
  "retailer": "Walmart",
  "ai_assistant": "Sparky",
  "title": {
    "ideal_max_characters": 90,
    "hard_max_characters": 100,
    "formula": "Brand + Product Line + Pet Food Flavor + Pet Food Condition + Pet Food Form + Dry Dog Food + Animal Lifestage + Nutrient Content Claims + Size + Container Type",
    "rules": [
      "No standalone 'dog' or 'cat' — must use full 'Adult Dog Food' or 'Dry Dog Food' phrasing",
      "Sizing must be lowercase — lb. and oz. not LB or OZ"
    ],
    "prohibited_in_title": ["Uppercase sizing", "Special characters: ®, TM, *, !, ?"]
  },
  "bullets": {
    "minimum_count": 4,
    "recommended_count": 6,
    "rules": [
      "Begin each bullet with a capital letter",
      "Sentence fragments — not full sentences",
      "No ending punctuation",
      "Do not open with the word 'contains'",
      "# symbol is permitted",
      "No special characters: *, !"
    ]
  },
  "description": {
    "min_words": 60,
    "recommended_words": 150,
    "format": "HTML paragraph: <p>text here</p>",
    "rules": [
      "Paragraph form only — no bullet points",
      "Repeat product name and keywords for SEO"
    ]
  },
  "images": {
    "hero_image_required": true,
    "secondary_images_recommended": 9
  },
  "general_rules": [
    {
      "rule_id": "brand_capitalisation",
      "rule": "Brand capitalised but NOT all caps — IAMS is the only exception",
      "severity": "critical"
    },
    {
      "rule_id": "no_made_in_usa",
      "rule": "No domestic origin claims — no 'Made in USA', 'US Chicken', 'US Facilities', or equivalent including 'Domestically crafted'",
      "severity": "critical"
    },
    {
      "rule_id": "no_standalone_disclaimers",
      "rule": "Disclaimers must be integrated within copy — no asterisk (*) disclaimers",
      "severity": "high"
    },
    {
      "rule_id": "no_special_characters",
      "rule": "No ®, TM, (*), or similar special characters in any content field",
      "severity": "high"
    }
  ]
}
```

---

## `data/rufus_criteria.json`

```json
{
  "retailer": "Amazon",
  "ai_assistant": "Rufus",
  "behaviour_summary": "Rufus synthesises listing copy, reviews, and Q&A to recommend products. Rewards descriptive, review-aligned, fact-dense content that answers natural language shopper questions.",
  "scoring_note": "Score each dimension and sum. Raw total out of 100 × 0.30 = contribution to overall score.",
  "scoring_dimensions": [
    {
      "id": "named_protein_source",
      "label": "Named protein source",
      "max_points": 15,
      "full_points_when": "Named protein in title AND first or second bullet (e.g. 'Real chicken is the #1 ingredient')",
      "partial_points_when": "Named protein present but not prominently featured",
      "zero_when": "Protein source vague or generic (e.g. 'animal protein', 'meat meal')"
    },
    {
      "id": "fact_density",
      "label": "Fact density",
      "max_points": 20,
      "full_points_when": "Majority of bullets contain specific verifiable facts with numbers, named ingredients, or named mechanisms",
      "partial_points_when": "Mix of specific facts and generic claims",
      "zero_when": "Majority of content is generic marketing language"
    },
    {
      "id": "life_stage_explicit",
      "label": "Life stage explicit and accurate",
      "max_points": 10,
      "full_points_when": "Life stage stated correctly using AAFCO language (Adult, Puppy, Senior)",
      "partial_points_when": "Life stage present but ambiguous",
      "zero_when": "Life stage absent or incorrect"
    },
    {
      "id": "functional_ingredients_named",
      "label": "Functional ingredients named with benefit",
      "max_points": 15,
      "full_points_when": "3+ functional ingredients named with mechanism (e.g. 'L-Carnitine supports fat metabolism')",
      "partial_points_when": "1–2 functional ingredients named",
      "zero_when": "No functional ingredients named — generic benefit claims only"
    },
    {
      "id": "no_prohibited_superlatives",
      "label": "No prohibited superlatives",
      "max_points": 15,
      "full_points_when": "No prohibited superlatives anywhere in title, bullets, or description",
      "partial_points_when": "One prohibited superlative present",
      "zero_when": "Multiple prohibited superlatives present",
      "prohibited_terms": ["great tasting", "world's finest", "finest ingredients", "best", "amazing", "superior"]
    },
    {
      "id": "aafco_visible",
      "label": "AAFCO statement visible",
      "max_points": 10,
      "full_points_when": "AAFCO explicitly mentioned in bullets or description with life stage",
      "partial_points_when": "AAFCO referenced without life stage specificity",
      "zero_when": "AAFCO not mentioned in visible content"
    },
    {
      "id": "attribute_completeness",
      "label": "Attribute completeness",
      "max_points": 15,
      "key_attributes": ["life stage", "breed size", "primary protein", "grain inclusion", "pack size", "health benefit"],
      "full_points_when": "5–6 key attributes clearly stated",
      "partial_points_when": "3–4 attributes present",
      "zero_when": "Fewer than 3 attributes determinable"
    }
  ]
}
```

---

## `data/sparky_criteria.json`

```json
{
  "retailer": "Walmart",
  "ai_assistant": "Sparky",
  "behaviour_summary": "Sparky launched June 2025, live in Walmart app, ChatGPT, and Google Gemini. Rewards structured, attribute-complete listings. Prefers specific verifiable claims over narrative marketing.",
  "scoring_note": "Score each dimension and sum. Raw total out of 100 × 0.30 = contribution to overall score.",
  "scoring_dimensions": [
    {
      "id": "structured_attribute_completeness",
      "label": "Structured attribute completeness",
      "max_points": 35,
      "key_attributes": ["life stage", "breed size", "primary protein", "grain inclusion", "pack size", "flavour", "health benefit"],
      "full_points_when": "6–7 key attributes present and accurate",
      "partial_points_when": "3–5 attributes present",
      "zero_when": "Fewer than 3 attributes determinable"
    },
    {
      "id": "claim_specificity",
      "label": "Claim specificity and clarity",
      "max_points": 30,
      "full_points_when": "Claims are short, specific, and structured — concrete facts a shopper can act on",
      "partial_points_when": "Mix of specific and vague claims",
      "zero_when": "Majority of content is narrative marketing without specific facts"
    },
    {
      "id": "no_prohibited_superlatives",
      "label": "No prohibited superlatives",
      "max_points": 15,
      "full_points_when": "No prohibited superlatives",
      "partial_points_when": "One present",
      "zero_when": "Multiple present",
      "prohibited_terms": ["world's finest", "best", "great tasting", "amazing", "premium", "superior", "domestically crafted"]
    },
    {
      "id": "occasion_intent_relevance",
      "label": "Occasion and intent relevance",
      "max_points": 20,
      "full_points_when": "Content addresses 2+ shopper intents (sensitive stomach, large breed, weight management, active dogs)",
      "partial_points_when": "One intent signal present",
      "zero_when": "Generic content with no intent specificity"
    }
  ]
}
```
