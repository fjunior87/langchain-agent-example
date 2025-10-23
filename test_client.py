#!/usr/bin/env python3
"""
Simple test client for the Harness Pipeline Agent API.
Run this script to test the API endpoints.
"""

import requests
import json
import sys


API_BASE_URL = "http://localhost:8000"


def print_response(response):
    """Pretty print the API response."""
    print(f"\nStatus Code: {response.status_code}")
    print("-" * 80)
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    print("-" * 80)


def test_health():
    """Test the health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{API_BASE_URL}/health")
    print_response(response)
    return response.status_code == 200


def test_generate_pipeline():
    """Test pipeline generation."""
    print("\n=== Testing Pipeline Generation ===")
    payload = {
        "request": "Create a simple CI pipeline for a Python application with build and test stages"
    }
    response = requests.post(
        f"{API_BASE_URL}/api/v1/generate/pipeline",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response)
    return response.status_code == 200


def test_generate_connector():
    """Test connector generation."""
    print("\n=== Testing Connector Generation ===")
    payload = {
        "request": "Create a GitHub connector for a repository with OAuth authentication"
    }
    response = requests.post(
        f"{API_BASE_URL}/api/v1/generate/connector",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response)
    return response.status_code == 200


def test_query():
    """Test general query."""
    print("\n=== Testing General Query ===")
    payload = {
        "request": "What are the main components of a Harness pipeline?"
    }
    response = requests.post(
        f"{API_BASE_URL}/api/v1/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response(response)
    return response.status_code == 200


def main():
    """Run all tests."""
    print("=" * 80)
    print("Harness Pipeline Agent API - Test Client")
    print("=" * 80)

    tests = [
        ("Health Check", test_health),
        ("Pipeline Generation", test_generate_pipeline),
        ("Connector Generation", test_generate_connector),
        ("General Query", test_query),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Error: Could not connect to API at {API_BASE_URL}")
            print("Make sure the API server is running (python main.py or ./run.sh)")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error running {test_name}: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
