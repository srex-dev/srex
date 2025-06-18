#!/usr/bin/env python3
"""
Test script to verify the dicts_with_numeric_keys_to_lists function.
"""

def dicts_with_numeric_keys_to_lists(obj):
    """Convert dicts with only numeric keys to lists."""
    if isinstance(obj, dict):
        # If all keys are numeric, convert to list
        if all(str(k).isdigit() for k in obj.keys()) and obj:
            # Sort keys numerically and convert to list
            sorted_keys = sorted(obj.keys(), key=lambda x: int(x))
            result = [dicts_with_numeric_keys_to_lists(obj[k]) for k in sorted_keys]
            return result
        else:
            # Recursively process all values
            return {k: dicts_with_numeric_keys_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dicts_with_numeric_keys_to_lists(v) for v in obj]
    else:
        return obj

# Test cases
test_cases = [
    {
        "name": "Simple numeric keys",
        "input": {"0": {"name": "test"}, "1": {"name": "test2"}},
        "expected": [{"name": "test"}, {"name": "test2"}]
    },
    {
        "name": "Nested numeric keys",
        "input": {"slo": {"0": {"name": "test"}, "1": {"name": "test2"}}},
        "expected": {"slo": [{"name": "test"}, {"name": "test2"}]}
    },
    {
        "name": "Mixed keys",
        "input": {"slo": {"0": {"name": "test"}, "1": {"name": "test2"}, "other": "value"}},
        "expected": {"slo": {"0": {"name": "test"}, "1": {"name": "test2"}, "other": "value"}}
    },
    {
        "name": "Clean data",
        "input": {"slo": [{"name": "test"}, {"name": "test2"}]},
        "expected": {"slo": [{"name": "test"}, {"name": "test2"}]}
    }
]

def test_conversion():
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        result = dicts_with_numeric_keys_to_lists(test_case['input'])
        print(f"Result: {result}")
        print(f"Expected: {test_case['expected']}")
        print(f"Match: {result == test_case['expected']}")

if __name__ == "__main__":
    test_conversion() 