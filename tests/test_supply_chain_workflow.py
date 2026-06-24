from __future__ import annotations

from pathlib import Path


def test_supply_chain_workflow_contains_required_tools_and_outputs() -> None:
    workflow = Path(".github/workflows/security-supply-chain.yml").read_text(encoding="utf-8")

    assert "aquasecurity/trivy-action@v0.36.0" in workflow
    assert "docker/build-push-action@v7" in workflow
    assert "docker/setup-buildx-action@v4" in workflow
    assert "sigstore/cosign-installer@v4.1.0" in workflow
    assert "github/codeql-action/upload-sarif@v4" in workflow
    assert "trivy-filesystem.sarif" in workflow
    assert "trivy-image.sarif" in workflow
    assert "vulnoraiq-filesystem.spdx.json" in workflow
    assert "vulnoraiq-image.cdx.json" in workflow
    assert "cosign sign --yes" in workflow
    assert "cosign verify" in workflow
    assert "vulnoraiq-security-supply-chain-${{ github.sha }}" in workflow


def test_supply_chain_workflow_has_safe_publish_and_gate_controls() -> None:
    workflow = Path(".github/workflows/security-supply-chain.yml").read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "publish_image:" in workflow
    assert "enforce_security_gate:" in workflow
    assert "SHOULD_PUBLISH=${should_publish}" in workflow
    assert "github.event_name == 'workflow_dispatch' && inputs.enforce_security_gate" in workflow
    assert "steps.publish_policy.outputs.should_publish == 'true'" in workflow
    assert "id-token: write" in workflow
    assert "packages: write" in workflow
    assert "security-events: write" in workflow


def test_supply_chain_docs_are_linked_from_docs_index() -> None:
    docs_index = Path("docs/README.md").read_text(encoding="utf-8")
    pipeline_doc = Path("docs/SUPPLY_CHAIN_PIPELINE.md").read_text(encoding="utf-8")
    backlog = Path("docs/PRODUCTION_HARDENING_BACKLOG.md").read_text(encoding="utf-8")
    status = Path("docs/IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8")

    assert "SUPPLY_CHAIN_PIPELINE.md" in docs_index
    assert "Trivy" in pipeline_doc
    assert "Cosign" in pipeline_doc
    current_backlog = backlog.split("## Current maturity backlog", 1)[1].split("## Production claim rule", 1)[0]
    assert "Container supply chain" not in current_backlog
    assert "Security testing pipeline" not in current_backlog
    assert "Supply-chain workflow" in backlog
    assert "Supply-chain workflow" in status
