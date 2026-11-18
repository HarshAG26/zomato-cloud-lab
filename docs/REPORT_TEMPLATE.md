# Ten-page case-study report outline (fill with real sources and measurements)

1. Cover page: title, course, three members, dates, contributions.
2. Case-study introduction: Zomato traffic peaks and requirements. **Cite independently verified public sources**; do not claim the demo reproduces Zomato's proprietary architecture.
3. Problem statement: request bursts, routing, scaling, latency, availability, budget constraints.
4. Public-source research: source URLs, publication dates, confirmed facts vs assumptions.
5. Target architecture diagram: two-region conceptual design, routing, failover, consistency, security.
6. Implemented architecture diagram: one region, two AZs, ALB, ASG, EC2, CloudWatch; service choices and tradeoffs.
7. Deployment steps: CloudFormation template, health check, scaling policy, screenshots.
8. Experiment methodology: fixed requests/workers, baseline and two-instance test, measurement timestamps, real healthy target count.
9. Results: real CSV, response time vs instance count plot, CloudWatch CPU/ASG events, estimated/actual cost (label each), limitations.
10. Conclusion, lessons, AWS cleanup confirmation, references and three-member daily Git commit links.

## Measurement table (do not invent values)

| Test | Requests | Workers | Healthy EC2 targets | Mean latency (ms) | P95 latency (ms) | Errors | Evidence |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | TBD | TBD | 1 (verify) | TBD | TBD | TBD | screenshot/CSV |
| Scale comparison | same | same | 2 (verify) | TBD | TBD | TBD | screenshot/CSV |

## Assignment mapping

- Week 1: research summary and salient points -> sections 2, 4.
- Week 2: 10-page analysis, architecture diagram, roles -> sections 1–6, 10.
- Week 3: implement, load-test, latency/scaling/cost measurements -> sections 7–9.
- Week 4: finalize report and submission -> completed report and evidence.
- Week 5: viva -> explain architecture, demo, measured results, costs and limitations.

**Extra optional exercise (not required for Zomato's assigned category):** compare modeled cloud costs using pricing calculators. Serverless function, lift-and-shift migration, and government-platform exercises are separate categories in the PDF, not mandatory for this selected case.
