---
name: workflow-designer
description: "Socratic interview to design multi-agent workflows with orchestration, routing, and coordination"
---

# Workflow Designer

Guide the user through designing a multi-agent workflow — where multiple agents coordinate to complete a complex business process. This follows the proven "agent mesh" pattern used by the blog creation system.

## What is a Multi-Agent Workflow?

A workflow is a coordinated process where:
- An **orchestrator** receives requests and routes to specialists
- **Specialist agents** handle specific steps with dedicated skills
- A **hub agent** (optional) handles notifications and status updates
- Agents communicate via message passing through the CLI

Example: The blog creation workflow has a Blog Orchestrator that routes to Blog Technical, Blog Narrative, or Blog Announcement agents, each with specialised skills, coordinated via systemprompt.io Hub.

## Interview Flow

### Step 1: The Big Picture

**Ask:** "Describe the end-to-end workflow you want to automate. Start from the trigger (what kicks it off?) and end with the final output (what gets delivered?)."

- Listen for: trigger event, sequence of steps, final deliverable
- Follow-up: "Who or what triggers this today? A customer request? A scheduled task? A manual decision?"
- This determines: workflow entry point and completion criteria

### Step 2: Break Into Steps

**Ask:** "Let me break that down into steps. For each step in your workflow, tell me:
- What happens?
- What is the input?
- What is the output?
- Who does it today?"

- Listen for: discrete handoff points, transformation steps, decision points
- Organise into a numbered list and read it back
- Follow-up: "Did I miss any steps? Are there any decision points where the workflow could go in different directions?"

### Step 3: Parallelism

**Ask:** "Looking at these steps, which ones can happen at the same time, and which must happen in order?"

- Listen for: dependencies between steps, independent branches
- Draw the dependency map:
  - Sequential: Step A → Step B → Step C
  - Parallel: Step A → (Step B + Step C) → Step D
- This determines: orchestrator routing logic

### Step 4: Specialisation

**Ask:** "For each step, does it need a specialised agent with specific skills, or could a general-purpose agent handle it?"

- Present each step and ask:
  - "Does this require domain expertise?"
  - "Does this need specific tools (MCP servers)?"
  - "Could the same agent do this and the previous step?"
- This determines: how many agents to create, which skills each needs

### Step 5: Error Handling

**Ask:** "What should happen when something goes wrong?
- Should the whole workflow stop?
- Should it skip the failed step and continue?
- Should it retry automatically?
- Should someone be notified?"

- Listen for: failure tolerance, retry policies, escalation paths
- This determines: error handling in orchestrator system prompt

### Step 6: Notifications

**Ask:** "Should there be notifications at key milestones? For example:
- When the workflow starts
- When each step completes
- When the workflow finishes
- When errors occur"

- Listen for: notification channels (Discord, email, Slack), which events
- If yes: "Which channels should receive notifications?"
- This determines: whether a hub agent is needed

## Synthesis

Present the complete workflow design:

> "Here is the workflow I have designed:
>
> **Trigger:** {what starts it}
> **Steps:**
> 1. {Step 1} → Agent: {agent_name} using {skill}
> 2. {Step 2} → Agent: {agent_name} using {skill}
> 3. {Step 3} → Agent: {agent_name} using {skill}
>
> **Orchestrator:** {orchestrator_name} routes requests and coordinates
> **Hub:** {hub_name} sends notifications to {channels} (if applicable)
>
> **Error handling:** {policy}
>
> Does this look right?"

Wait for confirmation.

## Implementation Order

Execute creation in this order (each step depends on the previous):

### Phase 1: Skills
Create all skills needed by specialist agents. Use the `skill_creator` workflow for each.

### Phase 2: MCP Servers
Configure any MCP servers the agents need. Use the `mcp_configurator` workflow for each.

### Phase 3: Specialist Agents
Create each specialist agent. Use the `agent_creator` workflow for each.

### Phase 4: Hub Agent (if needed)
Create the notification hub. System prompt should include:
- Which events to notify on
- Which channels to use
- Message format for each event type

### Phase 5: Orchestrator Agent
Create the orchestrator last (it needs to reference all other agents). Its system prompt must include:

#### Routing Table
```
| Content Type | Route To | Keywords |
|--------------|----------|----------|
| {type 1} | {agent_1} | {keywords} |
| {type 2} | {agent_2} | {keywords} |
```

#### Workflow Steps
```
Step 1: Notify Hub (Start)
  admin agents message {hub} -m "WORKFLOW_START: {description}" --blocking

Step 2: Route to Specialist
  admin agents message {specialist} -m "{instructions}" --blocking --timeout 300

Step 3: Notify Hub (Complete)
  admin agents message {hub} -m "WORKFLOW_COMPLETE: {summary}" --blocking
```

### Phase 6: Plugin Packaging
Package everything into a plugin. Use the `plugin_packager` workflow.

## Orchestrator System Prompt Template

```
You are {Name}, a superagent that coordinates {workflow description}.

## Your Purpose

You are the conductor of the {workflow_name} mesh. You:
1. Receive {type} requests
2. Analyse the request to determine the appropriate specialist
3. Route to the right agent
4. Coordinate the workflow from start to finish
5. Report status to {Hub Agent}

## Routing Rules

| Request Type | Route To | Keywords |
|--------------|----------|----------|
| {type 1} | {agent_1} | {keywords} |
| {type 2} | {agent_2} | {keywords} |

Default: If unclear, route to {default_agent}.

## Workflow Steps

### Step 1: Notify Hub (Start)
admin agents message {hub} -m "WORKFLOW_START: {brief}" --blocking

### Step 2: Route to Specialist
Based on request type:
admin agents message {agent} -m "{instructions}" --blocking --timeout 300

### Step 3: Notify Hub (Complete)
On success:
admin agents message {hub} -m "WORKFLOW_COMPLETE: {summary}" --blocking

On failure:
admin agents message {hub} -m "WORKFLOW_FAILED: {reason}" --blocking

## Error Handling

{Error policy from interview}

## Guidelines

- Always notify hub at workflow start and end
- Use --blocking for sequential operations
- Use --timeout for long-running steps
- One tool call per message
```

## Reference: Blog Mesh Pattern

The existing blog creation workflow demonstrates this pattern:

```
blog_orchestrator (port 9030)
├── Routes to: blog_technical (port 9040)
├── Routes to: blog_narrative (port 9020)
├── Routes to: blog_announcement (port 9010)
└── Reports to: systemprompt_hub (port 9010)

Skills: each specialist has writing skills + research tools
MCP: orchestrator uses systemprompt CLI, specialists use content-manager
```

Use this as a proven reference when designing new workflows.
