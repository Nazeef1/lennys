# Manual Test Plan & QA Matrix
## The Lenny Growth Assistant UI & End-to-End Verification

---

## 1. Test Environment Setup
- Operating System: Windows / Linux / macOS
- Prerequisites: Python 3.11, Node.js v18+, Docker (optional)
- Command to run: `python run.py` (or backend on `http://localhost:8000`, frontend on `http://localhost:3000`)

---

## 2. Test Execution Matrix

| Test Case ID | Test Scenario | Steps | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **UI-001** | Initial Page Load & Health Check | Open `http://localhost:3000` | Header displays "The Lenny Growth Assistant", index chunk counter badge (>20 chunks), and active model indicator. | PASS |
| **UI-002** | Model Selector Dropdown | Click provider dropdown in header -> Select "Anthropic", "OpenAI", "Ollama", or "Fallback" | Provider updates dynamically with status indicator badge without requiring page refresh. | PASS |
| **UI-003** | Grounded Q&A Consultation | Enter prompt: *"What is Shreyas Doshi's LNO framework for product managers?"* | Assistant streams grounded response, cites guest "Shreyas Doshi", and includes collapsible "Grounded Sources" drawer. | PASS |
| **UI-004** | Ship 30 for 30 Skill Trigger | Click "Ship 30 Masterclass Essay" preset button or type *"Write a ~1,250 word Ship 30 essay on PLG retention loops"* | Assistant triggers `Ship30For30Skill` producing a structured ~1,250-word essay with hook, narrative, framework, and 5-step checklist. | PASS |
| **UI-005** | HTML Artifact Side-by-Side Rendering | Enter prompt: *"Generate an interactive HTML SaaS Growth Metrics Calculator artifact"* | Assistant generates complete HTML snippet; UI automatically expands the right-side Artifact Viewer rendering the live preview inside a sandboxed iframe. | PASS |
| **UI-006** | Iframe Sandbox Security Policy | Inspect HTML Artifact DOM element inside Chrome DevTools | Iframe exhibits `sandbox="allow-scripts"` and lacks `allow-same-origin`, preventing DOM/cookie access to host app. | PASS |
| **UI-007** | Copy Code & File Download | Click "Copy Code" button and "Download File" button in Artifact Viewer | Clipboard receives raw code string; browser downloads `.html` or `.md` file to disk. | PASS |
| **UI-008** | Session Persistence | Create a new session -> Switch back to previous session | Messages, citations, and generated artifacts reload seamlessly from PostgreSQL/SQLite. | PASS |
| **UI-009** | Resilience Fallback | Disable network/Ollama daemon and send a prompt | System catches connection error, logs diagnostic trace, and returns grounded fallback response without crashing. | PASS |
