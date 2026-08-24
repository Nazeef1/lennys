# Design Principles and UI/UX Rationale
## The Lenny Growth Assistant

---

## 1. Design System & Aesthetics

### 1.1 Visual Identity & Palette
The Lenny Growth Assistant utilizes a high-contrast dark theme with vibrant indigo, purple, and emerald accents inspired by modern AI developer tools (Linear, Raycast, Claude Artifacts).

- **Background Dark**: `#0f172a` (Slate 900) - Deep, anti-fatigue canvas.
- **Card/Panel Glass**: `rgba(30, 41, 59, 0.7)` with `backdrop-filter: blur(12px)` - Modern depth.
- **Primary Accent**: `#6366f1` (Indigo 500) - Trust, intelligence, and focus.
- **Artifact Highlight**: `#a855f7` (Purple 500) - Expressive content creation.
- **Success & Grounding**: `#10b981` (Emerald 500) - Verifiable citation status.
- **Border Utility**: `rgba(255, 255, 255, 0.08)` - Crisp division without visual clutter.

### 1.2 Typography
- **Primary UI Font**: Inter (Google Fonts) - Clean sans-serif optimized for dense analytical dashboards.
- **Monospace / Code**: JetBrains Mono - Clear code formatting in the Artifact Viewer.

---

## 2. Information Architecture & Layout Specs

```
+-----------------------------------------------------------------------------------+
|  HEADER BAR: Brand | Knowledge Index Status | Model Switcher (Ollama/Claude/GPT)  |
+---------------------+---------------------------------------+---------------------+
| SIDEBAR (w-72)      | CHAT INTERFACE (Flex-1)               | ARTIFACT VIEWER     |
| - New Chat Button   | - Message History & Markdown          | (Side-by-Side 50%)  |
| - Growth Templates  | - Grounded Citation Accordion         | - Preview Tab       |
| - History List      | - Quick Action Artifact Buttons       | - Code Tab          |
|                     | - Message Input Bar                   | - Iframe Sandbox    |
+---------------------+---------------------------------------+---------------------+
```

### 2.1 Split-Pane Workspace Design
The application features a responsive split-pane layout:
- **Left Pane (Chat & Navigation)**: Focuses on conversation flow, prompt input, and quick templates.
- **Right Pane (Side-by-Side Artifact Viewer)**: Opens dynamically when the assistant generates an HTML component or Markdown report. This eliminates context-switching and allows users to preview interactive artifacts while continuing to converse.

---

## 3. Security Isolation Strategy (Iframe Sandbox)

### 3.1 Threat Model
Generated HTML/CSS/JS artifacts originate from dynamic LLM outputs. Rendering raw untrusted HTML directly in the host DOM (`dangerouslySetInnerHTML`) creates severe Cross-Site Scripting (XSS) risks, DOM pollution, and potential cookie theft.

### 3.2 Security Mitigation Architecture
All HTML artifacts are rendered inside an HTML5 `<iframe>` element with explicit sandbox policies:

```html
<iframe
  srcDoc={artifact.content}
  title={artifact.title}
  sandbox="allow-scripts"
  className="w-full h-full rounded-xl bg-white border border-slate-700 shadow-inner"
/>
```

### 3.3 Security Policies Enforced
1. `allow-scripts`: Permits standard vanilla JavaScript execution (e.g. interactive chart calculations, sliders, toggles).
2. **Omitted `allow-same-origin`**: Forces the iframe into a unique, isolated null origin. The artifact script cannot read host localStorage, access parent cookies, or manipulate the parent application DOM.
3. **Omitted `allow-top-navigation`**: Prevents untrusted scripts from redirecting the parent app window to malicious third-party URLs.

---

## 4. Key Interaction States

1. **Idle State**: Displays welcome banner with feature cards and preset growth templates.
2. **Ingesting / Processing State**: Pulsing ambient status indicator with model badge.
3. **Citation Expansion State**: Accordion toggle displaying matching transcript chunks with match scores and guest metadata.
4. **Artifact View State**: Smooth slide-in right pane with tabbed Preview/Code views, copy to clipboard, and one-click file download.
