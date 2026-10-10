# ContentCrew — Part B3 Content Research & Writing

A Streamlit application using a real CrewAI Crew with two Agents and two Tasks. Enter a topic to receive an outline, key points and an article or LinkedIn-style post, with visible source excerpts and the actual CrewAI execution result.

## Setup (Windows / VS Code PowerShell)

Use Python 3.11 or 3.12. Extract this folder, open it in VS Code and run these commands from the folder containing app.py and requirements.txt:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Edit `.env` and enter your own `OPENAI_API_KEY`; no key is supplied. Alternatively enter a key in the masked sidebar field for the current browser session. Do not place requirements.txt inside .venv. The explicit interpreter commands above work without activating PowerShell scripts.

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m streamlit run app.py
```

The dependency ranges permit compatible updates; after a successful install, record your environment with `python -m pip freeze > requirements.lock.txt` if exact reproducibility is required.

## Local model option

Install Ollama, start its service, then run:

```text
ollama pull llama3.1:8b
ollama list
```

Select Ollama in the sidebar and enter the exact installed model name. Defaults come from OLLAMA_MODEL and OLLAMA_BASE_URL in .env. The local model must handle tool calls and structured output; smaller models may struggle. No OpenAI key is required in this mode. Wikipedia research still needs internet access. With OpenAI, requests incur API charges independently of a ChatGPT subscription.

## Agent, Task and Crew

1. **Evidence Researcher Agent:** role = research librarian; goal = traceable facts; backstory = careful evidence reviewer. It can call the custom `ApprovedEvidenceTool`, a CrewAI BaseTool that searches the approved source corpus.
2. **Research Task:** describes what to investigate and expects supported claims, source IDs, URLs and gaps. The app retrieves source text first, so a tool-call failure cannot silently turn research into unsupported model memory.
3. **Writer Agent:** role = writer/editor; goal = readable grounded content; backstory = editor who avoids fabricated claims.
4. **Writing Task:** receives the Research Task through `context=[research_task]`; expects a Pydantic Draft with title, outline, key_points, content and limitations.
5. **Crew:** connects both Agents and Tasks using `Process.sequential`. `crew.kickoff()` runs research then writing through the selected LLM. The UI displays `result.raw`, the structured result, the intermediate research output and token usage.

Workflow: Streamlit form → validation → approved-source retrieval → Research Agent/Task → Writer Agent/Task → CrewOutput → Streamlit tabs and Markdown download.

The optional collaboration extension is implemented through task context, rather than autonomous delegation. Role, goal, backstory, description and expected_output are explicit in workflow.py.

## Approved research source and limits

The only research endpoint is the English Wikipedia API (`https://en.wikipedia.org/w/api.php`). It searches the topic and retrieves up to four introductory text extracts and canonical page URLs. There is no arbitrary URL fetching. The corpus is scoped to each run; source IDs [S1]–[S4] refer to the exact excerpts shown in the UI. The lookup tool reads this same corpus. This is suitable for a small educational assignment and general background, not exhaustive research or live news validation.

Agents are instructed to cite factual claims, use only the corpus and report insufficient evidence. These are model instructions, not a guarantee of factual correctness: source relevance and claim entailment still need human review. The app does not independently verify every citation, fact or target word count. Wikipedia is a secondary source, and introductory excerpts can omit nuance. Choose a specific background topic; for example, “data quality”, “renewable energy”, or “machine learning”. A claim about today's market/news may lack sufficient evidence.

## UI and error handling

- Topic and audience length validation; model/key validation before research.
- Network requests have timeouts; empty/error sources stop the run.
- Previous results are cleared before a new attempt.
- Provider/runtime errors use a generic message so credentials are not echoed.
- No automatic retries that silently loop forever; agent iterations and retries are limited.
- Structured-output fallback displays the raw CrewOutput clearly.
- Markdown downloads include source links but never API keys.
- No publishing or LinkedIn account connection: outputs are drafts for review.

Credentials stay in .env or the password widget. Do not commit .env. They are not deliberately logged or put in results; a password widget masks display but the app server still receives the value. Use locally or deploy only behind appropriate access controls. Model requests include the topic and source extracts. CrewAI verbose output and telemetry are disabled by default. No app-level disk storage or shared result cache is used.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests cover invalid inputs, approved-source filtering and empty-source failure using mocked network responses. For an integration check, run the app with your own key or local model, enter “data quality”, and confirm both task outputs, outline, key points, final content, source IDs/links and Markdown download. Test a blank topic and an invalid model/key. Automated checks do not make paid calls. During delivery, Python compilation, the three offline source tests, Streamlit initial rendering and blank-input UI validation passed. Actual CrewAI object construction and output handling were also checked with kickoff mocked. A live LLM generation was not run because no user API key or local model was supplied.

## Files

- app.py — Streamlit form, configuration and result tabs
- workflow.py — LLM, Agents, Tasks, Crew and evidence tool
- research.py — approved-source retrieval and validation
- .env.example — secret-free configuration template
- requirements.txt — dependencies
- tests/test_research.py — offline validation tests

## Official references

- https://docs.crewai.com/en/concepts/agents
- https://docs.crewai.com/en/concepts/tasks
- https://docs.crewai.com/en/concepts/crews
- https://docs.crewai.com/en/concepts/tools
- https://docs.crewai.com/en/learn/llm-connections
