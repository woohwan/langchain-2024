import requests
import pandas as pd

fitcloud_url = "https://aws-dev.fitcloud.co.kr"
corpId = "KDjAqAG0TnEAAAFK5eqDUL0A"

accountId ="532805286864"
token = "8E50D599548535AEED40212E61BAE689"

# account 별 월 별 사용량 (saving plan 포함)
# type: usage - ApplySavingsPlanCompute
def corp_month(
    start_month: str, 
    end_month: str,
    token: str,
    groupBy="account",
    ):
  api_url = fitcloud_url + "/service/trend/corp/month"
  cookies = {
    "JSESSIONID": token,
  }

  data = {
      "from": start_month,
      "to": end_month,
      "groupBy": groupBy,
  }

  resp = requests.post(api_url, json=data, cookies=cookies)

  if resp.status_code == 200:
    # 일반 월 사용량에서 SavingPlan 가격을 제함
    return pd.DataFrame(resp.json())

  else:
    print("error")
#------------------------------------------------------------------------------------
# 월 입력값이  from: '201901', to: '202210'형태일 경우
# 시작 월부터 종료 월까지 리스트로 출력
from datetime import datetime, timedelta

def month_range(start_month, end_month):
    # Create datetime objects for start and end dates
    start_date = datetime.strptime(start_month, "%Y%m")
    end_date = datetime.strptime(end_month, "%Y%m")

    # Initialize list to store months
    months_list = []

    # Iterate over months and add them to the list
    current_month = start_date
    while current_month <= end_date:
        months_list.append(current_month.strftime("%Y%m"))
        current_month = (current_month + timedelta(days=32)).replace(day=1)

    return months_list
#-------------------------------------------------------------------------------------
# account 일자별 사용량을 반환
def ondemand_account_day(
    accountId: str, 
    day_from: str, 
    day_to: str, 
    token: str) -> float:
  api_url = fitcloud_url + "/ondemand/account/day"
  cookies = {
    "JSESSIONID": token,
  }

  data = {
      "from": day_from,
      "to": day_to,
      "accountId": accountId,
  }
  resp = requests.post(api_url, json=data, cookies=cookies)

  if resp.status_code == 200:
    # JSON 형식으로 응답을 파싱 후 usageFee 합계를 구하기 위해 dataframe 의 변환
    df = pd.DataFrame(resp.json())
    usage_sum = round( df['usage_fee'].astype("Float32").sum(), 2)
    return usage_sum

  else:
    print("error")

def corp_month_internal(start_month: str, end_month: str, accountId: str, token: str):
  """calculate resource usage per account. The period could be one month, or it could be several months. Usage is expressed in dollars.
  """
  json_data = corp_month(start_month, end_month, token)
  df = pd.DataFrame(json_data)
  # accountId = accountId
  # account에 관련된 데이터 추출
  df = df.query("accountId==@accountId")
  # 기간 내 월 리스트 추출
  month_list = month_range(start_month, end_month)
  # 월 column의 data type을 numeric으로 변환
  df_acc = df.copy()
  df_acc[month_list] = df_acc[month_list].apply(pd.to_numeric)
  # 내부 사용자용 filter: 합산에 포함시킬 항목
  internal_filter = ['Usage','ApplySavingsPlanCompute', 'ApplyRI' ]
  # internal_filter = ['Usage','ApplySavingsPlanCompute']
  df_int = df_acc.query("type in @internal_filter")
  sum = df_int[month_list].sum().sum()
  return sum

corp_month_internal_description = """
<tool_description>
<tool_name>corp_month_internal</tool_name>
<description>
Returns resource usage for a given start month, end month, accountId and token. </description>
<parameters>
<parameter>
<name>start_month</name>
<type>string</type>
<description>start month as a string format '%Y%m' in resource usage duration.
for example. not '2023-09-01' but '202309' </description>
</parameter> 
<parameter>
<name>end_month</name>
<type>string</type>
<description>end month as a string format '%Y%m' in resource usage duration. for example. not '2023-09-01' but '202309'</description>
</parameter>
<parameter>
<name>accountId</name>
<type>string</type>
<description>account id as a string who used resource</description>
</parameter>
<parameter>
<name>token</name>
<type>string</type>
<description>token value as a string</description>
</parameter>
</parameters>
</tool_description>
"""


list_of_tools_specs = [corp_month_internal_description]