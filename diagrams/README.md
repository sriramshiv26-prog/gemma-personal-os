# Architecture Diagrams

This folder contains professional enterprise-grade diagrams for the Gemma 4 Personal OS architecture.

## Diagrams Included

### 1. Task Execution Pipeline (BPMN Swimlane)
**File:** `task-execution-pipeline.png`
- **Type:** BPMN Swimlane Diagram (5 lanes)
- **Purpose:** Shows complete task execution flow from user input through agent processing to result delivery
- **Lanes:** User, System, Agent, Storage, External Services
- **Quality:** 300 DPI, professional enterprise-grade
- **Use Case:** Technical documentation, training, compliance review

**What it shows:**
- User submits task
- System receives, validates, and routes
- Agent executes with intelligent model selection (local vs external)
- Results stored in persistence layer
- Complete audit trail captured

### 2. System Architecture (C4 Context)
**File:** `system-architecture.png` (to be generated)
- **Type:** C4 Context Diagram
- **Purpose:** System components and their interactions
- **Includes:** Model router, orchestration, knowledge layer, tools

### 3. Data Flow Diagram (DFD)
**File:** `dataflow-diagram.png` (to be generated)
- **Type:** Data Flow Diagram
- **Purpose:** Data movement through the system
- **Shows:** Processes, data stores, external entities, flows

---

## How to Use These Diagrams

### In Documentation
```markdown
![Task Execution Pipeline](diagrams/task-execution-pipeline.png)
```

### In Presentations
- Use 300 DPI versions for printing (professional quality)
- Diagrams are colorblind-safe and accessible

### Customization
- Edit original DOT/Graphviz files in `/templates/`
- Regenerate with: `dot -Tpng -Gdpi=300 diagram.dot -o diagram.png`
- Or use Visio-Analytix skill for enterprise-grade updates

---

## Quality Standards

All diagrams follow enterprise-grade standards:
- ✓ 300 DPI minimum resolution
- ✓ Professional color palette (light pastels + dark borders)
- ✓ Clear typography (Helvetica, 9-12pt)
- ✓ Colorblind-safe colors
- ✓ Proper spacing and alignment
- ✓ Semantic clarity (no ambiguous arrows)

---

## Creating New Diagrams

See [../templates/ENTERPRISE-SWIMLANE-EXAMPLES.md](../templates/ENTERPRISE-SWIMLANE-EXAMPLES.md) for reusable templates and best practices.

---

Last updated: May 2026
