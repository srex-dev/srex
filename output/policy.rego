# description: All pods must have CPU and memory resource limits
# soc2: CC6.1
# iso27001: A.12.1.2

package main

deny contains reason if {
  input.kind == "Pod"
  some i
  c := input.spec.containers[i]
  not c.resources.limits.cpu
  reason := sprintf("Container %q is missing CPU limits", [c.name])
}

deny contains reason if {
  input.kind == "Pod"
  some j
  c := input.spec.containers[j]
  not c.resources.limits.memory
  reason := sprintf("Container %q is missing memory limits", [c.name])
}