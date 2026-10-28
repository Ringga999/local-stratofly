# ROLE-BLUEPRINT-SPEC v1 (Product Spec + Post-Demo Dev Blueprint)

Status: DESIGN FROZEN. Do not implement before Monday demo is complete.
Home: this file lives in local-stratofly/docs/ (product spec), NOT the journal.
Core Principle: each role is a CAPABILITY PROFILE, not a separate engine.
All roles share the same machinery (provider_hub, memory, settings, model_kind).

## OVERVIEW: 2 perpendicular axes
Axis 1 - DIVISION (where the agent works): Engineering, Security, Content,
  Operations, Community, Marketing.
Axis 2 - ROLE (what the brain is good at): Solver, Architect, Crafter,
  Analyst, Communicator, Sentinel, Operator.
Each role = expertise, tasks, outputs, commands, speciality, abilities,
  privileges, tools, persona_hint, example_use_case, ui_modules.

## ROLE 1: SOLVER (The Orchestrator)
Expertise: complex problem decomposition; multi-agent orchestration; synthesis
  of diverse inputs (text, PDF, images, links); what-if simulation.
Tasks: receive raw materials + user prompt; break into sub-tasks; delegate to
  other agents (Crafter = code, Analyst = research); synthesize; simulate
  before execution; order revisions.
Outputs: structured solutions; delegation reports; simulation results; drafts.
Commands: /solve <prompt>+attachments; /delegate <agent> <task>; /simulate
  <scenario>; /revise <agent> <feedback>.
Speciality: ONLY role with SUPERVISION rights; absorbs multi-modal inputs;
  holds context across multi-step workflows.
Abilities: task decomposition; cross-agent coordination; QA via revision;
  draft-first delivery.
Privileges: supervise; read_all_divisions (with grant); draft_first.
Tools: task-solving; supervise; simulate; absorb.
Persona: decisive, structured, asks-before-acting. Thinks in systems.
Example: user must write a product whitepaper but lacks time and expertise ->
  uploads 3 example PDFs + a brief -> Solver absorbs structure (vision),
  decomposes into sections, delegates Crafter (technical) + Analyst (data),
  runs a what-if simulation on target audience, presents a draft via Telegram
  for approval.

## ROLE 2: ARCHITECT (The Forest-Viewer)
Expertise: system-level design; principle-conflict detection; redesign with
  trade-off analysis; long-term technical vision.
Tasks: audit repo structure; detect architectural debt; propose redesigns;
  review PRs for fit; maintain vision docs.
Outputs: audit reports; redesign proposals (diagrams in markdown);
  principle-violation flags; vision docs.
Commands: /audit <repo|module>; /propose <change>; /review_pr <n>; /vision <topic>.
Speciality: sees the forest; reasons about abstract principles and trade-offs.
Abilities: structure analysis; principle enforcement; trade-off reasoning;
  long-term planning.
Privileges: read_structure; propose_change (cannot execute).
Tools: read_structure; propose_change.
Persona: thoughtful, principled, asks why before how.
Example: module X becomes a god-object with 50 deps -> /audit module_X ->
  flags 3 violations -> proposes split into 3 micro-modules -> presents the
  trade-off (2 weeks refactor vs 6 months debt) -> user delegates to Crafter.

## ROLE 3: CRAFTER (The Technical Hands)
Expertise: code writing, refactoring, debugging; tests; PRs; CI/CD.
Tasks: write code from spec; refactor; debug; write and run tests; open PRs;
  review PRs for code quality (not architecture).
Outputs: code files; test suites; PRs; bug-fix proposals; review comments.
Commands: /write <spec>; /refactor <file|module>; /debug <issue>; /test <module>;
  /pr <branch>.
Speciality: reasons about behavior not just syntax; TDD mindset.
Abilities: code generation; refactoring; debugging; test writing.
Privileges: write_code; run_tests; create_pr.
Tools: write_code; run_tests; create_pr.
Persona: precise, pragmatic, ships working code; prefers simple over clever.
Example: spec POST /api/settings, validate schema, save -> Crafter writes the
  endpoint + 3 unit tests -> runs tests (pass) -> opens a PR -> Sentinel checks
  security, Architect checks fit, both approve.

## ROLE 4: ANALYST (The Eyes and Synthesizer)
Expertise: web research; document absorption (PDF/images via vision); data
  synthesis; cited reporting.
Tasks: research topics; summarize documents; analyze trends; generate insight
  reports; monitor metrics and flag anomalies.
Outputs: research reports (cited); document summaries; data analyses; insight
  briefs; text dashboards.
Commands: /research <topic>; /summarize <doc>; /analyze <data>; /insight <q>;
  /monitor <metric>.
Speciality: processes large info volume fast; extracts signal; cites everything;
  uses vision to read docs.
Abilities: web research; document absorption; data analysis; report generation.
Privileges: read_web; read_file; produce_report.
Tools: read_web; read_file; produce_report.
Persona: curious, thorough, cites everything; asks what the data says first.
Example: agent response times rose -> /analyze agent_response_times 7d ->
  pulls memory data, finds 3 spikes -> correlates with model fallbacks ->
  report times +40 percent due to 3 fallback events -> recommends adding
  nemotron as secondary in WORKHORSE -> user delegates to Crafter.

## ROLE 5: COMMUNICATOR (The Public Voice)
Expertise: drafting posts, threads, DMs, devlogs; tone matching; mention
  monitoring; sensitive escalation.
Tasks: draft social posts; write devlogs and changelogs; monitor mentions and
  draft replies; escalate sensitive issues; enforce community guidelines.
Outputs: draft posts; devlogs; reply drafts; escalation reports; sentiment
  summaries.
Commands: /draft_post <topic> <platform>; /devlog <period>; /reply <mention>;
  /escalate <issue>; /community_health.
Speciality: knows platform norms and brand voice; judges escalate vs handle.
Abilities: draft generation; tone matching; mention monitoring; escalation
  judgment.
Privileges: draft_first (ALL outputs are drafts until user approves);
  send_for_approval; monitor_mentions.
Tools: draft; send_for_approval; monitor_mentions.
Persona: diplomatic, brand-aware, never posts without approval.
Example: major feature shipped -> /draft_post launch X -> 3-thread draft ->
  sent to user via Telegram -> user wants a more technical tone -> revised ->
  approved -> scheduled (manual publish by user).

## ROLE 6: SENTINEL (The Shield)
Expertise: security audit; dependency and CVE tracking; breaking-change
  detection; compliance.
Tasks: audit code for vulns; scan deps for CVEs; detect API/SDK drift; enforce
  best practices; generate security reports.
Outputs: audit reports; CVE alerts (severity + fix); breaking-change warnings;
  compliance checklists; recommendations.
Commands: /audit_security <scope>; /scan_deps; /detect_breaking <api|sdk>;
  /compliance <standard>; /security_report.
Speciality: OWASP knowledge; tracks CVE advisories; reasons about security
  impact of changes.
Abilities: vuln detection; CVE tracking; breaking-change analysis; compliance.
Privileges: read_security; flag_change; block_merge (recommend only).
Tools: read_security; flag_change; cve_tracker.
Persona: vigilant, cautious, assumes the worst; asks what could go wrong.
Example: Crafter PR bumps a dep v1.2 to v2.0 -> Sentinel sees an auth breaking
  change + 2 medium CVEs in v1.2 -> flags update auth code, block until fixed ->
  Crafter updates -> Sentinel re-reviews -> approves.

## ROLE 7: OPERATOR (The Clock)
Expertise: scheduled routines; handoff coordination; pipeline management;
  consistency over creativity.
Tasks: run scheduled routines (patrol, CI, release); coordinate handoffs
  (Scout to Triage to Crafter); monitor pipeline health; maintain consistency;
  execute repetitive tasks reliably.
Outputs: execution logs; handoff reports; pipeline health; ops summaries;
  failure alerts.
Commands: /run_routine <name>; /handoff <from> <to> <ctx>; /pipeline_health;
  /ops_summary <period>; /alert <issue>.
Speciality: reliable repetition; understands workflow dependencies and sequence.
Abilities: routine execution; handoff coordination; pipeline monitoring;
  alert generation.
Privileges: run_routine; handoff; alert.
Tools: run_routine; handoff; pipeline_monitor.
Persona: reliable, consistent, never misses a beat; asks is this on schedule.
Example: 6 AM daily patrol -> /run_routine daily_patrol -> coordinates Scout
  scan, Triage categorize, Crafter fix simple -> monitors CI green ->
  ops_summary 5 triaged, 2 fixed, CI green -> Telegram to user -> user approves
  release -> /run_routine release_pipeline.

## UI / NAVIGATION BLUEPRINT (per-role workspace, the tidy layer)
Principle: ONE page per agent, but the layout is MODULAR by role. A user never
  sees a field or button irrelevant to that agent role. This turns a generic
  messy form into a tidy professional workspace.
Navigation flow:
  Live Crew grid --click card--> Agent Detail Page (role-aware) --back--> grid.
  Create Agent: pick ROLE in the dropdown FIRST -> once created, the detail
  page is already configured for that role.
Agent Detail Page = FIXED frame + ROLE-SPECIFIC MODULE SLOTS.
  Fixed frame (all roles): id, division, role badge, brain + model-kind badge,
    autonomy and enabled toggle, cadence, back button.
  Module slots (only the relevant ones render):
    SOLVER: multi-modal upload (drag PDF, image, link); complex prompt;
      delegation board (sub-task to agent, status); simulation runner;
      draft approval queue.
    ARCHITECT: repo or module selector; audit report viewer; dependency graph
      (text); redesign proposal editor.
    CRAFTER: spec input; code diff viewer; test runner + results; PR creator.
    ANALYST: topic or document input; source list with citations; trend chart
      (text); report generator.
    COMMUNICATOR: platform selector (X, LinkedIn, devlog); tone selector;
      draft composer; approval queue + Telegram send; mention monitor.
    SENTINEL: scope selector; CVE dashboard; breaking-change flags; compliance
      checklist; block-merge recommendation.
    OPERATOR: routine list + run buttons; handoff timeline; pipeline health;
      ops summary generator; alert log.
Why this is tidy: a Solver never sees the Communicator tone selector and vice
  versa; each agent feels like a PROFESSION with its own toolkit, not one
  giant toolbox for everyone.
Role Gallery (pre-creation): in Create Agent, before finalizing, the user can
  preview the role to see which modules this agent will get. This sells
  role = capability.
Technical implementation (post-demo):
  - app.html: add a hash route #agent/<id> that fetches /api/agent/<id>.
  - New endpoint /api/agent/<id> returns config, role, modules list,
    recent_events list, memory list (merge settings + memory + role map).
  - Each role module = a JS component rendered conditionally on the role.
  - This answers different page per agent AND tailored to role at once.
UI guardrail: no module may invoke a tool outside its role privileges (only
  Solver gets the delegation board; only Communicator gets the post approval
  queue). The UI mirrors rights, never exceeds them.

## IMPLEMENTATION PRIORITY (post-demo)
Phase 1 (Tue): role field in agent config (already in settings.py); wire role
  to preferred_kinds filtering in the wizard; role-specific tool availability.
Phase 2 (Wed): Solver orchestration (multi-agent delegation); /solve with
  attachments; Communicator draft-first workflow; Agent Detail Page frame +
  hash route + /api/agent/<id>.
Phase 3 (Thu): role module slots per role (the tidy layer); Sentinel CVE
  integration; Architect structure analysis; Operator routine scheduler.

## GUARDRAILS
1. Roles are METADATA, not separate engines; all share provider_hub, memory,
  settings.
2. Supervision rights exist ONLY for Solver, only when the user creates one.
3. Draft-first is sacred for Communicator: never auto-post without approval.
4. Sentinel flags or blocks but cannot auto-fix (that is Crafter work).
5. Operator runs routines but cannot modify routine definitions (user job).
6. UI modules must never exceed a role privileges (mirror rights, not more).
