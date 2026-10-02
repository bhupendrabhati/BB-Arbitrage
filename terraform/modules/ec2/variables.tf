variable "name_prefix" { type = string }
variable "ami_id" {
  type    = string
  default = null
}
variable "instance_type" { type = string }
variable "subnet_id" { type = string }
variable "security_group_id" { type = string }
variable "key_name" { type = string }
variable "volume_size" { type = number }
variable "volume_type" { type = string }
variable "user_data" { type = string }
variable "tags" { type = map(string) }
