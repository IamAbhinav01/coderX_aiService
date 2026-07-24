import os
import json
from groq import Groq
from config.serverConfig import ServerConfig

# client = Groq(
#     api_key=ServerConfig()["GROQ_API_KEY"],
# )

groq = Groq()

response = groq.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "Extract product review information from the text."},
        {
            "role": "user",
            "content": "I bought the UltraSound Headphones last week and I'm really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I'd give it 4.5 out of 5 stars.",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "product_review",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "rating": {"type": "number"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral"]
                    },
                    "key_features": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["product_name", "rating", "sentiment", "key_features"],
                "additionalProperties": False
            }
        }
    }
)

result =json.loads(response.choices[0].message.content or "{}")
print(json.dumps(result,indent=2))