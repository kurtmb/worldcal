from worldcal.schemas import ModelRecord

NOVA_MICRO = ModelRecord(
    id="nova-micro",
    provider="amazon",
    bedrock_model_id="us.amazon.nova-micro-v1:0",
    display_name="Amazon Nova Micro",
    seed_supported=False,
)

HAIKU_45 = ModelRecord(
    id="haiku-4.5",
    provider="anthropic",
    bedrock_model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    display_name="Claude Haiku 4.5",
    seed_supported=False,
)

FIRST_MODELS = {m.id: m for m in (NOVA_MICRO, HAIKU_45)}
