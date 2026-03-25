#!/usr/bin/env python3
"""
rate-limiter.py — Token bucket rate limiter for sequential command execution.

Usage:
  echo '["query1","query2"]' | python3 rate-limiter.py --rate 1 --command "python3 serp-parser.py"

  Reads list of inputs from stdin (JSON array of strings).
  Executes --command once per input, enforcing --rate requests/sec between calls.
  Aggregates stdout from each run into a JSON array on stdout.

Args:
  --rate FLOAT     Requests per second (default: 1.0)
  --command STR    Shell command to execute per input item
  --passthrough    If set, pass each input item as stdin to the command
"""

import argparse
import json
import shlex
import subprocess
import sys
import time


class TokenBucket:
    """Simple token bucket for rate limiting."""

    def __init__(self, rate: float):
        self.rate = max(0.01, rate)          # tokens per second
        self.capacity = 1.0                  # max burst = 1 token
        self.tokens = self.capacity
        self.last_refill = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def acquire(self):
        """Block until one token is available."""
        while True:
            self._refill()
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return
            wait = (1.0 - self.tokens) / self.rate
            time.sleep(wait)


def run_command(command: str, input_data: str) -> dict:
    """Execute command with input_data as stdin. Returns result dict."""
    try:
        # Split command string into argv list to avoid shell=True (command injection risk)
        cmd_args = shlex.split(command)
        proc = subprocess.run(
            cmd_args,
            shell=False,
            input=input_data.encode('utf-8'),
            capture_output=True,
            timeout=60
        )
        stdout = proc.stdout.decode('utf-8', errors='replace').strip()
        stderr = proc.stderr.decode('utf-8', errors='replace').strip()

        result = {
            'input': input_data[:200],
            'exit_code': proc.returncode,
            'stderr': stderr if stderr else None
        }

        if stdout:
            try:
                result['output'] = json.loads(stdout)
            except json.JSONDecodeError:
                result['output'] = stdout
        else:
            result['output'] = None

        return result

    except subprocess.TimeoutExpired:
        return {'input': input_data[:200], 'exit_code': -1, 'error': 'timeout'}
    except Exception as e:
        return {'input': input_data[:200], 'exit_code': -1, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='Token bucket rate limiter for sequential command execution'
    )
    parser.add_argument('--rate', type=float, default=1.0,
                        help='Requests per second (default: 1.0)')
    parser.add_argument('--command', type=str, required=True,
                        help='Shell command to execute per input item')
    parser.add_argument('--passthrough', action='store_true',
                        help='Pass each item as raw string (not JSON-encoded)')
    args = parser.parse_args()

    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({'error': 'No input provided on stdin'}), file=sys.stderr)
        sys.exit(1)

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON input: {e}'}), file=sys.stderr)
        sys.exit(1)

    if not isinstance(items, list):
        items = [items]

    bucket = TokenBucket(args.rate)
    results = []

    for i, item in enumerate(items):
        bucket.acquire()

        if args.passthrough:
            input_str = str(item)
        else:
            input_str = json.dumps(item, ensure_ascii=False)

        result = run_command(args.command, input_str)
        results.append(result)

        # Progress to stderr so stdout stays clean
        print(f'[rate-limiter] {i + 1}/{len(items)} done (exit={result["exit_code"]})',
              file=sys.stderr)

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
