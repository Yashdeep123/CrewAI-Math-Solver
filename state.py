from pydantic import BaseModel, Field


class MathState(BaseModel):
    question: str = ""
    concept : str = ""
    equation : str = ""
    answer: str = ""

class MathQuestionType(BaseModel):
    concept: str = Field(default="", description="Identifies as the question is of conceptual, theoretical or any of the math's terminology related question.")
    equation: str = Field(default="", description="Identifies as the question is of equation type, requiring computational steps to solve.")
