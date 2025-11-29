import os
import re
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

# Define the state of our graph
# Define the state of our graph
class AgentState(TypedDict):
    topic: str
    research_data: List[str]
    analysis: str
    chart_files: List[str]
    final_report: str
    feedback: str
    revision_count: int

class MarketResearchGraph:
    def __init__(self, model_provider="gemini"):
        self.model_provider = model_provider
        self.search_tool = DuckDuckGoSearchRun()
        self.llm = self._get_llm()

    def _get_llm(self):
        if self.model_provider == "openai":
            return ChatOpenAI(
                model="gpt-4o",
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            # Default to Gemini
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.7
            )

    def researcher_node(self, state: AgentState):
        print(f"--- Researcher: Searching for {state['topic']} ---")
        topic = state['topic']
        feedback = state.get('feedback', '')
        
        query = f"latest market trends and news for {topic} last 12 months"
        if feedback:
            query = f"market research for {topic} focusing on: {feedback}"
            print(f"--- Researcher: Refining search based on feedback: {feedback} ---")
            
        search_results = self.search_tool.invoke(query)
        return {"research_data": [search_results]}

    def analyst_node(self, state: AgentState):
        print("--- Analyst: Analyzing data ---")
        data = "\n".join(state['research_data'])
        feedback = state.get('feedback', '')
        
        prompt = f"""
        Analyze the following market data about {state['topic']}:
        {data}
        
        Identify top 3 trends, potential opportunities, and major risks.
        Also extract any numerical data that could be visualized (e.g., market growth, percentages).
        """
        
        if feedback:
            prompt += f"\n\nIMPORTANT: Previous analysis was rejected. Please address this feedback: {feedback}"
            
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"analysis": response.content}

    def reviewer_node(self, state: AgentState):
        print("--- Reviewer: Reviewing analysis ---")
        analysis = state['analysis']
        revision_count = state.get('revision_count', 0)
        
        if revision_count >= 2:
            print("--- Reviewer: Max revisions reached, approving ---")
            return {"feedback": None}
            
        prompt = f"""
        Review the following market analysis for {state['topic']}:
        {analysis}
        
        Is this analysis comprehensive, data-backed, and insightful?
        If YES, respond with "APPROVED".
        If NO, respond with "REJECTED" followed by specific feedback on what is missing or needs improvement (e.g., "Missing specific market size data", "Too generic", "Needs more focus on risks").
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = response.content
        
        if "APPROVED" in result:
            return {"feedback": None}
        else:
            feedback = result.replace("REJECTED", "").strip()
            return {"feedback": feedback, "revision_count": revision_count + 1}

    def chart_generator_node(self, state: AgentState):
        print("--- Chart Generator: Creating charts ---")
        analysis = state['analysis']
        
        # Clean up previous charts
        for f in os.listdir():
            if f.startswith("chart_") and f.endswith(".png"):
                try:
                    os.remove(f)
                except:
                    pass

        prompt = f"""
        Based on the following analysis, generate Python code using matplotlib to create MULTIPLE relevant charts (bar charts, pie charts, or line charts) if the data allows.
        
        Analysis:
        {analysis}
        
        Requirements:
        1. Use matplotlib.pyplot.
        2. The code should be self-contained (import matplotlib.pyplot as plt, etc.).
        3. Define the data directly in the code based on the analysis (estimate values if necessary but keep them realistic).
        4. Create as many distinct charts as relevant (at least 1, up to 3).
        5. Save the plots to files named 'chart_1.png', 'chart_2.png', etc. using plt.savefig().
        6. Clear the figure between plots using plt.clf() or plt.figure().
        7. Use a modern, professional style (e.g., plt.style.use('ggplot') or custom colors).
        8. Do NOT use plt.show().
        9. Return ONLY the python code, no markdown formatting like ```python.
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        code = response.content.replace("```python", "").replace("```", "").strip()
        
        # Execute the code to generate the chart
        try:
            exec(code, {"plt": plt})
            print("Charts generated successfully.")
        except Exception as e:
            print(f"Failed to generate charts: {e}")
            
        # Find generated charts
        chart_files = [f for f in os.listdir() if f.startswith("chart_") and f.endswith(".png")]
        chart_files.sort() # Ensure consistent order
        return {"chart_files": chart_files}

    def writer_node(self, state: AgentState):
        print("--- Writer: Writing report ---")
        analysis = state['analysis']
        chart_files = state.get('chart_files', [])
        
        prompt = f"""
        Write a comprehensive market research report on {state['topic']} based on the following analysis:
        {analysis}
        
        The report must be in Markdown format with sections for Executive Summary, Key Trends, Opportunities, Risks, and Conclusion.
        
        IMPORTANT: The following chart images have been generated: {", ".join(chart_files)}
        You MUST embed these charts inline within the relevant sections of your report using markdown image syntax: ![Description](filename)
        
        For example:
        - Place market trend charts in the "Key Trends" section
        - Place opportunity/risk charts in their respective sections
        - Distribute the charts throughout the report where they best support your analysis
        
        DO NOT create a separate "Visualizations" section at the end. Instead, embed each chart directly in the section where it's most relevant.
        Each chart should have a descriptive caption that explains what it shows.
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {"final_report": response.content}

    def should_continue(self, state: AgentState):
        if state.get('feedback'):
            return "researcher"
        return "chart_generator"

    def _create_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("researcher", self.researcher_node)
        workflow.add_node("analyst", self.analyst_node)
        workflow.add_node("reviewer", self.reviewer_node)
        workflow.add_node("chart_generator", self.chart_generator_node)
        workflow.add_node("writer", self.writer_node)
        
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "reviewer")
        
        workflow.add_conditional_edges(
            "reviewer",
            self.should_continue,
            {
                "researcher": "researcher",
                "chart_generator": "chart_generator"
            }
        )
        
        workflow.add_edge("chart_generator", "writer")
        workflow.add_edge("writer", END)
        return workflow.compile()

    def run(self, topic: str):
        app = self._create_graph()
        inputs = {"topic": topic, "research_data": [], "analysis": "", "chart_files": [], "final_report": "", "feedback": None, "revision_count": 0}
        result = app.invoke(inputs)
        with open("report.md", "w") as f:
            f.write(result["final_report"])
        return result

    def run_stream(self, topic: str):
        app = self._create_graph()
        inputs = {"topic": topic, "research_data": [], "analysis": "", "chart_files": [], "final_report": "", "feedback": None, "revision_count": 0}
        for output in app.stream(inputs):
            for key, value in output.items():
                yield key, value
