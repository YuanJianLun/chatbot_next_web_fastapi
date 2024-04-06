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
from langchain_core.prompts.string import (
    DEFAULT_FORMATTER_MAPPING,
    StringPromptTemplate,
    check_valid_template,
    get_template_variables,
)
from test import get_completion,prompt,examples

# 数据库连接参数
server = '.'  # 服务器名称或IP地址
database = 'adms706_test'  # 数据库名称
username = 'sa'  # 数据库用户名
password = '58286008'  # 数据库密码
driver = '{ODBC Driver 17 for SQL Server}'  # 根据你的ODBC驱动版本进行修改

# 创建连接字符串
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# 初始化 FastAPI 应用实例
# app = APIRouter()
app = FastAPI(default_response_class=JSONResponse, default_encoding="utf-8")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载环境变量
load_dotenv(find_dotenv())

client = OpenAI()

messages = [
    {
        "role": "user",
        "content": "你是谁？"  # 问问题。可以改改试试
    },
]


# 指定txt文件路径
file_path = "path/to/your/file.txt"
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

@app.post("/v1/chat/completions")
async def completions(request: Request, authorization: str = Header(None)):
    chat_message = ChatMessages(data=await request.json())

    print(chat_message.messages)
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_message.messages,
            stream=True)
              
    return response.choices[0].message.content          # 返回模型生成的文本

@app.get("/v1/chat/get_result1")
def get_result1(input: str):
    print(input)
    # 建立连接
    try:
        conn = pyodbc.connect(conn_str)
        print("Connected to the database successfully.")

        # 创建游标对象
        cursor = conn.cursor()

        # 执行SQL查询
        query = "SELECT top 2 student_name,teacher FROM a_iep_month_plan"  # 替换为你的查询语句和表名
        cursor.execute(query)

        # 获取查询结果
        rows = cursor.fetchall()

        # 使用 cursor.description 获取所有列名
        columns=[description[0] for description in cursor.description]
        print(columns)

       # 创建一个空列表，用于存储每个查询结果的字典
        results_list = []

        # 遍历每一行结果，创建字典并添加到列表中
        for row in rows:
            # 使用列名作为键，结果值作为值创建字典
            row_dict = dict(zip(columns, row))
            results_list.append(row_dict)

        #print(df)

        print(results_list)
        return {'rows':results_list}
    except Exception as e:
        print("An error occurred:", e)

    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    return "OK"

@app.get("/v1/chat/get_result")
def get_result(input: str):
    # # 调用大模型
    # response = get_completion(prompt)
    # print(response)
    data = json.loads(examples)
    return {'rows':data}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3003,
                reload=True)
