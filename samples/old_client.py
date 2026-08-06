from square.client import LegacySquare

client = LegacySquare(

    access_token="TOKEN",

    custom_url="https://sandbox.example.com",

    square_version="2024-01-01",

    environment="sandbox",

    http_call_back=None,

    user_agent_detail="Research Prototype"
)
