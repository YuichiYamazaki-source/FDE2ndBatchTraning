from agents import Agent, Runner, InputGuardrail, OutputGuardrail, GuardrailFunctionOutput

from ai_agents.tools import (
    analyze_reviews,
    get_product,
    recommend_alternatives,
    search_products,
)

INSTRUCTIONS = """
You are a helpful e-commerce product assistant for an online store.

You have access to four tools:
- search_products: find products using natural language queries
- get_product: retrieve full details for a specific product by ID
- analyze_reviews: fetch and analyze customer reviews for a product
- recommend_alternatives: suggest better-rated products in the same category

Behaviour guidelines:
- When asked about a specific product (product ID provided), use get_product first.
- When asked "is this product good?" or similar, call analyze_reviews, summarize
  positives and negatives, and state an overall verdict.
- If a product rating is poor (< 3.5) or the user asks for alternatives, call
  recommend_alternatives with the product's category and a min_rating of 4.0.
- When no product ID is given, use search_products to find relevant items.
- Keep responses concise and helpful. Do not expose raw JSON.
- When responding about a specific product, always include its product ID
  (e.g. "Product 430528189: Exultantex Grey Blackout Curtains").
""".strip()


# ===================================================================
# Guardrails
# ===================================================================

# --- 禁止キーワード ---
BLOCKED_INPUT_KEYWORDS = [
    "ignore previous instructions",
    "system prompt",
    "you are now",
    "disregard",
    "override",
]

BLOCKED_OUTPUT_KEYWORDS = [
    "OPENAI_API_KEY",
    "sk-",
    "password",
    "secret_key",
]


async def input_guardrail_fn(ctx, agent, input_data):
    """Input Guardrail: プロンプトインジェクション等の不正入力を検出する。"""
    # input_data は str or list — str に正規化
    if isinstance(input_data, str):
        text = input_data
    elif isinstance(input_data, list):
        text = " ".join(
            item.get("content", "") if isinstance(item, dict) else str(item)
            for item in input_data
        )
    else:
        text = str(input_data)

    text_lower = text.lower()
    for keyword in BLOCKED_INPUT_KEYWORDS:
        if keyword in text_lower:
            return GuardrailFunctionOutput(
                output_info={"blocked_keyword": keyword, "input_preview": text[:100]},
                tripwire_triggered=True,
            )

    return GuardrailFunctionOutput(
        output_info={"status": "passed"},
        tripwire_triggered=False,
    )


async def output_guardrail_fn(ctx, agent, output_data):
    """Output Guardrail: 機密情報やAPIキーの漏洩を検出する。"""
    text = str(output_data).lower() if output_data else ""

    for keyword in BLOCKED_OUTPUT_KEYWORDS:
        if keyword.lower() in text:
            return GuardrailFunctionOutput(
                output_info={"blocked_keyword": keyword, "output_preview": text[:100]},
                tripwire_triggered=True,
            )

    return GuardrailFunctionOutput(
        output_info={"status": "passed"},
        tripwire_triggered=False,
    )


# ===================================================================
# Agent 定義
# ===================================================================

_orchestrator = Agent(
    name="Orchestrator",
    model="gpt-4o-mini",
    instructions=INSTRUCTIONS,
    tools=[search_products, get_product, analyze_reviews, recommend_alternatives],
    input_guardrails=[
        InputGuardrail(guardrail_function=input_guardrail_fn, name="injection_detector"),
    ],
    output_guardrails=[
        OutputGuardrail(guardrail_function=output_guardrail_fn, name="secret_leak_detector"),
    ],
)


async def run_orchestrator(message: str, product_id: str | None = None) -> str:
    """Run the Orchestrator Agent and return its final text response."""
    if product_id:
        user_input = f"[Context: product_id={product_id}]\n\n{message}"
    else:
        user_input = message

    result = await Runner.run(_orchestrator, input=user_input)
    return result.final_output
