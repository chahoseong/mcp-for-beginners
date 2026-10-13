"""Generate credentials for the local learning services without printing them."""

from pathlib import Path
import secrets

path = Path(__file__).resolve().parent / ".env"
if path.exists():
    print("Existing .env kept; credentials were not changed.")
else:
    path.write_text(
        "PRACTICE_CLIENT_ID=quote-client\n"
        f"PRACTICE_CLIENT_SECRET={secrets.token_urlsafe(32)}\n"
        "PRACTICE_VERIFIER_ID=quote-server\n"
        f"PRACTICE_VERIFIER_SECRET={secrets.token_urlsafe(32)}\n",
        encoding="utf-8",
    )
    print("Local .env created. Credential values were not printed.")
