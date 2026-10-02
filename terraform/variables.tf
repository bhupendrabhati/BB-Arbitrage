variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "name_prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "bb-arbitrage"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "allowed_ssh_cidrs" {
  description = "CIDRs allowed to SSH to EC2"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "allowed_http_cidrs" {
  description = "CIDRs allowed to HTTP (80)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "allowed_https_cidrs" {
  description = "CIDRs allowed to HTTPS (443)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ami_id" {
  description = "Ubuntu AMI ID; leave empty to use latest Ubuntu 24.04"
  type        = string
  default     = ""
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 30
}

variable "volume_type" {
  description = "Root EBS volume type"
  type        = string
  default     = "gp3"
}

variable "app_dir" {
  description = "Directory to clone repo into on EC2"
  type        = string
  default     = "/home/ubuntu/apps/BB-Arbitrage"
}

variable "repo_url" {
  description = "Git repository URL"
  type        = string
  default     = "https://github.com/bhupendrabhati/BB-Arbitrage.git"
}

variable "repo_branch" {
  description = "Git branch to deploy"
  type        = string
  default     = "main"
}

variable "save_private_key" {
  description = "Save generated private key locally"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default = {
    Project     = "BB-Arbitrage"
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
