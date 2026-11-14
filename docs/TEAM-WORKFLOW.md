\# Team Workflow \& Governance



\## Ownership split (authoring work, NOT product structure)

\- US (admin + core): catalog #1-50.

\- TEAM: catalog #51-100.

Divisions/packs remain user-composable; this split is only about who AUTHORS role definitions.



\## Team batches (5 roles each; 10 batches)

| Batch | Roles (#) | Names |

|---|---|---|

| B1 | 51-55 | SecurityAuditor, PenTester, CryptographyAdvisor, PrivacyOfficer, ComplianceAnalyst |

| B2 | 56-60 | LicenseAuditor, IncidentResponder, ThreatModeler, AccessController, AuditLogger |

| B3 | 61-65 | Bookkeeper, BudgetAnalyst, ExpenseTracker, InvoiceClerk, PayrollAssistant |

| B4 | 66-70 | TaxPreparer, AssetRegistrar, PortfolioAnalyst, RiskAssessor, FinanceReporter |

| B5 | 71-75 | GeoResearcher, ClimateAnalyst, WeatherForecaster, GISMapper, HydrologyAnalyst |

| B6 | 76-80 | SeismologyAnalyst, EcologyAnalyst, AgricultureAdvisor, DisasterModeler, EnvironmentalReporter |

| B7 | 81-85 | PhysicsSimulator, ChemistrySimulator, MechanicalSimulator, AerospaceSimulator, CivilStructuralSimulator |

| B8 | 86-90 | BiologicalSimulator, EpidemiologyModeler, EconomicsModeler, TrafficSimulator, EnergySystemsModeler |

| B9 | 91-95 | ProjectManager, ProductManager, ScrumMaster, HRCoordinator, Recruiter |

| B10 | 96-100 | CustomerSupport, SalesStrategist, MarketingAnalyst, SupplyChainAnalyst, ExecutiveBriefer |



Guardrails: B1-B4 (security/finance) and B7-B8 (simulation) MUST include read\_only / requires\_approval / illustrative fields and admin sign-off.



\## Onboarding (every member, once)

1\. Install GitHub Desktop: https://desktop.github.com/

2\. Sign in with your GitHub account.

3\. Clone: File > Clone repository > URL > https://github.com/Ringga999/local-stratofly

4\. Ask admin (Ringga) in WA to be added as Collaborator (Write access). Wait for confirmation.

5\. Read CONTRIBUTING.md + ROLE-CATALOG-100.md + this file.

6\. Local setup: python -m venv venv; venv\\Scripts\\activate; pip install -r requirements.txt; python main.py serve.



\## Per-batch loop (the gate)

1\. Claim: comment on the batch issue; admin assigns it to you.

2\. Branch: in GitHub Desktop create `feature/team-batch-<n>` (e.g. feature/team-batch-1).

3\. Author the 5 role JSONs (+ persona + blueprint cells). Additive only.

4\. Local gate: serve + verify with your own eyes + clean-clone test.

5\. Commit locally (GitHub Desktop): `feat(team): batch <n> roles <a>-<b>`.

6\. Push the BRANCH (Publish branch). Main is protected; you cannot push main directly.

7\. Open Pull Request; request review from @Ringga999.

8\. WA admin: "batch <n> ready, PR #<x>". Admin reviews, approves, merges.

9\. Admin confirms in WA; only then is the batch "in". Next batch unlocked.



\## Definition of Done (PR checklist)

\- \[ ] 5 role JSONs valid (name, persona, capabilities, tools, modules)

\- \[ ] Guardrail fields present for sensitive roles

\- \[ ] Blueprint cells added; status flipped to done in same PR

\- \[ ] Local gate passed (serve + own eyes + clean-clone)

\- \[ ] No .env / settings.json / memory.sqlite3 committed

\- \[ ] AI-dev protocol followed (raw feed, verified anchors, human gate)



\## Communication

\- WA group for coordination; batch issues for claims; PR for code review.

\- Admin review SLA: <= 24h. Blocked? Ping admin, don't force-push.

