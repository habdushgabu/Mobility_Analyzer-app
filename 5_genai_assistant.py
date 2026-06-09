import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_groq_api_key() -> str | None:
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key

    try:
        import streamlit as st

        return st.secrets.get("GROQ_API_KEY")
    except Exception:
        return None


def ask_groq(prompt: str) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        return "GROQ_API_KEY is not configured. Add it in Streamlit secrets or your local .env file."

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise urban mobility analytics assistant. Answer using the current taxi analytics context and mention if the data is based on generated project outputs.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        return f"GenAI request failed: {exc}"


def main():
    print("GenAI assistant is configured for GROQ.")
    query = input("Ask a question about your mobility dataset: ")
    print(ask_groq(query))


if __name__ == "__main__":
    main()
