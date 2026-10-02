variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "allowed_ssh_cidrs" { type = list(string) }
variable "allowed_http_cidrs" { type = list(string) }
variable "allowed_https_cidrs" { type = list(string) }
variable "tags" { type = map(string) }
