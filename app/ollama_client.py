import base64
import os

import ollama


class OllamaClient:
    """
    TODO: write doc comment

    See Also:
    - https://github.com/ollama/ollama-python
    """

    def __init__(self, host_url, model, headers):
        self.client = ollama.AsyncClient(host=host_url, headers=headers)
        self.model = model

    def from_env():
        url = os.getenv("OLLAMA_URL")
        model = os.getenv("OLLAMA_MODEL")
        auth_user = os.getenv("OLLAMA_AUTH_USER")
        auth_pass = os.getenv("OLLAMA_AUTH_PASS")

        headers = {
            "Authorization": generate_auth_header(auth_user, auth_pass)
        }

        return OllamaClient(url, model, headers)

    async def preload(self):
        self.client.chat(model=self.model)

    async def chat(self, messages):
        response = await self.client.chat(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            stream=False,
        )
        return response["message"]["content"]


def generate_auth_header(username, password):
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    auth_header = f"Basic {encoded_credentials}"
    return auth_header
