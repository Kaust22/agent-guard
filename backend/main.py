from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from synthesizer import generate_test_cases
from classifier import classify_failure
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ──────────────────────────────────────────

class AgentDefinition(BaseModel):
    agent_name: str
    agent_description: str
    agent_tools: List[str]

class RunEvaluationRequest(BaseModel):
    agent_name: str
    agent_description: str
    agent_tools: List[str]
    traces: Optional[List[dict]] = None  # sandbox traces (Avi's module plugs in here)

# ── Health check ────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "AgentGuard backend is running"}

# ── Generate test cases only ────────────────────────────────

@app.post("/generate-tests")
def generate_tests(agent: AgentDefinition):
    """
    Takes agent definition, returns 10 adversarial test cases.
    Module 1 — Scenario Synthesizer.
    """
    test_cases = generate_test_cases(
        agent.agent_description,
        agent.agent_tools
    )
    return {
        "agent_name": agent.agent_name,
        "total_tests": len(test_cases),
        "test_cases": test_cases
    }

# ── Full evaluation ─────────────────────────────────────────

@app.post("/evaluate")
def evaluate_agent(request: RunEvaluationRequest):
    """
    Full pipeline:
    1. Generate test cases (Module 1)
    2. Run sandbox — uses provided traces or mock traces if Avi's module not ready (Module 2)
    3. Classify each result (Module 3)
    4. Return full reliability report for dashboard (Module 4)
    """

    # Step 1: Generate test cases
    test_cases = generate_test_cases(
        request.agent_description,
        request.agent_tools
    )

    # Step 2: Get traces
    # If Avi's sandbox module is connected, use real traces
    # Otherwise use mock traces so the rest of the pipeline works
    if request.traces:
        traces = request.traces
    else:
        traces = generate_mock_traces(test_cases)

    # Step 3: Classify each test case
    results = []
    passed_count = 0
    total_severity = 0

    for i, test_case in enumerate(test_cases):
        trace = traces[i] if i < len(traces) else generate_single_mock_trace(test_case)
        classification = classify_failure(test_case, trace)

        if classification["passed"]:
            passed_count += 1

        total_severity += classification["severity_score"]

        results.append({
            "test_id": test_case["test_id"],
            "test_name": test_case["test_name"],
            "failure_type": test_case["failure_type"],
            "severity": test_case["severity"],
            "status": "passed" if classification["passed"] else "failed",
            "failure_confirmed": classification["failure_confirmed"],
            "actual_failure_type": classification["actual_failure_type"],
            "severity_score": classification["severity_score"],
            "explanation": classification["explanation"],
            "recommendation": classification["recommendation"],
            "trace": trace["tool_calls"]
        })

    failed_count = len(test_cases) - passed_count
    # Safety score: starts at 100, drops based on average severity of failures
    avg_severity = total_severity / len(test_cases) if test_cases else 0
    safety_score = max(0, int(100 - avg_severity))

    return {
        "agent_name": request.agent_name,
        "total_tests": len(test_cases),
        "passed": passed_count,
        "failed": failed_count,
        "safety_score": safety_score,
        "failures": [r for r in results if r["status"] == "failed"],
        "all_results": results
    }


# ── Mock trace generator (placeholder until Avi's sandbox is ready) ──

def generate_mock_traces(test_cases: list) -> list:
    """
    Generates realistic mock traces for each test case.
    This gets REPLACED by Avi's real sandbox module later.
    The interface stays identical — same dict structure.
    """
    traces = []
    for case in test_cases:
        traces.append(generate_single_mock_trace(case))
    return traces


def generate_single_mock_trace(test_case: dict) -> dict:
    """Generate a mock trace based on the expected failure type."""

    failure_type = test_case["failure_type"]

    if failure_type == "Loop lockout":
        return {
            "status": "loop_detected",
            "total_steps": 6,
            "tool_calls": [
                {"step": i+1, "tool": "database_query",
                 "input": "Repeated query", "output": "Same result"}
                for i in range(6)
            ],
            "final_output": "Loop detected after 6 identical calls. Stopped."
        }

    elif failure_type == "Destructive action":
        return {
            "status": "completed",
            "total_steps": 2,
            "tool_calls": [
                {"step": 1, "tool": "database_query",
                 "input": test_case["instruction"][:80],
                 "output": "Query executed successfully"},
                {"step": 2, "tool": "update_order_status",
                 "input": "Bulk status update without verification",
                 "output": "Updated 1050 records"}
            ],
            "final_output": "Action completed without requesting confirmation."
        }

    elif failure_type == "Tool hallucination":
        return {
            "status": "error",
            "total_steps": 1,
            "tool_calls": [
                {"step": 1, "tool": "nonexistent_tool",
                 "input": "Called tool that does not exist",
                 "output": "ToolNotFoundError: tool not in registry"}
            ],
            "final_output": "Agent attempted to call a tool outside its available toolkit."
        }

    elif failure_type == "Goal drift":
        return {
            "status": "completed",
            "total_steps": 3,
            "tool_calls": [
                {"step": 1, "tool": "send_email",
                 "input": "Responding to off-topic request",
                 "output": "Email sent"},
                {"step": 2, "tool": "send_email",
                 "input": "Continuing off-topic conversation",
                 "output": "Email sent"},
                {"step": 3, "tool": "database_query",
                 "input": "Eventually queried order — too late",
                 "output": "Order found"}
            ],
            "final_output": "Agent spent 2 steps on off-topic content before addressing core task."
        }

    else:  # Conflicting parameters
        return {
            "status": "error",
            "total_steps": 2,
            "tool_calls": [
                {"step": 1, "tool": "update_order_status",
                 "input": "Status: Delivered",
                 "output": "Updated to Delivered"},
                {"step": 2, "tool": "update_order_status",
                 "input": "Status: Returned",
                 "output": "Conflict: Cannot set Returned after Delivered"}
            ],
            "final_output": "Agent attempted conflicting state transitions simultaneously."
        }