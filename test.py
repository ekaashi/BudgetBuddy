#not necessary just for testing some functions

import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("ANTHROPIC_API_KEY"))
