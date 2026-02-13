# Agents Flashcards

> 共 77 张闪卡

---

## 卡片 1

**Q:** In the SAMAS architecture, which event-driven technology replaces the polling-based communication found in earlier multi-agent systems?

**A:** NATS JetStream.

---

## 卡片 2

**Q:** Why is NATS JetStream considered superior to Apache Kafka for autonomous agent 'interest-based' retention?

**A:** It retains messages only as long as active consumers are interested, matching the cognitive lifecycle of a task.

---

## 卡片 3

**Q:** Which specific memory technique prepends context strings to text chunks before indexing to improve retrieval precision?

**A:** Contextual Retrieval (Anthropic).

---

## 卡片 4

**Q:** The 'Rule of Two' for agent security allows a session to satisfy only two of which three properties simultaneously?

**A:** Access to private data, exposure to untrusted content, and external communication capability.

---

## 卡片 5

**Q:** In SiteGPT's 'Mission Control', what is the actual operational mechanism behind the perceived real-time interaction of 14 agents?

**A:** Staggered cron jobs creating one-shot isolated sessions every 15 minutes.

---

## 卡片 6

**Q:** Which consensus protocol technique requires agents to generate an initial solution independently before seeing others' work?

**A:** All-Agents Drafting (AAD).

---

## 卡片 7

**Q:** Why is WebAssembly (WASM) preferred over standard shell execution for agentic tool use in production?

**A:** It provides a sandboxed runtime to mitigate remote code execution risks from prompt injection.

---

## 卡片 8

**Q:** In the SagaLLM framework, what is the purpose of a 'compensating action'?

**A:** To restore the system to a consistent state by rolling back previous successful steps if a subsequent step fails.

---

## 卡片 9

**Q:** Which cost optimisation tool uses trained classifiers to route queries between 'strong' and 'weak' models?

**A:** RouteLLM.

---

## 卡片 10

**Q:** How does GraphRAG enhance multi-hop reasoning compared to standard vector search?

**A:** It traverses edges between entity nodes to find non-obvious relationships that vector embeddings might miss.

---

## 卡片 11

**Q:** What is the primary target of Phase 0 in the SAMAS implementation roadmap?

**A:** Deploying three hardcoded agents performing one impressive task to achieve time-to-first-value in under five minutes.

---

## 卡片 12

**Q:** Which orchestration framework is selected for SAMAS due to its support for cyclic graphs and native persistence (checkpoints)?

**A:** LangGraph.

---

## 卡片 13

**Q:** The 'Memory Curator' pattern is designed to solve which specific problem in multi-agent systems?

**A:** Conflicting agent knowledge by performing entity resolution and deduplication against a shared knowledge graph.

---

## 卡片 14

**Q:** According to ACL 2025 research, why does multi-agent debate often yield lower accuracy than simple voting protocols?

**A:** Extended discussion causes premature answer convergence, destroying the cognitive diversity that powers effective voting.

---

## 卡片 15

**Q:** In a confidence-weighted voting model, how is the final decision (final_answer) mathematically determined?

**A:** $argmax(\sum(confidence_{i} \times vote_{i}))$

---

## 卡片 16

**Q:** What is the specific risk associated with OpenClaw's 'local-first' execution model on a host machine?

**A:** Broad access to the host file system and shell creates a massive attack surface for prompt injection and malicious 'AgentSkills'.

---

## 卡片 17

**Q:** Which framework is used in SAMAS to replace static prompt strings with parameters that are mathematically tuned by an optimizer agent?

**A:** DSPy.

---

## 卡片 18

**Q:** What is the architectural role of a 'Guard Agent' in the Coordinator + Guard dual-agent security model?

**A:** Post-validating outputs to enforce format rules and block residual risks before delivery.

---

## 卡片 19

**Q:** Which technology allows Qdrant to manage thousands of private memories for different agents within a single collection?

**A:** Payload-based Partitioning (Multi-tenancy).

---

## 卡片 20

**Q:** The GEPA optimizer improves prompts by using LLMs to mathematically propose mutations based on what data?

**A:** Reflective feedback from successful and failed task execution traces.

---

## 卡片 21

**Q:** Why is the Model Context Protocol (MCP) used to connect agents to external tools in the SAMAS blueprint?

**A:** It decouples tool maintenance from agent logic, allowing standardised access control and easier API updates.

---

## 卡片 22

**Q:** In SiteGPT's topology, which agent acts as the 'Squad Lead' or project manager?

**A:** Jarvis.

---

## 卡片 23

**Q:** What is the primary disadvantage of OpenClaw's 'Lane Queue' system?

**A:** It defaults to serial execution, which blocks concurrent operations and severely limits system throughput.

---

## 卡片 24

**Q:** Which caching tier in SAMAS provides 100% savings on API costs when identical queries are intercepted?

**A:** Semantic caching (e.g., GPTCache).

---

## 卡片 25

**Q:** What is the purpose of the 'A2A Protocol' (Agent-to-Agent)?

**A:** To enable capability discovery and standard communication between disparate agent systems using JSON-based 'Agent Cards'.

---

## 卡片 26

**Q:** Which dashboard component is recommended for visualising live agent topology and message flows?

**A:** React Flow (or @xyflow/react).

---

## 卡片 27

**Q:** In the context of cost optimisation, why is prompt caching highly effective for 20+ agents?

**A:** Stable system prompts (SOPs) are shared across many agents, leading to high cache hit rates and 90% cost reductions on input.

---

## 卡片 28

**Q:** What 'autonomy slider' configuration is implemented for SAMAS agents?

**A:** Discrete levels (e.g. Low/Medium/High) mapped to specific Human-in-the-loop (HITL) interrupt triggers.

---

## 卡片 29

**Q:** The 'Collective Improvement' (CI) technique adds what specific step to the multi-agent consensus process?

**A:** Structured iterative refinement to prevent excessive or unguided communication.

---

## 卡片 30

**Q:** Why is self-hosting LLMs considered a 'trap' for most agent deployments below 100M tokens per month?

**A:** Managed APIs are significantly cheaper (60–700$\times$) than the hardware and operational costs of serving open-weight models.

---

## 卡片 31

**Q:** Which real-time database is used by Bhanu Teja P for his Mission Control dashboard?

**A:** Convex.

---

## 卡片 32

**Q:** In the SAMAS dashboard stack, which library is used for accessible, Tailwind-based UI primitives?

**A:** shadcn/ui.

---

## 卡片 33

**Q:** What trigger should cause an agent system to automatically escalate a task to a human operator?

**A:** Average confidence across voting agents falls below a specific threshold (e.g. 40%).

---

## 卡片 34

**Q:** The 'SagaLLM' approach ensures reliability by decomposing complex goals into what kind of units?

**A:** Atomic steps with defined forward actions and reversible states.

---

## 卡片 35

**Q:** Which OpenClaw file serves as the core instruction set for an agent's personality and 'soul'?

**A:** SOUL.md.

---

## 卡片 36

**Q:** How does the 'Competitive Swarming' pattern work within NATS JetStream?

**A:** A request is broadcast (Fan-Out) to multiple agents, and a 'Judge' agent selects the best generated variation.

---

## 卡片 37

**Q:** Which technology provides hardware-level isolation for agents while maintaining millisecond startup times?

**A:** Firecracker MicroVMs.

---

## 卡片 38

**Q:** What is the function of the 'MIPROv2' optimizer in the DSPy framework?

**A:** It mathematically proposes multi-step instructions to maximise a success metric based on a training dataset.

---

## 卡片 39

**Q:** Which specific risk did OpenClaw encounter shortly after reaching 100k stars on GitHub?

**A:** The proliferation of malicious skills (11.3% of the marketplace) due to an uncurated registry.

---

## 卡片 40

**Q:** In the context of multi-agent memory, what are 'multi-resolution summaries'?

**A:** Global summaries paired with agent-specific fine-grained logs to prevent information overload.

---

## 卡片 41

**Q:** Which consensus model routes factual verification tasks differently than strategic reasoning tasks?

**A:** Adaptive protocol selector.

---

## 卡片 42

**Q:** How does LiteLLM facilitate cost management in enterprise agent swarms?

**A:** It acts as a self-hosted gateway with routing strategies, usage-based budgets, and automatic retries.

---

## 卡片 43

**Q:** What is the primary benefit of the 'Agent-to-Agent' (A2A) JSON manifest?

**A:** It allows an orchestrator to dynamically 'hire' agents based on their advertised capabilities and inputs.

---

## 卡片 44

**Q:** Which specific database is recommended for low-latency thread-level persistence in LangGraph?

**A:** Redis.

---

## 卡片 45

**Q:** In the SAMAS security model, what is 'Provenance Ledger' tracking?

**A:** Data origin and trust levels across agents to detect indirect prompt injection.

---

## 卡片 46

**Q:** What is the 'martingale' concern in NeurIPS 2025 research regarding multi-agent debate?

**A:** Debate induces belief trajectories that don't improve correctness without specific corrective update interventions.

---

## 卡片 47

**Q:** Which OpenClaw tool enables a 'Live Canvas' visual workspace?

**A:** A2UI.

---

## 卡片 48

**Q:** What distinguishes 'Agentic Plan Caching' from standard prompt caching?

**A:** It caches structured execution plans from completed runs to reduce latency and cost for recurring task types.

---

## 卡片 49

**Q:** Why is 'Diversity' of model architectures considered essential for multi-agent voting?

**A:** Homogeneous agents (using the same model) tend to hallucinate in similar patterns, reducing the error-correction benefit of voting.

---

## 卡片 50

**Q:** In the OpenClaw Gateway, what is the 'main' session's default security privilege?

**A:** Full access to the host machine (tools run on the host).

---

## 卡片 51

**Q:** Which specific protocol standardises 'RUN_STARTED' and 'RUN_FINISHED' events for agent-to-frontend communication?

**A:** AG-UI (from CopilotKit).

---

## 卡片 52

**Q:** What does the 'A-HMAD' framework use to reduce factual errors by 30%?

**A:** Dynamic routing that activates specific agent subsets based on the query type.

---

## 卡片 53

**Q:** In SiteGPT's squad, what is the role of the agent named 'Friday'?

**A:** Development.

---

## 卡片 54

**Q:** What is the primary advantage of the 'Recursive Hierarchical Supervisor' pattern for 20+ agents?

**A:** It prevents the top-level orchestrator from becoming a processing bottleneck by delegating to domain-specific sub-teams.

---

## 卡片 55

**Q:** Which specific tool is used by SAMAS to process asynchronous text and extract entities for the knowledge graph?

**A:** Curator Agent.

---

## 卡片 56

**Q:** What is the recommended layout algorithm for automatically positioning nodes in an agent dashboard topology?

**A:** Dagre or ELK.

---

## 卡片 57

**Q:** Which agent type in the GaaS framework implements hard blocks on prohibited actions?

**A:** Coercive enforcement mode.

---

## 卡片 58

**Q:** What defines the 'Active' state in the research-supported agent lifecycle?

**A:** An agent that is currently available and actively processing events or tasks.

---

## 卡片 59

**Q:** Which specific benefit does Anthropic's 'Prompt Caching' offer for recurring input blocks?

**A:** A 90% reduction in input costs for cache hits.

---

## 卡片 60

**Q:** What is the role of the 'Evolution Agent' in the SAMAS infrastructure?

**A:** To run weekly GEPA optimization against production traces and mathematically tune agent instructions.

---

## 卡片 61

**Q:** Which OpenClaw command is used to troubleshoot risky or misconfigured DM policies?

**A:** openclaw doctor

---

## 卡片 62

**Q:** What does the 'AgentSpawn' paper propose to improve task completion rates during dynamic agent creation?

**A:** Automatic memory transfer and adaptive spawning policies.

---

## 卡片 63

**Q:** Which specific React library is recommended for implementing a Kanban task board for agents?

**A:** dnd-kit.

---

## 卡片 64

**Q:** In the context of the SAMAS nervous system, what is 'Queue Group' load balancing?

**A:** Distributing tasks across multiple identical specialist agents (e.g. three 'Friday' developers) to handle spikes.

---

## 卡片 65

**Q:** Which language is used for defining agent SOPs (roles, goals, backstories) in the SAMAS repository?

**A:** YAML.

---

## 卡片 66

**Q:** What is 'Semantic Search' fusion in OpenClaw's memory architecture?

**A:** Combining semantic similarity (sqlite-vec) with keyword matching (FTS5/BM25).

---

## 卡片 67

**Q:** In the SAMAS dashboard, which tool provides deep distributed tracing for agent reasoning loops?

**A:** LangFuse (or Arize Phoenix).

---

## 卡片 68

**Q:** How does 'Staggered Cron' help maintain low operational costs in SiteGPT's multi-agent system?

**A:** It ensures that most agents consume zero VPS resources between their specific 15-minute heartbeats.

---

## 卡片 69

**Q:** Which OpenClaw feature allows a user to control the agent via WhatsApp or Telegram?

**A:** The Gateway Pattern (Multi-channel inbox).

---

## 卡片 70

**Q:** What is the 'All-Agents Drafting' (AAD) impact on reasoning tasks?

**A:** A 3.3% improvement in accuracy by ensuring independent initial thought.

---

## 卡片 71

**Q:** Which security tier in the SAMAS authority model requires manual approval for most actions?

**A:** Intern tier.

---

## 卡片 72

**Q:** What distinguishes the SAMAS 'Push-Based Swarm Topology' from SiteGPT's 'Mission Control'?

**A:** Agents react instantly to NATS events rather than waiting for the next 15-minute polling tick.

---

## 卡片 73

**Q:** Which specific model is recommended by Peter Steinberger for long-context strength in OpenClaw?

**A:** Anthropic Claude Pro/Max (Opus 4.6).

---

## 卡片 74

**Q:** In LangGraph, what is the 'interrupt()' mechanism used for?

**A:** Enforcing Human-in-the-loop (HITL) approval by pausing execution during high-risk tool calls.

---

## 卡片 75

**Q:** What is the significance of the 'Wait for round 3' findings in ReConcile research?

**A:** Consensus protocols generally converge within three rounds, making further debate rounds computationally inefficient.

---

## 卡片 76

**Q:** Which component in OpenRAG handles the intelligent identification and extraction of PDF tables?

**A:** Docling.

---

## 卡片 77

**Q:** How does 'Confidence-weighted voting' handle a disagreement between a highly accurate agent and a low-accuracy agent?

**A:** The historical accuracy weight of the agents is multiplied by their current confidence to recalibrate the final vote.

