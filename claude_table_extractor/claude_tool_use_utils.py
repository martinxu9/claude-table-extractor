import base64

from anthropic import Anthropic

client = Anthropic()

MAX_TOKENS = 4096
MODEL_NAME = "claude-3-haiku-20240307"
TOOLS = [
    {
        "name": "extract_table",
        "description": "Extract table as list of lists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tables": {
                    "type": "object",
                    "description": "The extracted table as a list of lists.",
                },
            },
            "required": ["tables"],
        },
    }
]


QUERY_TEXT = """Extract the first table in the image as a list of lists including empty cells. For null or empty cells, always use empty strings. Use the extract_table tool."""


def parse_table_plain_text(plain_text: str) -> list[list[str]]:
    try:
        return eval(plain_text.replace("\n", ""))
    except Exception as ex:
        print(ex)
        return []


def extract_table_as_json_from_image(
    image_data: str, image_media_type: str
) -> list[list[str]]:
    response = client.beta.tools.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        tools=TOOLS,  # type: ignore
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_data,
                        },
                    },  # type: ignore
                    {
                        "type": "text",
                        "text": QUERY_TEXT,
                    },
                ],
            }
        ],
    )

    for content in response.content:
        if content.type == "tool_use" and content.name == "extract_table":
            # print(content.input)
            # Workaround: seems it does not return json encoded string
            return parse_table_plain_text(content.input.get("tables", "[]"))

    return []
