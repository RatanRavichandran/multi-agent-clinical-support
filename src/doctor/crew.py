from pathlib import Path
import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, MDXSearchTool, SerperDevTool, ScrapeWebsiteTool


@CrewBase
class Diagnosis:
    """Orchestrates the diagnostic workflow crew."""

    _BASE_DIR = Path(__file__).resolve().parents[2]
    _CONFIG_DIR = Path(__file__).resolve().parent / "config"

    agents_config = str(_CONFIG_DIR / "agents.yaml")
    tasks_config = str(_CONFIG_DIR / "tasks.yaml")

    _PATIENT_CASE_DIR = _BASE_DIR / "data" / "patient_case"
    _KNOWLEDGE_BASE_DIR = _BASE_DIR / "data" / "knowledge_base"
    _MDX_FILE = _KNOWLEDGE_BASE_DIR / "overall.mdx"

    def __init__(self) -> None:
        required_files = {
            "patient_profile": self._PATIENT_CASE_DIR / "patient_profile.txt",
            "lab_results": self._PATIENT_CASE_DIR / "lab_results.txt",
            "imaging_results": self._PATIENT_CASE_DIR / "imaging_results.txt",
            "knowledge_index": self._MDX_FILE,
        }

        missing = [name for name, path in required_files.items() if not path.exists()]
        if missing:
            readable = ", ".join(missing)
            raise FileNotFoundError(
                f"Missing required data files: {readable}. "
                "Check the data directory layout."
            )

        self.mdx_search_tool = MDXSearchTool(mdx=str(self._MDX_FILE))

        self.patient_history_tool = FileReadTool(
            file_path=str(required_files["patient_profile"])
        )
        self.lab_history_tool = FileReadTool(
            file_path=str(required_files["lab_results"])
        )
        self.imaging_data_tool = FileReadTool(
            file_path=str(required_files["imaging_results"])
        )

        serper_api_key = os.getenv("SERPER_API_KEY")
        if not serper_api_key:
            raise EnvironmentError(
                "SERPER_API_KEY environment variable is not set. "
                "Provide your Serper API key before running the crew."
            )
        os.environ["SERPER_API_KEY"] = serper_api_key

        self.serper_search_tool = SerperDevTool(api_key=serper_api_key)
        self.scrape_website_tool = ScrapeWebsiteTool()

    @agent
    def ethics_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["ethics_advisor"],
            verbose=True,
            tools=[
                self.patient_history_tool,
                self.lab_history_tool,
                self.imaging_data_tool,
                self.mdx_search_tool,
            ],
        )

    @agent
    def medical_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["medical_researcher"],
            verbose=True,
            tools=[
                self.patient_history_tool,
                self.lab_history_tool,
                self.imaging_data_tool,
                self.mdx_search_tool,
                self.serper_search_tool,
                self.scrape_website_tool,
            ],
        )

    @agent
    def patient_historian(self) -> Agent:
        return Agent(
            config=self.agents_config["patient_historian"],
            verbose=True,
            tools=[
                self.patient_history_tool,
                self.mdx_search_tool,
            ],
        )

    @agent
    def lab_interpreter(self) -> Agent:
        return Agent(
            config=self.agents_config["lab_interpreter"],
            verbose=True,
            tools=[
                self.lab_history_tool,
                self.imaging_data_tool,
                self.mdx_search_tool,
            ],
        )

    @agent
    def case_data_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["case_data_extractor"],
            verbose=True,
            tools=[
                self.patient_history_tool,
                self.lab_history_tool,
                self.imaging_data_tool,
                self.mdx_search_tool,
            ],
        )

    @agent
    def diagnostic_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["diagnostic_specialist"],
            verbose=True,
            tools=[
                self.patient_history_tool,
                self.lab_history_tool,
                self.imaging_data_tool,
                self.mdx_search_tool,
            ],
        )

    @task
    def ethics_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["ethics_review_task"]
        )

    @task
    def medical_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["medical_research_task"]
        )

    @task
    def patient_history_task(self) -> Task:
        return Task(
            config=self.tasks_config["patient_history_task"]
        )

    @task
    def lab_interpretation_task(self) -> Task:
        return Task(
            config=self.tasks_config["lab_interpretation_task"]
        )

    @task
    def case_data_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config["case_data_extraction_task"]
        )

    @task
    def diagnostic_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config["diagnostic_assessment_task"]
        )

    @task
    def treatment_recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config["treatment_recommendation_task"]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Diagnosis crew."""

        return Crew(
            agents=[
                self.ethics_advisor(),
                self.medical_researcher(),
                self.patient_historian(),
                self.lab_interpreter(),
                self.case_data_extractor(),
                self.diagnostic_specialist(),
            ],
            tasks=[
                self.ethics_review_task(),
                self.medical_research_task(),
                self.patient_history_task(),
                self.lab_interpretation_task(),
                self.case_data_extraction_task(),
                self.diagnostic_assessment_task(),
                self.treatment_recommendation_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
