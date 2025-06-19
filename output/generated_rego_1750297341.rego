package main

# Description: all S3 buckets secure
# SOC2 Compliance: A.14.2.2
# ISO27001 Compliance: ISO27001_A.14.2.2

deny [
    input bucketName,
    input region,
    input acl,
    input tags
] {
    if !bucketName || !region || !acl || !tags then {
        error "Clear error message"
    }
} on bucketName, region, acl, tags