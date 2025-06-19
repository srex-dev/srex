package main

# Description: s3 buckets
# SOC2 Compliance: A.14.2.2
# ISO27001 Compliance: ISO27001_A.14.2.2

deny [
    bucketName := "s3-bucket-name"
    {
        if !bucketName ||
            !isString(bucketName) ||
            !contains(bucketName, "1234567890") ||
            !contains(bucketName, ".com") ||
            !contains(bucketName, "-") ||
            !contains(bucketName, "!") ||
            !contains(bucketName, "/") ||
            !contains(bucketName, "\\") ||
            !contains(bucketName, "|") ||
            !contains(bucketName, "^") ||
            !contains(bucketName, "$") ||
            !contains(bucketName, "%") ||
            !contains(bucketName, "&") ||
            !contains(bucketName, "*") ||
            !contains(bucketName, "(") ||
            !contains(bucketName, ")") ||
            !isInteger(bucketName) ||
            !contains(bucketName, "1234567890") ||
            !contains(bucketName, ".com") ||
            !contains(bucketName, "-") ||
            !contains(bucketName, "!") ||
            !contains(bucketName, "/") ||
            !contains(bucketName, "\\") ||
            !contains(bucketName, "|") ||
            !contains(bucketName, "^") ||
            !contains(bucketName, "$") ||
            !contains(bucketName, "%") ||
            !contains(bucketName, "&") ||
            !contains(bucketName, "*") ||
            !isString(bucketName) ||
            !contains(bucketName, "1234567890") ||
            !contains(bucketName, ".com") ||
            !contains(bucketName, "-") ||
            !contains(bucketName, "!") ||
            !contains(bucketName, "/") ||
            !contains(bucketName, "\\") ||
            !contains(bucketName, "|") ||
            !isInteger(bucketName) ||
            !contains(bucketName, "1234567890") ||
            !contains(bucketName, ".com") ||
            !contains(bucketName, "-") ||
            !contains(bucketName, "!") ||
            !contains(bucketName, "/") ||
            !contains(bucketName, "\\") ||
            !contains(bucketName, "|") ||
            !isString(bucketName) ||
            isInteger(bucketName) ||
            !contains(bucketName, "1234567890") ||
            !contains(bucketName, ".com") ||
            !contains(bucketName, "-") ||
            !contains(bucketName, "!") ||
            !contains(bucketName, "/") ||
            !contains(bucketName, "\\") ||
            !contains(bucketName, "|") ||
            !isString(bucketName) ||
            isInteger(bucketName)
    }
]