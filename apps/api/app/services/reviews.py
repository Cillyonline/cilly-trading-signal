import csv
import io
import json
from collections import Counter
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import ManualReviewLabel
from app.models.review import ReviewBatch, ReviewEntry
from app.models.signal import Signal
from app.schemas.reviews import ReviewBatchCreate, ReviewBatchSummary, ReviewEntryCreate

EVIDENCE_ONLY_NOTICE = (
    "Review batches are process evidence only. They are not backtests, profitability "
    "validation, trading advice, live-readiness evidence, or broker/execution workflows."
)
REVIEW_BATCH_CSV_HEADERS = [
    "batch_id",
    "batch_name",
    "evidence_only_notice",
    "entry_id",
    "symbol",
    "asset_class",
    "strategy_type",
    "signal_status",
    "score_class",
    "manual_review_label",
    "quality_blockers",
    "benchmark_context",
    "follow_up_needed",
    "follow_up_issue_url",
    "outcome_r",
    "outcome_measurement_rule",
    "notes",
    "created_at",
]
ATTENTION_LABELS = {
    ManualReviewLabel.TOO_PERMISSIVE.value,
    ManualReviewLabel.TOO_STRICT.value,
    ManualReviewLabel.UNCLEAR.value,
}


class ReviewEntryError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


def list_review_batches(db: Session, user_id: int) -> list[ReviewBatch]:
    return list(
        db.scalars(
            select(ReviewBatch)
            .options(selectinload(ReviewBatch.entries))
            .where(ReviewBatch.user_id == user_id)
            .order_by(ReviewBatch.updated_at.desc(), ReviewBatch.id.desc())
        )
    )


def get_review_batch(db: Session, user_id: int, batch_id: int) -> ReviewBatch | None:
    batch = db.scalar(
        select(ReviewBatch)
        .options(selectinload(ReviewBatch.entries))
        .where(ReviewBatch.id == batch_id)
    )
    if batch is None or batch.user_id != user_id:
        return None
    return batch


def create_review_batch(db: Session, user_id: int, payload: ReviewBatchCreate) -> ReviewBatch:
    batch = ReviewBatch(user_id=user_id, **payload.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def create_review_entry(
    db: Session, user_id: int, batch_id: int, payload: ReviewEntryCreate
) -> ReviewEntry:
    batch = get_review_batch(db, user_id, batch_id)
    if batch is None:
        raise ReviewEntryError("Review batch not found.")

    data = payload.model_dump()
    if data.get("follow_up_issue_url") is not None:
        data["follow_up_issue_url"] = str(data["follow_up_issue_url"])
    data["symbol"] = data["symbol"].strip().upper()
    signal_id = data.get("signal_id")
    if signal_id is not None:
        signal = db.get(Signal, signal_id)
        if signal is None or signal.user_id != user_id:
            raise ReviewEntryError("Signal not found.")

    entry = ReviewEntry(batch_id=batch.id, user_id=user_id, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def build_review_batch_summary(batch: ReviewBatch) -> ReviewBatchSummary:
    entries = batch.entries
    label_counts = Counter(entry.manual_review_label.value for entry in entries)
    blocker_counts: Counter[str] = Counter()
    for entry in entries:
        for pattern in _extract_patterns(entry.quality_blockers):
            blocker_counts[pattern] += 1

    return ReviewBatchSummary(
        reviewed_count=len(entries),
        label_counts=dict(label_counts),
        follow_up_needed_count=sum(1 for entry in entries if entry.follow_up_needed),
        repeated_attention_labels=sorted(
            label
            for label, count in label_counts.items()
            if label in ATTENTION_LABELS and count >= 2
        ),
        repeated_blocker_patterns=sorted(
            pattern for pattern, count in blocker_counts.items() if count >= 2
        ),
        evidence_only_notice=EVIDENCE_ONLY_NOTICE,
    )


def export_review_batch_csv(batch: ReviewBatch) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=REVIEW_BATCH_CSV_HEADERS, lineterminator="\r\n")
    writer.writeheader()
    for entry in sorted(batch.entries, key=lambda item: (item.created_at, item.id)):
        writer.writerow(
            {
                "batch_id": batch.id,
                "batch_name": batch.name,
                "evidence_only_notice": EVIDENCE_ONLY_NOTICE,
                "entry_id": entry.id,
                "symbol": entry.symbol,
                "asset_class": entry.asset_class.value if entry.asset_class else "",
                "strategy_type": entry.strategy_type.value if entry.strategy_type else "",
                "signal_status": entry.signal_status.value if entry.signal_status else "",
                "score_class": entry.score_class.value if entry.score_class else "",
                "manual_review_label": entry.manual_review_label.value,
                "quality_blockers": _json_for_csv(entry.quality_blockers),
                "benchmark_context": entry.benchmark_context or "",
                "follow_up_needed": "yes" if entry.follow_up_needed else "no",
                "follow_up_issue_url": entry.follow_up_issue_url or "",
                "outcome_r": _fmt_decimal(entry.outcome_r),
                "outcome_measurement_rule": entry.outcome_measurement_rule or "",
                "notes": entry.notes or "",
                "created_at": str(entry.created_at),
            }
        )
    return output.getvalue()


def _extract_patterns(value: list | dict | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        patterns: list[str] = []
        for item in value:
            if isinstance(item, str):
                patterns.append(item)
            elif isinstance(item, dict):
                pattern = item.get("key") or item.get("code") or item.get("label")
                if isinstance(pattern, str):
                    patterns.append(pattern)
        return patterns
    if isinstance(value, dict):
        pattern = value.get("key") or value.get("code") or value.get("label")
        return [pattern] if isinstance(pattern, str) else []
    return []


def _json_for_csv(value: list | dict | None) -> str:
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _fmt_decimal(value: Decimal | None) -> str:
    return "" if value is None else str(value)
