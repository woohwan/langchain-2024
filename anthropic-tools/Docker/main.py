from typing import Union
from fastapi import FastAPI
from fit_tools import time_tool_user
import datetime
import json

app = FastAPI()

@app.get("/")
async def read_root():
  return {"Hello": "World"}

@app.post("/chat")
async def chat(user_input: str):
  accountId = "532805286864"
  token = "C6B31F50687372B1491EE08607087F45"

  year = datetime.date.today().year
  month = datetime.date.today().month
  day = datetime.date.today().day

  prompt = f"""accountId는 {accountId} 이고, token은 {token}입니다, 
            start_month와 end_month format은 '%Y%m'입니다.
            오늘은 {year}년 {month}월 {day}일 입니다. 
            year 정보가 부족할 경우 <year></year>사이의 정보를 사용하세요
            <year>{year}</year>
            month 정보가 하나일 경우, start_month와 end_month는 동일합니다.
            지난 달의 의미 previous month 이고, 작년의 의미는 year-1 입니다.
            답변 시 반드시 한국어를 사용하고 계정(account) 정보는 사용하지 마세요.
            {user_input}"""
  
  messages = [ {'role': 'user', 'content': prompt}]
  completions = time_tool_user.use_tools(messages, execution_mode="automatic")
  print(completions)
  return json.dumps({
    "output": completions
  })