# Cost and security checklist

- [ ] AWS account owner approved any possible charges. Verify **current** AWS regional prices and Free Tier/credit eligibility before launch.
- [ ] Configure AWS Budget **actual and forecast alerts**, e.g. USD 2 and USD 5, with a working notification email. **Budgets are alerts, not spending caps; charges can exceed them.** Some budget features themselves may cost money.
- [ ] Check EC2 service quotas, ALB hourly and LCU charges, public IPv4 hourly charges, data transfer, CloudWatch monitoring and taxes. The project does **not** promise a particular cost.
- [ ] Avoid NAT Gateway, RDS, EKS, paid domains, WAF, cross-region replicas, provisioned databases, reserved capacity, and continuous load tests.
- [ ] Do not enable EC2 detailed monitoring, verbose log ingestion, or custom CloudWatch metrics unnecessarily.
- [ ] Use a dedicated IAM role with minimum permissions for a temporary stack; no root account and no committed keys.
- [ ] Public ALB is HTTP only: **no login, passwords, customer information, or payment processing**. Restrict `OperatorCidr` if practical.
- [ ] Limit ASG to max 2 and test client concurrency to max 20; run load only against your own resources.
- [ ] Plan a 30–60 minute supervised deployment window, but **billing is not guaranteed to stay below any amount**.
- [ ] Delete CloudFormation stack after testing; verify resource deletion and review billing later.
- [ ] Never screenshot account identifiers, billing personal details, access keys, or tokens for public GitHub.

## Cost model to put in report (replace with current AWS pricing)

Total = (EC2 instance-hours × EC2 rate) + (ALB hours × ALB hourly rate) + (ALB LCU-hours × LCU rate) + (public IPv4 address-hours × rate) + (data transfer and CloudWatch usage) + applicable taxes. Some AWS promotional credits may offset some charges; eligibility varies. For multi-region cost estimation, model both regional stacks, inter-region transfer, DNS health checks and shared-data replication, without deploying them.
