import os
import json
import re
import csv
import asyncio
import aiohttp
import logging
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# Configure logging
log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# Configuration
CONFIG = {
    "OPENAI_API_URL": "https://api.openai.com/v1/chat/completions",
    "MODELS": [
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09",
        "gpt-3.5-turbo-0125"
    ],
    "API_KEY": os.getenv("OPENAI_API_KEY"),  # Load API key from environment variable
    "TEST_RUNS": 1, # testrun number for each model
    "QUESTION_FILES": [os.path.join("dataset", "MultichoiceQuestions.json")], # can be adjusted based on actual enviorment
    "PROMPTS": [
        "You are an expert in cryptography and blockchain field, Please think carefully and answer the following question by providing only the letter of the correct option (A, B, C, or D). Your response should include no explanation, but ensure you consider all the options before selecting an answer.\n\nThe response should be a JSON object containing the following fields: 'answer': Your chosen answer (A, B, C, or D) . Please ensure your response is in valid JSON format. Here is an example { \"answer\": \"A\"}\nNow, let's look at the question:\n"
    #Output Json format to reduce uncertainty
    ]
}

async def load_questions(file_paths):
    all_questions = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                questions = json.load(file)
                all_questions.extend([(file_path, q) for q in questions])
            logging.info(f"Successfully loaded {len(questions)} questions from {file_path}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error in {file_path}: {e}")
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
    return all_questions

async def call_openai_api(session, question, model, prompt, max_retries=3, delay=5):
    full_prompt = f"{prompt}\n{question}"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": ""},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 10, # depends on the type of question and the output characteristics of different models, and needs to be adjusted flexibly
        "temperature": 0  # Ensure deterministic output
    }
    headers = {
        "Authorization": f"Bearer {CONFIG['API_KEY']}",
        "Content-Type": "application/json"
    }

    for attempt in range(max_retries):
        try:
            async with session.post(
                CONFIG["OPENAI_API_URL"],
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "choices" in data and data["choices"]:
                        return data["choices"][0]["message"]["content"].strip().upper()
                    else:
                        raise ValueError(f"Unexpected API response format: {data}")
                elif response.status == 429:
                    logging.warning(f"Rate limit hit, retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    error_detail = await response.text()
                    logging.error(f"API call failed with status {response.status}: {error_detail}")
        except Exception as e:
            logging.error(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                logging.error("Max retries reached. Skipping this question.")
    return None

def compare_answers(llm_answer, correct_answer):
    correct_answer = correct_answer.strip().upper()
    answer = llm_answer.strip().upper()

    # Define regex patterns to match various possible responses
    patterns = [
        r'^\s*([A-D])\s*$',                                    # Single letter responses
        r'\bTHE\s+CORRECT\s+ANSWER\s*(?:IS\s*|:?\s*)([A-D])\b', # "The correct answer is D"
        r'\bANSWER\s*(?:IS\s*|:?\s*)([A-D])\b',                 # "Answer is C", "Answer: C"
        r'\bI\s*CHOOSE\s*([A-D])\b',                            # "I choose B"
        r'\bMY\s*ANSWER\s*(?:IS\s*|:?\s*)([A-D])\b',            # "My answer is D"
        r'\bOPTION\s*([A-D])\b',                                # "Option C"
        r'\b([A-D])[.)\s]',                                     # "C)", "B.", "A "
        r'\b([A-D])\b'                                          # Any standalone A-D
    ]

    llm_answer_clean = ''
    for pattern in patterns:
        match = re.search(pattern, answer)
        if match:
            llm_answer_clean = match.group(1)
            break  # Stop at the first successful match

    # Check for multiple unique options to detect ambiguity
    all_matches = re.findall(r'\b[A-D]\b', answer)
    unique_matches = set(all_matches)

    if len(unique_matches) == 1 and llm_answer_clean == correct_answer:
        return 1
    else:
        return 0


async def run_test_for_model_and_prompt(all_questions, model, prompt):
    async with aiohttp.ClientSession() as session:
        all_scores = []
        for run in range(1, CONFIG["TEST_RUNS"] + 1):
            logging.info(f"\nRun {run} for model: {model}, prompt: {prompt[:30]}...")
            scores = []
            for i, (file_path, q) in enumerate(all_questions, 1):
                try:
                    llm_answer = await call_openai_api(session, q["question"], model, prompt)
                    if llm_answer:
                        score = compare_answers(llm_answer, q["answer"])
                        scores.append((file_path, q.get("categories", []), score))
                        logging.info(f"Q{i}: File: {os.path.basename(file_path)}, Answer: {llm_answer}, Correct: {q['answer']}, Score: {score}")
                    else:
                        scores.append((file_path, q.get("categories", []), 0))
                        logging.warning(f"Q{i}: File: {os.path.basename(file_path)}, Failed to get answer")
                except Exception as e:
                    logging.error(f"Error processing question {i}: {e}")
                    scores.append((file_path, q.get("categories", []), 0))
            all_scores.append(scores)
            accuracy = sum(score for _, _, score in scores) / len(scores) * 100
            logging.info(f"Run {run} - Accuracy: {accuracy:.2f}%")
        return all_scores

def generate_csv_report(all_results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'model_performance_{timestamp}.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write header
        header = ['Model', 'Prompt', 'Run', 'Question File', 'Question Number', 'Categories', 'Score']
        csvwriter.writerow(header)

        # Write results for each question
        for (model, prompt), runs in all_results.items():
            for run_index, run in enumerate(runs, 1):
                for i, (file_path, categories, score) in enumerate(run):
                    row = [
                        model,
                        prompt[:30],
                        run_index,
                        os.path.basename(file_path),
                        i + 1,
                        ', '.join(categories) if categories else 'N/A',
                        score
                    ]
                    csvwriter.writerow(row)

    logging.info(f"Results have been saved to {filename}")

async def main():
    try:
        all_questions = await load_questions(CONFIG["QUESTION_FILES"])
        if not all_questions:
            logging.error("No questions loaded, exiting")
            return

        all_results = {}

        for model in CONFIG["MODELS"]:
            for prompt in CONFIG["PROMPTS"]:
                logging.info(f"\nTesting model: {model} with prompt: {prompt[:30]}...")
                all_results[(model, prompt)] = await run_test_for_model_and_prompt(all_questions, model, prompt)

        # Generate detailed CSV report
        generate_csv_report(all_results)

        logging.info("\nResults have been saved to CSV.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
