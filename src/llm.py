from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings

import os
os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

def generate_summaries(texts: list[str]) -> list[str]:
    model = settings.OPENAI_ENGINE
    promp_template = ChatPromptTemplate.from_messages(
        [("system", settings.PROMPT_SUMMARY_TEMPLATE), ("user", "{content}")]
    )
    model = ChatOpenAI(model=model, temperature=0)
    chain = promp_template | model | StrOutputParser()

    return chain.batch(texts)
