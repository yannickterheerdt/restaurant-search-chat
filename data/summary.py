from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import RateLimitError
import os
import time
from config import settings
from typing import Iterable, List

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

def splicegen(maxchars: int, texts: List[str]) -> Iterable[List[int]]:
    """
    Splits a list of strings into sublists where the cumulative character length
    of each sublist does not exceed maxchars.

    Args:
        maxchars (int): Maximum number of characters allowed per sublist.
        texts (List[str]): List of strings to be chunked.

    Yields:
        List[int]: A list of indices representing each chunk within texts.
    """
    current_length = 0  
    index_chunk = []  
    
    for i, item in enumerate(texts):
        current_length += len(item)
        if current_length < maxchars:
            index_chunk.append(i)
        else:
            yield index_chunk
            index_chunk = [i]
            current_length = len(item)
    
    if index_chunk:
        yield index_chunk

def generate_summaries(texts: List[str], max_retries: int = 6, delay: int = 10) -> List[str]:
    """
    Generates summaries for a list of texts using OpenAI's language model, with retry logic for rate limiting.

    Args:
        texts (List[str]): List of strings to summarize.
        max_retries (int): Maximum number of retries on rate limiting.
        delay (int): Initial delay between retries, in seconds.

    Returns:
        List[str]: Summarized text for each input string.

    Raises:
        Exception: If the maximum number of retries is exceeded.
    """
    # Create prompt and model pipeline
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", settings.PROMPT_SUMMARY_TEMPLATE), ("user", "{content}")]
    )
    model = ChatOpenAI(model=settings.OPENAI_ENGINE, temperature=0)
    chain = prompt_template | model | StrOutputParser()

    attempt = 0
    while attempt < max_retries:
        try:
            return chain.batch(texts)

        except RateLimitError as e:
            attempt += 1
            time.sleep(delay)
    
    raise Exception(f"Failed to generate summaries after {max_retries} attempts due to rate limit.")
