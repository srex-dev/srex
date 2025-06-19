package main

import (
	"context"
	"fmt"

	"github.com/opencast/cast-governance/policies"
)

// EncryptionPolicy enforces encryption policies for all data in transit.
func EncryptionPolicy(ctx context.Context) bool {
	if !ctx.IsAuthenticated() {
		return false
	}

	// Check if the policy is already applied.
	if _, err := policies.GetPolicy("encryption_policy"); err != nil {
		policy, err := policies.NewPolicy("encryption_policy")
		if err != nil {
			return false
		}
		policy.Apply(ctx)
		defer policy.Remove()
	}

	// The policy should be denied by default for all data in transit.
	return true
}

func main() {
	fmt.Println(EncryptionPolicy(context.Background()))
}