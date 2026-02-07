import os
from huggingface_hub import InferenceClient

token = os.getenv("HF_TOKEN")

client = InferenceClient(
    model="tiiuae/falcon-7b-instruct",
    token=token
)

def ask_llm(user_text):
    response = client.text_generation(
        prompt=user_text,
        max_new_tokens=200,
        temperature=0.7
    )
    return response


if __name__ == "__main__":
    print(ask_llm("Suggest a 2 day budget trip to Jaipur"))
