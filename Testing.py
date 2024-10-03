import os
import json
import csv
import asyncio
import logging
from datetime import datetime
import aiohttp
import html
from asyncio import Semaphore
import sys  


# Configure logging
log_filename = f"log_generate_answers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),  # set code to utf-8
        logging.StreamHandler(sys.stdout)  # use sys.stdout to supoort utf-8
    ]
)

# Configuration
CONFIG = {
    # Testing LLM configuration (OpenAI API)

    "TESTING_LLM_MODEL": ["gpt-4o-2024-08-06"], 
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),  # OpenAI API KEY
    "OPENAI_API_URL": "https://api.openai.com/v1/chat/completions",# or replace with 3rd party URL

    "QUESTION_FILE": os.path.join("dataset", "newtasks.json"),
    "OUTPUT_CSV": f"answers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",

    # Concurrency settings
    "MAX_CONCURRENT_QUESTIONS": 3,  
    "MAX_CONCURRENT_MODELS": 4,     
    "MAX_CONCURRENT_API_CALLS": 12, 

    # Prompts
    "TESTING_PROMPT": """You are a highly knowledgeable expert in cryptography and blockchain technology. Please provide a clear and accurate answer to the following question.

**Question:**
{question}

**Instructions:**

- **Direct Answer:** Begin with a direct response to the question.
- **Essential Explanation:** Provide a brief explanation if necessary.
- **Clarity:** Ensure your answer is understandable and uses appropriate terminology.
- **Conciseness:** Keep your response focused and avoid unnecessary details.

**Goal:** Deliver a high-quality answer that demonstrates your expertise while being concise.
""",

    "AUDITING_PROMPT": """You are an expert smart contract auditor specializing in blockchain security. Analyze the following smart contract code and provide your findings.

**Tasks:**

1. **Identify Security Vulnerabilities:**
   - Point out any potential security issues.

2. **Exploitation Scenarios:**
   - Briefly explain how each vulnerability could be exploited.

3. **Recommendations:**
   - Suggest fixes to improve security.

**Contract Code:**
{code}

**Instructions:**
- **Identify Security Vulnerabilities:** Analyze the code thoroughly to uncover all potential security issues
- **Focus on Critical Issues:** Prioritize the most significant vulnerabilities.
- **Clarity and Conciseness:** Present your analysis clearly and succinctly.
- **Professional Tone:** Use appropriate technical terms.

**Goal:** Provide a concise audit report that helps improve the contract's security.
    
""",

    "CODING_PROMPT": """You are a skilled blockchain developer with expertise in smart contract development. Please provide a complete and functional smart contract implementation for the following problem.

**Problem Statement:**
{question}

**Instructions:**

- **Complete Smart Contract:** Provide a fully functional smart contract written in Solidity (or the relevant programming language) that solves the problem.
- **Code Clarity:** Ensure the code is well-organized, readable, and follows best practices for smart contract development.
- **Comments:** Include comments where necessary to explain complex sections of the code.
- **Security Best Practices:** Implement security measures to protect against common vulnerabilities.
- **Efficiency:** Optimize the code for performance and gas efficiency where possible.

**Goal:** Deliver a precise and secure smart contract solution that fully addresses the problem requirements.
"""
}

# Create semaphores for concurrency
API_SEMAPHORE = Semaphore(CONFIG["MAX_CONCURRENT_API_CALLS"])
QUESTION_SEMAPHORE = Semaphore(CONFIG["MAX_CONCURRENT_QUESTIONS"])
MODEL_SEMAPHORE = Semaphore(CONFIG["MAX_CONCURRENT_MODELS"])

async def load_questions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            questions = json.load(file)
        logging.info(f"Successfully loaded {len(questions)} questions from {file_path}")
        return questions
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error in {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
    return []

async def call_openai_api(session, model, messages, max_retries=6, delay=8):
    async with API_SEMAPHORE:
        for attempt in range(max_retries):
            try:
                async with session.post(
                    CONFIG["OPENAI_API_URL"],
                    headers={
                        "Authorization": f"Bearer {CONFIG['OPENAI_API_KEY']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens":4096,
                        "temperature": 0
                    },
                    timeout=500
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "choices" in data and data["choices"]:
                            return data["choices"][0]["message"]["content"].strip()
                        else:
                            raise ValueError(f"Unexpected API response format: {data}")
                    elif response.status == 429:
                        logging.warning(f"Rate limit hit, retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        error_detail = await response.text()
                        raise ValueError(f"API call failed with status {response.status}: {error_detail}")
            except Exception as e:
                logging.error(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(delay)
    return None

async def generate_answer(session, question_data):
    tasks = []
    for model in CONFIG["TESTING_LLM_MODEL"]:
        task = asyncio.create_task(generate_single_answer_with_semaphore(session, question_data, model))
        tasks.append(task)
    
    answers = await asyncio.gather(*tasks)
    return answers


async def generate_single_answer_with_semaphore(session, question_data, model):
    async with MODEL_SEMAPHORE:
        if question_data.get("category") == "auditing":
            code = question_data.get('code') or "Code is included in the question."
            prompt = CONFIG["AUDITING_PROMPT"].format(
                code=code
            )
        elif question_data.get("category") == "coding":
            prompt = CONFIG["CODING_PROMPT"].format(
                question=question_data['question']
            )
        else:
            prompt = CONFIG["TESTING_PROMPT"].format(question=question_data['question'])

        messages = [
            {"role": "system", "content": "You are a helpful assistant specialized in blockchain and smart contract security."},
            {"role": "user", "content": prompt.strip()}
        ]

        answer = await call_openai_api(session, model, messages)
        return {"model": model, "answer": answer}

def escape_special_chars(text):
    """Escape special characters in the text."""
    return html.escape(text).replace('\n', '\\n').replace('\r', '\\r')

async def process_questions(questions):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for question in questions:
            task = asyncio.create_task(process_single_question_with_semaphore(session, question))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    return [item for sublist in results for item in sublist]

async def process_single_question_with_semaphore(session, question_data):
    async with QUESTION_SEMAPHORE:
        return await process_single_question(session, question_data)

async def process_single_question(session, question_data):
    start_time = asyncio.get_event_loop().time()
    logging.info(f"Started processing Question {question_data.get('id', '')} at {start_time}")
    
    llm_answers = await generate_answer(session, question_data)

    results = []
    for llm_result in llm_answers:
        model = llm_result["model"]
        llm_answer = llm_result["answer"]
        
        if llm_answer:
            logging.info(f"Generated Answer from {model}:\n{llm_answer}\n")
        else:
            logging.warning(f"Failed to generate an answer from {model}.")
            llm_answer = "No answer generated."

        result = {
            "Question ID": question_data.get("id", ""),
            "Model": model,
            "Question": escape_special_chars(question_data.get("question", "")),
            "Code": escape_special_chars(question_data.get("code", "")),
            "Standard Answer": escape_special_chars(question_data.get("answer", "")),
            "LLM Answer": escape_special_chars(llm_answer),
            "Category": question_data.get("category", ""),
            "Topics": ", ".join(question_data.get("topic", []))
        }
        results.append(result)

    end_time = asyncio.get_event_loop().time()
    logging.info(f"Finished processing Question {question_data.get('id', '')} at {end_time}. Took {end_time - start_time} seconds.")
    return results

def save_results_to_csv(results, filename):
    fieldnames = [
        "Question ID", "Model", "Category", "Topics",
        "Question", "Code", "Standard Answer", "LLM Answer"
    ]
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for result in results:
            # Unescape the special characters for writing to CSV
            for field in ["Question", "Code", "Standard Answer", "LLM Answer"]:
                if field in result:
                    result[field] = html.unescape(result[field]).replace('\\n', '\n').replace('\\r', '\r')
            writer.writerow(result)
    logging.info(f"Results have been saved to {filename}")

async def main():
    try:
        questions = await load_questions(CONFIG["QUESTION_FILE"])
        if not questions:
            logging.error("No questions loaded, exiting.")
            return

        results = await process_questions(questions)

        # Save results to CSV
        save_results_to_csv(results, CONFIG["OUTPUT_CSV"])

        logging.info("\nAll processes completed successfully.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        import traceback
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
