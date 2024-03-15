from fit_tools import UsageOfAmount

tool_name = "get_amount_of_usage"
tool_description = "calculate resource usage per account. The period could be one month, or it could be several months. Usage is expressed in dollars."
tool_parameters = [
  {"name": "start_month", "type": "str", "description": "the starting month in period to calulate usage amount"},
  {"name": "end_month", "type": "str", "description": "the end month in period to calulate usage amount"},
  {"name": "accountId", "type": "str", "description": "account number"},
  {"name": "token", "type": "str", "description": "account number"},
]

time_of_day_tool = UsageOfAmount(tool_name, tool_description, tool_parameters)

from tool_use_package.tool_user import ToolUser
time_tool_user = ToolUser([time_of_day_tool], first_party=False, model="anthropic.claude-v2:1")

accountId = "532805286864"
token = "E578C5BF1A0E7DAFCAD875DC4A355B65"

import datetime
import time

year = datetime.date.today().year
month = datetime.date.today().month
day = datetime.date.today().day

while True:
  user_input = input("조회기간을 입력하세요. 예: 2023년 9월 사용량은? ")

  prompt = f"""accountId는 {accountId} 이고, token은 {token}입니다, 
          start_month와 end_month format은 '%Y%m'입니다.
          오늘은 {year}년 {month}월 {day}일 입니다. 
          year 정보가 부족할 경우 <year></year>사이의 정보를 사용하세요
          <year>{year}</year>
          month 정보가 하나일 경우, start_month와 end_month는 동일합니다.
          지난 달의 의미 previous month 이고, 작년의 의미는 year-1 입니다.
          답변 시 반드시 한국어를 사용하고 계정(account) 정보는 사용하지 마세요.
          {user_input}"""
  
  print("\nprompt: \n",prompt)
  print('\n\n')

  messages = [ {'role': 'user', 'content': prompt}]
  print("Please wait...")
  start_time = time.localtime().tm_sec
  result = time_tool_user.use_tools(messages, execution_mode='automatic')
  end_time = time.localtime().tm_sec

  elapsed_time = end_time - start_time

  print(result)
  print("elapsed time: ", elapsed_time, ' secs')
  print("-"*80)
  print('\n\n')





