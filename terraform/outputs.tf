output "instance_id" {
  description = "EC2 instance ID"
  value       = module.ec2.instance_id
}

output "public_ip" {
  description = "EC2 public IP address"
  value       = module.ec2.public_ip
}

output "public_dns" {
  description = "EC2 public DNS"
  value       = module.ec2.public_dns
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ${var.name_prefix}-key.pem ubuntu@${module.ec2.public_ip}"
}

output "key_pair_name" {
  description = "Key pair name"
  value       = aws_key_pair.this.key_name
}
