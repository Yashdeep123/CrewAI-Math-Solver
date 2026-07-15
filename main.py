from inspect import ClassFoundException

from crewai_tools import WebsiteSearchTool
from crewai import Agent, LLM, Crew, Process, Task
from crewai.utilities.types import LLMMessage
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router
from dotenv import load_dotenv

from tools.math_tools import derivative_tool, integral_tool, factor_tool, simplify_tool
from prompts.prompts import classifier_prompt, concept_prompt # type: ignore
from state import MathQuestionType, MathState

load_dotenv()

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
        search_tool = WebsiteSearchTool()
        
        agent = Agent(role="Expert Math teacher/tutor",
                      llm=llm,
                      goal="Answer conceptual math questions using reliable web sources when needed.",
                      backstory="You are an experienced mathematics educator with deep knowledge "
                      "of algebra, calculus, geometry, probability, and linear algebra. "
                      "You explain concepts using intuitive examples and simple language.",
                      tools=[search_tool],
                      prompt_template=concept_prompt)
        
        result = agent.kickoff(concept)
        self.state.answer = result.raw # type:ignore
        return result.raw # type:ignore
    
    @listen("equation")
    def equation_handler(self):
        question = self.state.equation

        # Agent 1: Solve using newton API 1
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
flow.state.question = "Explain the intuition behind the chain rule in differentiation."
flow.kickoff()

print(f"Answer: {flow.state.answer}")
