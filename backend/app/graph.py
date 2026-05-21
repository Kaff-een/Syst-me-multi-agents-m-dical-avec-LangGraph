from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_node
from app.nodes.report_agent import report_node
from app.nodes.physician_review import physician_node
from app.tools.patient_tools import ask_patient
from app.tools.care_tools import recommend_interim_care
from app.tools.mcp_client import fetch_mcp_protocol

workflow = StateGraph(MedicalState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("diagnostic_agent", diagnostic_node)
workflow.add_node("report_agent", report_node)
workflow.add_node("physician_review", physician_node)

patient_tools = [ask_patient]
internal_tools = [recommend_interim_care, fetch_mcp_protocol]

workflow.add_node("patient_tools", ToolNode(patient_tools))
workflow.add_node("internal_tools", ToolNode(internal_tools))

workflow.add_edge(START, "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda x: x.get("next", "diagnostic_agent"),
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        "FINISH": END
    }
)

def route_diagnostic(state: MedicalState):
    messages = state.get("messages", [])
    if not messages:
        return "supervisor"
    last_message = messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_name = last_message.tool_calls[0]['name']
        if tool_name == "ask_patient":
            return "patient_tools"
        else:
            return "internal_tools"
            
    return "supervisor"

workflow.add_conditional_edges("diagnostic_agent", route_diagnostic)

workflow.add_edge("patient_tools", "diagnostic_agent")
workflow.add_edge("internal_tools", "diagnostic_agent")

workflow.add_edge("physician_review", "supervisor")
workflow.add_edge("report_agent", "supervisor")

memory = InMemorySaver()

api_graph = workflow.compile(
    checkpointer=memory,
    interrupt_after=["patient_tools"],     
    interrupt_before=["physician_review"]
)

graph = workflow.compile(
    interrupt_after=["patient_tools"],
    interrupt_before=["physician_review"]
)