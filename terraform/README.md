# BB-Arbitrage Terraform Deployment

This Terraform code provisions the AWS infrastructure to run BB-Arbitrage on a single EC2 instance using Docker Compose (production setup).

## Prerequisites
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5.0
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) configured (`aws configure`) with permissions to create VPC, EC2, Security Groups, EIP, Key Pair
- Your public IP (to restrict SSH access)

## Quick Start
1. Copy example variables:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   ```
2. Edit `terraform.tfvars`:
   - Set `allowed_ssh_cidrs = ["YOUR_IP/32"]` (get from https://checkip.amazonaws.com/)
   - Optionally change `aws_region`, `instance_type`, `repo_branch`
3. Initialize:
   ```bash
   terraform init
   ```
4. Plan:
   ```bash
   terraform plan
   ```
5. Apply:
   ```bash
   terraform apply
   ```
   Type `yes` when prompted.
6. Save outputs (they show SSH command and public IP):
   ```bash
   terraform output
   ```

## Post-Provisioning
1. SSH into the instance:
   ```bash
   terraform output -raw ssh_command
   # or
   ssh -i bb-arbitrage-key.pem ubuntu@$(terraform output -raw public_ip)
   ```
2. The user data clones the repo, installs Docker, and prepares `.env` from `.env.example`. Complete `.env` with your secrets (POSTGRES_PASSWORD, SECRET_KEY). See `AWS-Guide.md` section 6.
3. Start the app:
   ```bash
   cd /home/ubuntu/apps/BB-Arbitrage
   docker compose -f docker-compose.prod.yml up -d
   docker compose -f docker-compose.prod.yml ps
   curl -s http://localhost/api/health/
   ```
4. Demo mode (after each restart): `curl -X POST http://localhost/api/demo/start`

## Notes
- Only ports 22 (SSH, restricted), 80 (HTTP), 443 (HTTPS) are open.
- An Elastic IP is created and attached.
- The private key is saved to `bb-arbitrage-key.pem` in the terraform directory (0600 permissions).
- To destroy everything: `terraform destroy`.
