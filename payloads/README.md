# Payload Libraries

This folder is for reusable, safe starter payloads used during authorised AI security assessments.

Recommended subfolders:

- `prompt_injection/` - direct and indirect prompt-injection probes
- `jailbreaks/` - benign regression prompts for policy-boundary testing
- `rag_poisoning/` - controlled test-corpus snippets for retrieval manipulation checks
- `tool_abuse/` - agent tool-boundary and approval-gate cases

Payloads must be defensive, auditable, and scoped to systems you own or are explicitly authorised to test. Do not add payloads intended for credential theft, malware delivery, or unauthorised bypass of real systems.
