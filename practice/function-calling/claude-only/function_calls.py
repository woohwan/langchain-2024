import sys
from defusedxml import ElementTree
from collections import defaultdict
import os
from typing import Any
import time
import fitcloud
import boto3
import json
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

# timer decorator
def time_duration(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time} seconds")
        return result
    return wrapper

# fit cloud api belows
def create_prompt(tools_string, user_input):
    prompt_template = f"""
In this environment you have access to a set of tools you can use to answer the user's question.

You may call them like this. Only invoke one function at a time and wait for the results before invoking another function.
<function_calls>
<invoke>
<tool_name>$TOOL_NAME</tool_name>
<parameters>
<$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>
...
</parameters>
</invoke>
</function_calls>

Here are the tools available:
<tools>
{tools_string}
</tools>

Human:
{user_input}


Assistant:
"""
    return prompt_template

def add_tools():
    tools_string = ""
    for tool_spec in fitcloud.list_of_tools_specs:
        tools_string += tool_spec
    return tools_string

# account Id, token 추가.
def call_function(tool_name, parameters):
    func = getattr(fitcloud, tool_name)

    print("parameters",  parameters)
    output = func(**parameters)
    return output

def format_result(tool_name, output):
    return f"""
<function_results>
<result>
<tool_name>{tool_name}</tool_name>
<stdout>
{output}
</stdout>
</result>
</function_results>
"""

def etree_to_dict(t) -> dict[str, Any]:
    d = {t.tag: {}}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
    if t.text and t.text.strip():
        if children or t.attrib:
            d[t.tag]["#text"] = t.text
        else:
            d[t.tag] = t.text
    return d

@time_duration
def run_loop(prompt, accountId:str, token: str):
    print(prompt)
    # Start function calling loop
    while True:
    # initialize variables to make bedrock api call
        bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
        modelId = 'anthropic.claude-v2'
        body = json.dumps({"prompt": prompt,
        "stop_sequences":["\n\nHuman:", "</function_calls>"],
        "max_tokens_to_sample": 700,
        "temperature": 0})
        accept = 'application/json'
        contentType = 'application/json'
        # bedrock api call with prompt
        partial_completion = bedrock.invoke_model(
            body=body, 
            modelId=modelId, 
            accept=accept, 
            contentType=contentType
        )
   
        response_body = json.loads(partial_completion.get('body').read())


        partial_completion= response_body.get('completion')
        stop_reason=response_body.get('stop_reason')
        stop_seq = partial_completion.rstrip().endswith("</invoke>")
        
        # Get a completion from Claude

        # Append the completion to the end of the prommpt
        prompt += partial_completion
        if stop_reason == 'stop_sequence' and stop_seq:
            # If Claude made a function call
            print(partial_completion)
            start_index = partial_completion.find("<function_calls>")
            if start_index != -1:
                # Extract the XML Claude outputted (invoking the function)
                extracted_text = partial_completion[start_index+16:]

                # Parse the XML find the tool name and the parameters that we need to pass to the tool
                xml = ElementTree.fromstring(extracted_text)
                tool_name_element = xml.find("tool_name")
                if tool_name_element is None:
                    print("Unable to parse function call, invalid XML or missing 'tool_name' tag")
                    break
                tool_name_from_xml = tool_name_element.text.strip()
                parameters_xml = xml.find("parameters")
                if parameters_xml is None:
                    print("Unable to parse function call, invalid XML or missing 'parameters' tag")
                    break
                param_dict = etree_to_dict(parameters_xml)
                parameters = param_dict["parameters"]

                # 외부에서 고정 값으로 들어오는 값
                parameters['accountId'] = accountId
                parameters['token'] = token

                # Call the tool we defined in tools.py
                output = call_function(tool_name_from_xml, parameters)

                # Add the stop sequence back to the prompt
                prompt += "</function_calls>"
                print("</function_calls>")

                # Add the result from calling the tool back to the prompt
                function_result = format_result(tool_name_from_xml, output)
                print(function_result)
                prompt += function_result
        else:
            # If Claude did not make a function call
            # outputted answer
            print(partial_completion)
            break

# user_input = "account id 532805286864의 2023년 9월 자원 사용량은? token 값은 '8E50D599548535AEED40212E61BAE689'입니다?"
user_input = "2023년 9월 자원 사용량은?"
tools_string = add_tools()
prompt = create_prompt(tools_string, user_input)
run_loop(prompt, accountId="532805286864", token="151C75D463D0601E490A0B1EA283D841")