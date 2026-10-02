terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

module "vpc" {
  source = "./modules/vpc"

  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  azs                 = data.aws_availability_zones.available.names
  name_prefix         = var.name_prefix
  tags                = var.tags
}

module "security_group" {
  source = "./modules/security_group"

  name_prefix         = var.name_prefix
  vpc_id              = module.vpc.vpc_id
  allowed_ssh_cidrs   = var.allowed_ssh_cidrs
  allowed_http_cidrs  = var.allowed_http_cidrs
  allowed_https_cidrs = var.allowed_https_cidrs
  tags                = var.tags
}

resource "tls_private_key" "this" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "this" {
  key_name   = "${var.name_prefix}-key"
  public_key = tls_private_key.this.public_key_openssh
  tags       = var.tags
}

locals {
  user_data = templatefile("${path.module}/templates/user-data.sh.tpl", {
    app_dir  = var.app_dir
    repo_url = var.repo_url
    branch   = var.repo_branch
  })
}

module "ec2" {
  source = "./modules/ec2"

  name_prefix       = var.name_prefix
  ami_id            = var.ami_id != "" ? var.ami_id : null
  instance_type     = var.instance_type
  subnet_id         = module.vpc.public_subnet_ids[0]
  security_group_id = module.security_group.security_group_id
  key_name          = aws_key_pair.this.key_name
  volume_size       = var.volume_size
  volume_type       = var.volume_type
  user_data         = local.user_data
  tags              = var.tags
}

resource "local_file" "private_key" {
  count           = var.save_private_key ? 1 : 0
  content         = tls_private_key.this.private_key_pem
  filename        = "${path.cwd}/${var.name_prefix}-key.pem"
  file_permission = "0600"
}
