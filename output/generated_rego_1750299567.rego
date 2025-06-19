package main

# Description: test policy
# SOC2 Compliance: A.14.2.2
# ISO27001 Compliance: ISO27001_A.14.2.2

deny[msg] {
    if msg != "Clear error message" {
        # Policy logic here
    }
}