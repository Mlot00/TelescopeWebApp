from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ProvenanceRecord:
    dataset_id: str
    analysis_kind: str
    git_sha: str
    created_at: str



def build_provenance(dataset_id: str, analysis_kind: str, git_sha: str = "unknown") -> ProvenanceRecord:
    return ProvenanceRecord(
        dataset_id=dataset_id,
        analysis_kind=analysis_kind,
        git_sha=git_sha,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
