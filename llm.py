# --------------------------- STAGE 1: IMPORT REQUIRED MODULES ---------------------------
import os
import json
import logging
import requests
from dotenv import load_dotenv
from utils import load_faq_data, find_best_faq_match

# --------------------------- STAGE 2: LOAD ENVIRONMENT VARIABLES ---------------------------
load_dotenv()

# --------------------------- STAGE 3: SETUP LOGGING CONFIGURATION ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --------------------------- STAGE 4: MAIN CUSTOMER SUPPORT CLASS ---------------------------
class CustomerSupportAssistant:
    def __init__(self, api_key=None, history_file="chat_history.json", faq_file="faq_data.json"):
        """
        Initialize the chatbot with API key, model settings, and files for chat history & FAQ.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in .env as GROQ_API_KEY")

        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.model = "deepseek-r1-distill-llama-70b"
        self.max_input_length = 700
        self.history_file = history_file

        self.chat_history = self.load_chat_history()
        self.faq_data = load_faq_data(faq_file)

    def load_chat_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load chat history: {e}")
        return []

    def save_chat_history(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.chat_history, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save chat history: {e}")

    def preprocess_input(self, user_query):
        if len(user_query) > self.max_input_length:
            logging.warning("Trimming long input")
            user_query = user_query[:self.max_input_length]
        return user_query.strip()

    def get_response(self, user_query):
        user_query = self.preprocess_input(user_query)
        self.chat_history.append({"role": "user", "content": user_query})

        # Step 1: Try FAQ
        faq_answer = find_best_faq_match(user_query, self.faq_data)
        if faq_answer:
            self.chat_history.append({"role": "assistant", "content": faq_answer})
            self.save_chat_history()
            return faq_answer

        # Step 2: LLM fallback
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": (
                    "You are a financial customer support assistant for a bank app. "
                    "Answer the user professionally, clearly, and concisely. "
                    "Do not explain your reasoning or think out loud. "
                    "Keep replies under 100 words. Avoid markdown and internal thoughts."
                )}
            ] + self.chat_history,
            "max_tokens": 300,
            "temperature": 0.2
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"].strip()
            self.chat_history.append({"role": "assistant", "content": reply})
            self.save_chat_history()
            return reply

        except requests.exceptions.RequestException as e:
            logging.error(f"API Error: {e}")
            return "Sorry, I couldn't reach the server."
        except KeyError:
            logging.error("Unexpected response structure.")
            return "Error processing the response."

    def clear_history(self):
        self.chat_history = []
        self.save_chat_history()

# --------------------------- STAGE 5: RUNNING AS CLI CHAT TOOL ---------------------------
def main():
    from getpass import getpass

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = getpass("Enter your Groq API key: ")

    assistant = CustomerSupportAssistant(api_key)

    print("Welcome to your Banking Support Assistant (CLI)")
    print("Type 'exit' to quit or 'clear' to reset chat history.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break
        elif user_input.lower() == "clear":
            assistant.clear_history()
            continue
        elif not user_input:
            continue

        reply = assistant.get_response(user_input)
        print(f"Assistant: {reply}\n")

# --------------------------- STAGE 6: ENTRY POINT ---------------------------
if __name__ == "__main__":
    main()
