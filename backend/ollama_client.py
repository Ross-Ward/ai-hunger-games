import ollama
import asyncio

class OllamaClient:
    def __init__(self, model="llama3"):
        self.model = model

    async def generate(self, prompt, system_prompt=None):
        try:
            # Ollama python library is synchronous by default, but we can run it in a thread or use its async client if available.
            # For simplicity in this prototype, we'll wrap the sync call or use the async client if the library supports it.
            # Checking docs: ollama-python has an AsyncClient.
            
            client = ollama.AsyncClient()
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            response = await client.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error: {e}"

    async def list_models(self):
        client = ollama.AsyncClient()
        return await client.list()
