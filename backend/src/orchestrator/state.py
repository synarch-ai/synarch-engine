from typing import TypedDict, List, Annotated
import operator

class AgentLog(TypedDict):
    agent: str
    message: str
    timestamp: str

class MissionState(TypedDict):
    mission_id: str
    goal: str
    plan: List[str]
    current_step: int
    logs: Annotated[List[AgentLog], operator.add]
    final_output: str
