# description: Ensure all S3 buckets have versioning enabled and encryption at rest
# soc2: CC6.1, CC6.2
# iso27001: A.8.2.3, A.10.1.1

package main

deny[msg] if {
    bucket := input.resources[_]
    bucket.type == "aws_s3_bucket"
    not bucket.versioning_enabled
    msg := sprintf("S3 bucket %s does not have versioning enabled", [bucket.name])
}

deny[msg] if {
    bucket := input.resources[_]
    bucket.type == "aws_s3_bucket"
    not bucket.server_side_encryption_configuration
    msg := sprintf("S3 bucket %s does not have encryption at rest configured", [bucket.name])
}
