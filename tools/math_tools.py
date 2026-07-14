from crewai.tools import tool
import requests, re

base_url = "https://newton.vercel.app/api/v2/"

@tool("Derivative Tool")
def derivative_tool(expression: str) -> str:
    "This tool performs a calculation of derivative of the given equation."
    express = re.sub(r'([a-zA-Z])(\d+)\b', r'\1^\2', expression)
    result = requests.get(f"{base_url}derive/{express}")
    return result.json()

@tool("Integral Tool")
def integral_tool(expression: str) -> str:
    "This tool performs a calculation of integral of the given equation."
    express = re.sub(r'([a-zA-Z])(\d+)\b', r'\1^\2', expression)
    result = requests.get(f"{base_url}integrate/{express}")

    return result.json()

@tool("Factor Tool")
def factor_tool(equation: str) -> str:
    "This tool performs a calculation of factoring the given equation."
    express = re.sub(r'([a-zA-Z])(\d+)\b', r'\1^\2', equation)
    result = requests.get(f"{base_url}factor/{express}")

    return result.json()["result"]

@tool("Simplify Tool")
def simplify_tool(equation: str) -> str:
    "This tool performs a calculation of simplifying or expanding the given equation."
    express = re.sub(r'([a-zA-Z])(\d+)\b', r'\1^\2', equation)
    result = requests.get(f"{base_url}simplify/{express}")

    return result.json()["result"]
