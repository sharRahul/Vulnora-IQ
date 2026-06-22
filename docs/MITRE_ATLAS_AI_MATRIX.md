# MITRE ATLAS Matrix for AI Systems

This file is the VulnoraIQ implementation planning register for MITRE ATLAS tactics, techniques, and sub-techniques.

> **Generated snapshot:** this checked-in snapshot is generated from the official MITRE ATLAS v6 source path used by VulnoraIQ: `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml`.

> **Mapping rule:** if a tactic or technique cannot be confidently mapped to OWASP or a VulnoraIQ coverage area, it is still listed and marked `Unmapped / map later`. No ATLAS item should disappear just because it is not mapped yet.

## Official source alignment

- Site: `https://atlas.mitre.org`
- Data repository: `https://github.com/mitre-atlas/atlas-data`
- Source file: `dist/v6/ATLAS-2026.05.yaml`
- Collection version: `2026.05`
- Modified date: `2026-05-27`
- Tactic count in this snapshot: `16`
- Technique and sub-technique count in this snapshot: `170`

## Regeneration command

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md
```

Check for drift:

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md \
  --check
```

## Tactics

| Tactic ID | Tactic | OWASP mapping | VulnoraIQ coverage area | Implementation status |
| --- | --- | --- | --- | --- |
| AML.TA0000 | AI Model Access | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.TA0001 | AI Attack Staging | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.TA0002 | Reconnaissance | Unmapped / map later | Reconnaissance / environment discovery | Candidate mapping / needs validation |
| AML.TA0003 | Resource Development | Unmapped / map later | Supply-chain and capability provenance planning | Candidate mapping / needs validation |
| AML.TA0004 | Initial Access | Unmapped / map later | Configured target exposure / initial access planning | Candidate mapping / needs validation |
| AML.TA0005 | Execution | LLM05 / LLM06 | Output-to-action and agent tool execution governance | Candidate mapping / needs validation |
| AML.TA0006 | Persistence | LLM04 / LLM06 | Model, corpus, memory, and agent persistence review | Candidate mapping / needs validation |
| AML.TA0007 | Defense Evasion | LLM01 / LLM07 | Guardrail bypass and protected-instruction review | Candidate mapping / needs validation |
| AML.TA0008 | Discovery | LLM02 / LLM08 | System, RAG, agent, and model discovery review | Candidate mapping / needs validation |
| AML.TA0009 | Collection | LLM02 / LLM08 | Artifact, data-source, and service collection review | Candidate mapping / needs validation |
| AML.TA0010 | Exfiltration | LLM02 / LLM06 | Restricted information and agent-tool exfiltration review | Candidate mapping / needs validation |
| AML.TA0011 | Impact | LLM05 / LLM10 | Output, integrity, availability, and cost impact review | Candidate mapping / needs validation |
| AML.TA0012 | Privilege Escalation | LLM06 | Agent authority, permissions, and tool escalation review | Candidate mapping / needs validation |
| AML.TA0013 | Credential Access | LLM02 / LLM06 | Credential exposure and agent configuration review | Candidate mapping / needs validation |
| AML.TA0014 | Command and Control | LLM06 | Agent/tool command channel review | Candidate mapping / needs validation |
| AML.TA0015 | Lateral Movement | LLM06 | Agent/tool/data-source movement planning | Candidate mapping / needs validation |

## Techniques and sub-techniques

| Technique ID | Technique | OWASP mapping | VulnoraIQ coverage area | Implementation status |
| --- | --- | --- | --- | --- |
| AML.T0000 | Search Open Technical Databases | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0000.000 | Journals and Conference Proceedings | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0000.001 | Pre-Print Repositories | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0000.002 | Technical Blogs | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0001 | Search Open AI Vulnerability Analysis | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0002 | Acquire Public AI Artifacts | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0002.000 | Datasets | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0002.001 | Models | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0002.002 | AI Agent Configuration | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0003 | Search Victim-Owned Websites | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0004 | Search Application Repositories | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0005 | Create Proxy AI Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0005.000 | Train Proxy via Gathered AI Artifacts | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0005.001 | Train Proxy via Replication | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0005.002 | Use Pre-Trained Model | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0006 | Active Scanning | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0007 | Discover AI Artifacts | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008 | Acquire Infrastructure | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008.000 | AI Development Workspaces | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008.001 | Consumer Hardware | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008.002 | Domains | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008.003 | Physical Countermeasures | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008.004 | Serverless | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0008.005 | AI Service Proxies | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0010 | AI Supply Chain Compromise | LLM03 Supply Chain | AI artifact provenance and supply-chain checks | Candidate mapping / needs validation |
| AML.T0010.000 | Hardware | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0010.001 | AI Software | LLM03 Supply Chain | AI artifact provenance and supply-chain checks | Candidate mapping / needs validation |
| AML.T0010.002 | Data | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0010.003 | Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0010.004 | Container Registry | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0010.005 | AI Agent Tool | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0011 | User Execution | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0011.000 | Unsafe AI Artifacts | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0011.001 | Malicious Package | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0011.002 | Poisoned AI Agent Tool | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0011.003 | Malicious Link | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0012 | Valid Accounts | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0013 | Discover AI Model Ontology | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0014 | Discover AI Model Family | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0015 | Evade AI Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0016 | Obtain Capabilities | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0016.000 | Adversarial AI Attack Implementations | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0016.001 | Software Tools | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0016.002 | Generative AI | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0017 | Develop Capabilities | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0017.000 | Adversarial AI Attacks | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0018 | Manipulate AI Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0018.000 | Poison AI Model | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0018.001 | Modify AI Model Architecture | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0018.002 | Embed Malware | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0019 | Publish Poisoned Datasets | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0020 | Poison Training Data | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0021 | Establish Accounts | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0024 | Exfiltration via AI Inference API | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0024.000 | Infer Training Data Membership | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0024.001 | Invert AI Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0024.002 | Extract AI Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0025 | Exfiltration via Cyber Means | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0029 | Denial of AI Service | LLM10 Unbounded Consumption | Resource, token, rate-limit, and cost-control review | Candidate mapping / needs validation |
| AML.T0031 | Erode AI Model Integrity | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0034 | Cost Harvesting | LLM10 Unbounded Consumption | Resource, token, rate-limit, and cost-control review | Candidate mapping / needs validation |
| AML.T0034.000 | Excessive Queries | LLM10 Unbounded Consumption | Resource, token, rate-limit, and cost-control review | Candidate mapping / needs validation |
| AML.T0034.001 | Resource-Intensive Queries | LLM10 Unbounded Consumption | Resource, token, rate-limit, and cost-control review | Candidate mapping / needs validation |
| AML.T0034.002 | Agentic Resource Consumption | LLM10 Unbounded Consumption | Resource, token, rate-limit, and cost-control review | Candidate mapping / needs validation |
| AML.T0035 | AI Artifact Collection | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0036 | Data from Information Repositories | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0037 | Data from Local System | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0040 | AI Model Inference API Access | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0041 | Physical Environment Access | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0042 | Verify Attack | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0043 | Craft Adversarial Data | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0043.000 | White-Box Optimization | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0043.001 | Black-Box Optimization | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0043.002 | Black-Box Transfer | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0043.003 | Manual Modification | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0043.004 | Insert Backdoor Trigger | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0044 | Full AI Model Access | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0046 | Spamming AI System with Chaff Data | LLM10 Unbounded Consumption | Resource, token, rate-limit, and cost-control review | Candidate mapping / needs validation |
| AML.T0047 | AI-Enabled Product or Service | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0048 | External Harms | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0048.000 | Financial Harm | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0048.001 | Reputational Harm | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0048.002 | Societal Harm | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0048.003 | User Harm | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0048.004 | AI Intellectual Property Theft | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0049 | Exploit Public-Facing Application | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0050 | Command and Scripting Interpreter | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0051 | LLM Prompt Injection | LLM01 Prompt Injection / LLM07 System Prompt Leakage | Prompt boundary, protected-instruction, and guardrail review | Candidate mapping / needs validation |
| AML.T0051.000 | Direct | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0051.001 | Indirect | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0051.002 | Triggered | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0052 | Phishing | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0052.000 | Spearphishing via Social Engineering LLM | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0052.001 | Deepfake-Assisted Phishing | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0053 | AI Agent Tool Invocation | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0054 | LLM Jailbreak | LLM01 Prompt Injection / LLM07 System Prompt Leakage | Prompt boundary, protected-instruction, and guardrail review | Candidate mapping / needs validation |
| AML.T0055 | Unsecured Credentials | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0056 | Extract LLM System Prompt | LLM07 System Prompt Leakage | Protected instruction and system-context exposure review | Candidate mapping / needs validation |
| AML.T0057 | LLM Data Leakage | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0058 | Publish Poisoned Models | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0059 | Erode Dataset Integrity | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0060 | Publish Hallucinated Entities | LLM05 Improper Output Handling / LLM09 Misinformation | Output validation, citation, grounding, and synthetic-content review | Candidate mapping / needs validation |
| AML.T0061 | LLM Prompt Self-Replication | LLM01 Prompt Injection / LLM07 System Prompt Leakage | Prompt boundary, protected-instruction, and guardrail review | Candidate mapping / needs validation |
| AML.T0062 | Discover LLM Hallucinations | LLM05 Improper Output Handling / LLM09 Misinformation | Output validation, citation, grounding, and synthetic-content review | Candidate mapping / needs validation |
| AML.T0063 | Discover AI Model Outputs | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0064 | Gather RAG-Indexed Targets | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0065 | LLM Prompt Crafting | LLM01 Prompt Injection / LLM07 System Prompt Leakage | Prompt boundary, protected-instruction, and guardrail review | Candidate mapping / needs validation |
| AML.T0066 | Retrieval Content Crafting | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0067 | LLM Trusted Output Components Manipulation | LLM05 Improper Output Handling / LLM09 Misinformation | Output validation, citation, grounding, and synthetic-content review | Candidate mapping / needs validation |
| AML.T0067.000 | Citations | LLM05 Improper Output Handling / LLM09 Misinformation | Output validation, citation, grounding, and synthetic-content review | Candidate mapping / needs validation |
| AML.T0068 | LLM Prompt Obfuscation | LLM01 Prompt Injection / LLM07 System Prompt Leakage | Prompt boundary, protected-instruction, and guardrail review | Candidate mapping / needs validation |
| AML.T0069 | Discover LLM System Information | LLM07 System Prompt Leakage | Protected instruction and system-context exposure review | Candidate mapping / needs validation |
| AML.T0069.000 | Special Character Sets | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0069.001 | System Instruction Keywords | LLM07 System Prompt Leakage | Protected instruction and system-context exposure review | Candidate mapping / needs validation |
| AML.T0069.002 | System Prompt | LLM07 System Prompt Leakage | Protected instruction and system-context exposure review | Candidate mapping / needs validation |
| AML.T0070 | RAG Poisoning | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0071 | False RAG Entry Injection | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0072 | Reverse Shell | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0073 | Impersonation | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0074 | Masquerading | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0075 | Cloud Service Discovery | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0076 | Corrupt AI Model | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |
| AML.T0077 | LLM Response Rendering | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0078 | Drive-by Compromise | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0079 | Stage Capabilities | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0080 | AI Agent Context Poisoning | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0080.000 | Memory | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0080.001 | Thread | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0081 | Modify AI Agent Configuration | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0082 | RAG Credential Harvesting | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0083 | Credentials from AI Agent Configuration | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0084 | Discover AI Agent Configuration | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0084.000 | Embedded Knowledge | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0084.001 | Tool Definitions | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0084.002 | Activation Triggers | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0084.003 | Call Chains | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0085 | Data from AI Services | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0085.000 | RAG Databases | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0085.001 | AI Agent Tools | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0086 | Exfiltration via AI Agent Tool Invocation | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0087 | Gather Victim Identity Information | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0088 | Generate Deepfakes | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0089 | Process Discovery | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0090 | OS Credential Dumping | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0091 | Use Alternate Authentication Material | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0091.000 | Application Access Token | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0092 | Manipulate User LLM Chat History | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0093 | Prompt Infiltration via Public-Facing Application | LLM01 Prompt Injection / LLM07 System Prompt Leakage | Prompt boundary, protected-instruction, and guardrail review | Candidate mapping / needs validation |
| AML.T0094 | Delay Execution of LLM Instructions | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0095 | Search Open Websites/Domains | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0095.000 | Code Repositories | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0096 | AI Service API | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0097 | Virtualization/Sandbox Evasion | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0098 | AI Agent Tool Credential Harvesting | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0099 | AI Agent Tool Data Poisoning | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0100 | AI Agent Clickbait | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0101 | Data Destruction via AI Agent Tool Invocation | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0102 | Generate Malicious Commands | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0103 | Deploy AI Agent | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0104 | Publish Poisoned AI Agent Tool | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0105 | Escape to Host | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0106 | Exploitation for Credential Access | LLM02 Sensitive Information Disclosure / LLM06 Excessive Agency | Restricted information, credential, and data-access review | Candidate mapping / needs validation |
| AML.T0107 | Exploitation for Defense Evasion | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0108 | AI Agent | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0109 | AI Supply Chain Rug Pull | LLM03 Supply Chain | AI artifact provenance and supply-chain checks | Candidate mapping / needs validation |
| AML.T0110 | AI Agent Tool Poisoning | LLM04 Data and Model Poisoning / LLM08 Vector and Embedding Weaknesses | RAG/corpus/source-trust and poisoning review | Candidate mapping / needs validation |
| AML.T0111 | AI Supply Chain Reputation Inflation | LLM03 Supply Chain | AI artifact provenance and supply-chain checks | Candidate mapping / needs validation |
| AML.T0112 | Machine Compromise | Unmapped / map later | Unmapped / map later | Unmapped / map later |
| AML.T0112.000 | Local AI Agent | LLM06 Excessive Agency | Agent runtime, memory, tool, and approval governance | Candidate mapping / needs validation |
| AML.T0112.001 | AI Artifacts | LLM03 Supply Chain / LLM04 Data and Model Poisoning | AI artifact, model, dataset, and provenance review | Candidate mapping / needs validation |

## Unmapped / map later backlog

These entries are intentionally preserved so future VulnoraIQ work can map them later rather than losing them during generation.

### Techniques needing mapping review

- AML.T0000 — Search Open Technical Databases
- AML.T0000.000 — Journals and Conference Proceedings
- AML.T0000.001 — Pre-Print Repositories
- AML.T0000.002 — Technical Blogs
- AML.T0001 — Search Open AI Vulnerability Analysis
- AML.T0002.000 — Datasets
- AML.T0003 — Search Victim-Owned Websites
- AML.T0004 — Search Application Repositories
- AML.T0005.000 — Train Proxy via Gathered AI Artifacts
- AML.T0005.001 — Train Proxy via Replication
- AML.T0005.002 — Use Pre-Trained Model
- AML.T0006 — Active Scanning
- AML.T0007 — Discover AI Artifacts
- AML.T0008 — Acquire Infrastructure
- AML.T0008.000 — AI Development Workspaces
- AML.T0008.001 — Consumer Hardware
- AML.T0008.002 — Domains
- AML.T0008.003 — Physical Countermeasures
- AML.T0008.004 — Serverless
- AML.T0008.005 — AI Service Proxies
- AML.T0010.000 — Hardware
- AML.T0010.002 — Data
- AML.T0010.004 — Container Registry
- AML.T0011 — User Execution
- AML.T0011.001 — Malicious Package
- AML.T0011.003 — Malicious Link
- AML.T0012 — Valid Accounts
- AML.T0016 — Obtain Capabilities
- AML.T0016.000 — Adversarial AI Attack Implementations
- AML.T0016.002 — Generative AI
- AML.T0017 — Develop Capabilities
- AML.T0017.000 — Adversarial AI Attacks
- AML.T0018.002 — Embed Malware
- AML.T0021 — Establish Accounts
- AML.T0037 — Data from Local System
- AML.T0041 — Physical Environment Access
- AML.T0042 — Verify Attack
- AML.T0043 — Craft Adversarial Data
- AML.T0043.000 — White-Box Optimization
- AML.T0043.001 — Black-Box Optimization
- AML.T0043.002 — Black-Box Transfer
- AML.T0043.003 — Manual Modification
- AML.T0043.004 — Insert Backdoor Trigger
- AML.T0047 — AI-Enabled Product or Service
- AML.T0048 — External Harms
- AML.T0048.000 — Financial Harm
- AML.T0048.001 — Reputational Harm
- AML.T0048.002 — Societal Harm
- AML.T0048.003 — User Harm
- AML.T0048.004 — AI Intellectual Property Theft
- AML.T0049 — Exploit Public-Facing Application
- AML.T0050 — Command and Scripting Interpreter
- AML.T0051.000 — Direct
- AML.T0051.001 — Indirect
- AML.T0051.002 — Triggered
- AML.T0052 — Phishing
- AML.T0052.000 — Spearphishing via Social Engineering LLM
- AML.T0052.001 — Deepfake-Assisted Phishing
- AML.T0059 — Erode Dataset Integrity
- AML.T0069.000 — Special Character Sets
- AML.T0072 — Reverse Shell
- AML.T0073 — Impersonation
- AML.T0074 — Masquerading
- AML.T0075 — Cloud Service Discovery
- AML.T0077 — LLM Response Rendering
- AML.T0078 — Drive-by Compromise
- AML.T0079 — Stage Capabilities
- AML.T0080.000 — Memory
- AML.T0080.001 — Thread
- AML.T0084.000 — Embedded Knowledge
- AML.T0088 — Generate Deepfakes
- AML.T0089 — Process Discovery
- AML.T0091 — Use Alternate Authentication Material
- AML.T0091.000 — Application Access Token
- AML.T0092 — Manipulate User LLM Chat History
- AML.T0094 — Delay Execution of LLM Instructions
- AML.T0095 — Search Open Websites/Domains
- AML.T0095.000 — Code Repositories
- AML.T0096 — AI Service API
- AML.T0097 — Virtualization/Sandbox Evasion
- AML.T0102 — Generate Malicious Commands
- AML.T0105 — Escape to Host
- AML.T0107 — Exploitation for Defense Evasion
- AML.T0112 — Machine Compromise

## Drift-control rule

Future changes must not manually remove generated tactic or technique rows. Update the official source version or generator, regenerate this file, then update VulnoraIQ configuration and payload plans against the regenerated IDs. Unmapped entries must stay visible until deliberately mapped or excluded with documented rationale.
