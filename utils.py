
import json                # Used for loading the FAQ data stored in a JSON file
import logging             # Used to log errors, warnings, and debug information
from difflib import SequenceMatcher  # Used to calculate similarity between strings (user question vs. FAQ question)


# === Function to Load FAQ Data ===

def load_faq_data(faq_file):
    """
    Loads FAQ data from a JSON file.
    
    Parameters:
        faq_file (str): Path to the JSON file containing FAQ data.
    
    Returns:
        list: A list of dictionaries with 'question' and 'answer' fields if successful.
              Returns an empty list if loading fails.
    """
    try:
        with open(faq_file, "r") as f:
            return json.load(f)  # Load and return JSON data as Python list/dict
    except Exception as e:
        logging.error(f"Failed to load FAQ data: {e}")  # Log any error that occurs while opening or parsing
        return []


# === Function to Match User Query to FAQ ===

def find_best_faq_match(user_query, faq_data, threshold=0.7):
    """
    Finds the best matching FAQ answer based on the user's question.

    Parameters:
        user_query (str): The question asked by the user.
        faq_data (list): List of FAQ entries loaded from the JSON file.
        threshold (float): Minimum similarity score (0 to 1) required to accept a match.
    
    Returns:
        str or None: The best matching answer if score exceeds threshold; otherwise, None.
    """
    best_match = None           # Holds the answer with the best match
    highest_score = 0.0         # Highest similarity score found
    user_query = user_query.lower()  # Convert user input to lowercase for fair comparison

    # Loop through all FAQ entries and compute similarity score
    for faq in faq_data:
        faq_question = faq["question"].lower()
        score = SequenceMatcher(None, user_query, faq_question).ratio()  # Compute string similarity

        # Optional: log debug scores for each comparison
        logging.debug(f"Matching '{user_query}' with '{faq_question}' => Score: {score}")

        # Update best match if this FAQ has the highest score so far
        if score > highest_score:
            highest_score = score
            best_match = faq["answer"]

    # Return the match if it exceeds the similarity threshold
    if highest_score >= threshold:
        logging.info(f"FAQ match found with score: {highest_score}")
        return best_match
    else:
        logging.info("No suitable FAQ match found.")
        return None
