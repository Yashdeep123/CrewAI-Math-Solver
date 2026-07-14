from inspect import ClassFoundException

from crewai import Agent, LLM, Crew, Process, Task
from crewai.utilities.types import LLMMessage
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router
from crewai_tools import TavilySearchTool
from dotenv import load_dotenv

from tools.math_tools import derivative_tool, integral_tool, factor_tool, simplify_tool
from prompts.prompts import classifier_prompt # type: ignore

load_dotenv()

class MathState(BaseModel):
    question: str = ""
    concept : str = ""
    equation : str = ""
    answer: str = ""


class MathQuestionType(BaseModel):
    concept: str = Field(default="", description="Identifies as the question is of conceptual, theoretical or any of the math's terminology related question.")
    equation: str = Field(default="", description="Identifies as the question is of equation type, requiring computational steps to solve.")

llm = LLM(model="gpt-4o-mini")

class MathFlow(Flow[MathState]):
    @start()
    def classifier(self):
        question = self.state.question
        classifier_llm = LLM(
             model="gpt-5-nano")

        result = classifier_llm.call(messages=[
            LLMMessage(role="system", content=classifier_prompt),
            LLMMessage(role="user", content=f"Question: '{question}'")], response_model= MathQuestionType)
        return result # type: ignore
    
    @router(classifier)
    def route_next(self, result):
        concept = result.concept.strip()
        equation = result.equation.strip()

        if concept:
            self.state.concept = concept
            return "concept"
        elif equation:
            self.state.equation = equation
            return "equation"

    @listen("concept")
    def concept_handler(self):
        concept = self.state.concept
        return f"Conceptual Question: {concept}"
    
    @listen("equation")
    def equation_handler(self):
        question = self.state.equation

        # Agent 1: Solve using netwon API 1
        agent = Agent(
            tools=[derivative_tool, integral_tool, simplify_tool, factor_tool],
            llm=llm,
            role="Mathematical Calculus and Algebric Solving Agent",
            goal="Solve the given expression from the question",
            backstory="You are a math problem solving agent. You have access to the tools that can help you solve calculus problems.",
            verbose=True
        )

        task = Task(
            description=f"""

                   Solve the following mathematical problem:

                   Question:

                   {question}

                   Use the most appropriate tool for the expression.

                   Do not guess the answer if a tool is applicable.
                   If no tool applies, explain why.
                    """,

            expected_output="""

Return only the final solution as a string.

If applicable, include the intermediate mathematical expression returned by the tool.

""", agent = agent
     
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        self.state.answer = result.raw # type: ignore

        return result.raw # type: ignore


flow = MathFlow()
flow.state.question = "What is the derivation of x3?"
flow.kickoff()

print(f"Answer: {flow.state.answer}")
