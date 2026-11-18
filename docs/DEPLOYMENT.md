# Deployment runbook (one designated AWS operator)

**Prerequisites:** approved AWS account, CLI authenticated with limited permissions, permission to use ALB/ASG/EC2/CloudFormation, service quota for 2 EC2 instances, budget alert configured and acknowledged, prices checked for selected region. Never share access keys, passwords, or `.aws` files on GitHub. Verify the chosen instance type is supported and any Free Tier eligibility **for your specific account**. No need to create an SSH key pair.

1. Run `python -m unittest discover -s tests -v` locally.
2. Run `python scripts/generate_template.py` locally after app edits (`pip install pyyaml` if missing). Commit the generated template together with the code.
3. Run `aws cloudformation validate-template --template-body file://infra/zomato-stack.yaml --region ap-south-1`.
4. Review estimated service costs, then deploy during a **short supervised lab window**:
   `aws cloudformation deploy --stack-name zomato-lab --template-file infra/zomato-stack.yaml --region ap-south-1 --parameter-overrides MaxCapacity=2`
   Optionally add `OperatorCidr=YOUR_PUBLIC_IPV4/32` to limit access; confirm your network public IP first. This demo serves **unencrypted HTTP**.
5. Retrieve ALB DNS: `aws cloudformation describe-stacks --stack-name zomato-lab --region ap-south-1 --query 'Stacks[0].Outputs'`.
6. Wait for target group health = healthy (initial bootstrap may take several minutes). Open ALB URL and `/health`.
7. Capture console screenshots: stack resources, ALB listener/target group, ASG desired/min/max, EC2 instance count, CPU and request metrics, scaling policy and activity. Redact account IDs and sensitive data.
8. **1-instance baseline:** ensure 1 healthy target, run `python scripts/load_test.py --url http://YOUR-ALB-DNS --requests 100 --workers 5 --output evidence/one-instance.csv`. Record actual healthy instance count.
9. **2-instance experiment:** AWS Console > EC2 > Auto Scaling Groups > your group > Edit > Desired capacity 2 (Max already 2). Wait until **2 healthy targets**; repeat **identical** test to `evidence/two-instances.csv`. Note that low traffic may show no improvement; report real results, not assumed improvement.
10. For optional automatic scaling evidence, restore desired 1, allow cooldown, then run a **bounded, supervised** CPU test for several minutes while observing CloudWatch CPU and scaling activity. No guarantee the policy will trigger in a short window. Stop if costs or errors rise.
11. Combine measured CSV rows into `evidence/combined.csv` (same header, fill `instance_count_observed_manually` with measured 1/2); plot with `python scripts/plot_results.py evidence/combined.csv evidence/latency.png`. Screenshot CloudWatch timestamps corresponding to both experiments.
12. **Delete immediately:** `aws cloudformation delete-stack --stack-name zomato-lab --region ap-south-1` then `aws cloudformation wait stack-delete-complete --stack-name zomato-lab --region ap-south-1`. Verify stack gone, EC2 terminated, ALB and target group deleted, and no stray billable resources. Check billing again next day (charges may post later).

**No one else should deploy another copy.** Use a single shared AWS demo operated by one authorized member; other members contribute code, measurements, documentation, and evidence through GitHub.
