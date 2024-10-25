from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import RateLimitError
import os
import time
from config import settings
from typing import Iterable

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

def splicegen(maxchars: int, stringlist: list[str]) -> Iterable[list[int]]:
    runningcount = 0  
    tmpslice = []  
    for i, item in enumerate(stringlist):
        runningcount += len(item)
        if runningcount < maxchars:
            tmpslice.append(i)
        else:
            yield tmpslice
            tmpslice = [i]
            runningcount = len(item)
    yield tmpslice

def generate_summaries(texts: list[str], max_retries: int = 6, delay: int = 10) -> list[str]:
    model = settings.OPENAI_ENGINE
    promp_template = ChatPromptTemplate.from_messages(
        [("system", settings.PROMPT_SUMMARY_TEMPLATE), ("user", "{content}")]
    )
    model = ChatOpenAI(model=model, temperature=0)
    chain = promp_template | model | StrOutputParser()

    attempt = 0
    while attempt < max_retries:
        try:
            return chain.batch(texts)

        except RateLimitError as e:
            attempt += 1
            time.sleep(delay)
    
    raise Exception(f"Failed to generate summaries after {max_retries} attempts due to rate limit.")
