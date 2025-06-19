package main

import (
    "errors"
    "regexp"

    "cloud.google.com/go/s3"
)

// allS3BucketsSecure Deny rule for S3 buckets security
deny [
    msg = "Clear error message",
    description = "all s3 buckets secure",
    SOC2Compliance = true,
    ISO27001Compliance = true,
]

func main() {
    // Test the deny rule with a valid input
    if !isValidInput("my-bucket") {
        errors.New("invalid input")
    }
}