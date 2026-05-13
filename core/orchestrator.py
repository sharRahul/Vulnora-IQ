from __future__ import annotations

from dataclasses import dataclass, field

from core.types import Finding, ScanContext


@dataclass(slots=True)
class AttackChainStep:
    name: str
    objective: str
    module: str
    depends_on: list[str] = field(default_factory=list)


class Orchestrator:
    """Coordinates multi-step AI attack-chain simulations.

    The starter implementation is intentionally conservative: it records the
    chain plan and relies on individual modules for safe, authorised checks.
    """

    def build_agent_chain(self) -> list[AttackChainStep]:
        return [
            AttackChainStep(
                name="indirect_prompt_injection_probe",
                objective="Assess whether retrieved content can override system intent.",
                module="owasp_llm01_prompt_injection",
            ),
            AttackChainStep(
                name="tool_permission_boundary_check",
                objective="Assess whether the agent attempts unauthorised tool use.",
                module="owasp_llm06_excessive_agency",
                depends_on=["indirect_prompt_injection_probe"],
            ),
            AttackChainStep(
                name="sensitive_context_exposure_check",
                objective="Assess whether tool output or memory exposes sensitive context.",
                module="owasp_llm02_sensitive_information_disclosure",
                depends_on=["tool_permission_boundary_check"],
            ),
        ]

    def summarise_chain(self, context: ScanContext) -> Finding:
        chain = self.build_agent_chain()
        return Finding(
            title="Multi-step agent attack chain prepared",
            description="A safe chain plan was generated for prompt injection, tool boundary, and context exposure checks.",
            severity="info",
            owasp_id="LLM01:2025/LLM06:2025/LLM02:2025",
            affected_component=context.target_name,
            evidence={"steps": [step.__dict__ for step in chain]},
            recommendation="Validate each chain step inside an authorised test window with scoped tools and logging enabled.",
            mitre_atlas=["ATLAS-MAP-TODO"],
        )
