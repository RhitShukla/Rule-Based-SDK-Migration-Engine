from square.client import Square
from square.environment import SquareEnvironment

client = Square(

    token="TOKEN",

    base_url="https://sandbox.example.com",

    version="2024-01-01",

    environment=SquareEnvironment.SANDBOX
)
