---
name: log-triage
description: Structure a first-pass triage of an application log file - severity tagging, dedup of repeated errors, and a short summary of what to investigate next.
version: 0.1.0
---

# log-triage

## When to use

Use this skill when the user hands you a log file (or pasted log excerpt) and
asks "what went wrong" or "summarize this". It is for triage, not deep root
cause analysis.

## Instructions

1. Read the whole file first; note its time range and which levels appear.
2. Group identical or near-identical messages (same template, different ids)
   and count them instead of listing each occurrence.
3. Tag each group: `error` if it has a stack trace or non-zero exit, `warning`
   if degraded but recovered, `info` otherwise.
4. Order groups by severity, then by frequency.
5. End with a "next to check" list of at most five concrete follow-ups, each
   naming the file, endpoint or config involved.

## Examples

Input: a file where `ConnectionError` appears 240 times during a 30-second
window, plus scattered INFO lines.

Output: one grouped finding "240x ConnectionError during 12:04:11-12:04:41"
tagged error, with follow-ups pointing at the upstream host and the retry
timeout setting.