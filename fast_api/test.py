import os
import uvicorn
from fastapi import FastAPI,APIRouter, Request, Header
from sse_starlette import EventSourceResponse
from starlette.responses import JSONResponse
from msg.chat_messages import ChatMessages
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import json
from openai import OpenAI
from fastapi import HTTPException
from dotenv import load_dotenv, find_dotenv
import pyodbc
import pandas as pd


# 加载环境变量
load_dotenv(find_dotenv())

client = OpenAI()

instruction=""
output_format=""
examples=""
context="请给出下个月的康复计划。"
# 打开文件并读取内容到字符串
with open("./PromptFiles/instruction.txt", 'r', encoding='utf-8') as file:
    instruction = file.read()
with open("./PromptFiles/output_format.txt", 'r', encoding='utf-8') as file:
    output_format = file.read()
with open("./PromptFiles/examples.txt", 'r', encoding='utf-8') as file:
    examples = file.read()

prompt = f"""
{instruction}

输出格式要求：
{output_format}

上个月的计划和执行情况：
{examples}

输入：
{context}
"""

# 初始化 OpenAI 客户端
client = OpenAI()  # 默认使用环境变量中的 OPENAI_API_KEY 和 OPENAI_BASE_URL

# 基于 prompt 生成文本
def get_completion(prompt, model="gpt-3.5-turbo"):      # 默认使用 gpt-3.5-turbo 模型
    messages = [{"role": "user", "content": prompt}]    # 将 prompt 作为用户输入
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,                                  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content          # 返回模型生成的文本

# # 调用大模型
# response = get_completion(prompt)
# print(response)

data = json.loads(examples)
print(data["月计划标题"])