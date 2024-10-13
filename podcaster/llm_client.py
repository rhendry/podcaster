from abc import ABC, abstractmethod
from openai import AsyncClient
from pydantic import BaseModel
from typing import TypeVar, Type

T = TypeVar('T', bound=BaseModel)

class LLMClient(ABC):
    @abstractmethod
    async def generate_text_async(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_model_async(self, prompt: str, model_type: Type[T]) -> T:
        pass

class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo'):
        self.api_key = api_key
        self.model = model
        self.client = AsyncClient(api_key=self.api_key)

    async def generate_text_async(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        if response.choices[0].message.content is None:
            raise Exception("No content returned from the LLM")

        return response.choices[0].message.content

    async def generate_model_async(self, prompt: str, model_type: Type[T]) -> T:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            functions=[{
                "name": "generate_model",
                "description": "Generate a pydantic model",
                "parameters": model_type.model_json_schema()
            }],
            function_call={"name": "generate_model"}
        )

        if response.choices[0].message.function_call is None:
            raise Exception("No function call returned from the LLM")

        if response.choices[0].message.function_call.arguments is None:
            raise Exception("No arguments returned from the LLM")

        return model_type.model_validate_json(response.choices[0].message.function_call.arguments)
