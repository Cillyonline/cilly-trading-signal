import csv
import io
import json
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import ManualReviewLabel, ReviewFindingCategorySource
from app.models.review import ReviewBatch, ReviewEntry, ReviewEntryRevision
from app.models.signal import Signal
from app.schemas.reviews import (
    ReviewBatchCreate,
    ReviewBatchSummary,
    ReviewEntryCreate,
    ReviewEntryUpdate,
)

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
    "finding_category",
    "finding_category_source",
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
REPEATED_FINDING_THRESHOLD = 2
UNKNOWN_FINDING_CATEGORY = "unknown"
FINDING_CATEGORY_KEYWORDS = [
    ("market_regime_too_loose", ("market_regime", "benchmark", "regime", "relative_strength")),
    ("risk_plan_unclear", ("risk", "rr", "r:r", "stop", "target", "position_size")),
    ("trigger_too_strict", ("trigger", "breakout", "close_confirmation")),
    ("data_context_missing", ("stale", "missing", "partial", "failed", "unknown", "data")),
    ("liquidity_or_volatility", ("liquidity", "volume", "atr", "volatility", "wick")),
]


class ReviewEntryError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


def list_review_batches(db: Session, user_id: int) -> list[ReviewBatch]:
    return list(
        db.scalars(
            select(ReviewBatch)
            .options(selectinload(ReviewBatch.entries).selectinload(ReviewEntry.revisions))
            .where(ReviewBatch.user_id == user_id)
            .order_by(ReviewBatch.updated_at.desc(), ReviewBatch.id.desc())
        )
    )


def get_review_batch(db: Session, user_id: int, batch_id: int) -> ReviewBatch | None:
    batch = db.scalar(
        select(ReviewBatch)
        .options(selectinload(ReviewBatch.entries).selectinload(ReviewEntry.revisions))
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

    data = _entry_payload_data(payload)
    _validate_signal_ownership(db, user_id, data.get("signal_id"))
    data = _apply_finding_category(data)

    entry = ReviewEntry(batch_id=batch.id, user_id=user_id, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_review_entry(
    db: Session, user_id: int, batch_id: int, entry_id: int, payload: ReviewEntryUpdate
) -> ReviewEntry:
    batch = get_review_batch(db, user_id, batch_id)
    if batch is None:
        raise ReviewEntryError("Review batch not found.")
    entry = db.get(ReviewEntry, entry_id)
    if entry is None or entry.user_id != user_id or entry.batch_id != batch.id:
        raise ReviewEntryError("Review entry not found.")

    data = _entry_payload_data(payload)
    _validate_signal_ownership(db, user_id, data.get("signal_id"))
    data = _apply_finding_category(data)
    _record_entry_revision(db, entry)
    for key, value in data.items():
        setattr(entry, key, value)
    batch.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(entry)
    return entry


def build_review_batch_summary(batch: ReviewBatch) -> ReviewBatchSummary:
    entries = batch.entries
    label_counts = Counter(entry.manual_review_label.value for entry in entries)
    blocker_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    false_positive_counts: Counter[str] = Counter()
    for entry in entries:
        for pattern in _extract_patterns(entry.quality_blockers):
            blocker_counts[pattern] += 1
        category_counts[entry.finding_category] += 1
        if entry.manual_review_label == ManualReviewLabel.TOO_PERMISSIVE:
            for pattern in _false_positive_patterns(entry):
                false_positive_counts[pattern] += 1

    return ReviewBatchSummary(
        reviewed_count=len(entries),
        label_counts=dict(label_counts),
        follow_up_needed_count=sum(1 for entry in entries if entry.follow_up_needed),
        repeated_attention_labels=sorted(
            label
            for label, count in label_counts.items()
            if label in ATTENTION_LABELS and count >= REPEATED_FINDING_THRESHOLD
        ),
        repeated_blocker_patterns=sorted(
            pattern
            for pattern, count in blocker_counts.items()
            if count >= REPEATED_FINDING_THRESHOLD
        ),
        finding_category_counts=dict(sorted(category_counts.items())),
        repeated_finding_categories=sorted(
            category
            for category, count in category_counts.items()
            if category != UNKNOWN_FINDING_CATEGORY and count >= REPEATED_FINDING_THRESHOLD
        ),
        repeated_false_positive_patterns=sorted(
            pattern
            for pattern, count in false_positive_counts.items()
            if count >= REPEATED_FINDING_THRESHOLD
        ),
        evidence_only_notice=EVIDENCE_ONLY_NOTICE,
    )


def classify_review_finding(entry: ReviewEntry) -> str:
    if entry.manual_review_label == ManualReviewLabel.USEFUL and not entry.follow_up_needed:
        return UNKNOWN_FINDING_CATEGORY
    values = [
        entry.manual_review_label.value,
        entry.benchmark_context or "",
        entry.outcome_measurement_rule or "",
        entry.notes or "",
        *_extract_patterns(entry.quality_blockers),
        *_extract_patterns(entry.no_trade_reasons),
        *_extract_patterns(entry.risk_flags),
    ]
    text = " ".join(values).lower()
    for category, keywords in FINDING_CATEGORY_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return category
    if entry.manual_review_label == ManualReviewLabel.TOO_STRICT:
        return "trigger_too_strict"
    if entry.manual_review_label == ManualReviewLabel.TOO_PERMISSIVE:
        return "risk_plan_unclear"
    return UNKNOWN_FINDING_CATEGORY


def classify_review_finding_data(data: dict) -> str:
    if data["manual_review_label"] == ManualReviewLabel.USEFUL and not data["follow_up_needed"]:
        return UNKNOWN_FINDING_CATEGORY
    values = [
        data["manual_review_label"].value,
        data.get("benchmark_context") or "",
        data.get("outcome_measurement_rule") or "",
        data.get("notes") or "",
        *_extract_patterns(data.get("quality_blockers")),
        *_extract_patterns(data.get("no_trade_reasons")),
        *_extract_patterns(data.get("risk_flags")),
    ]
    text = " ".join(values).lower()
    for category, keywords in FINDING_CATEGORY_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return category
    if data["manual_review_label"] == ManualReviewLabel.TOO_STRICT:
        return "trigger_too_strict"
    if data["manual_review_label"] == ManualReviewLabel.TOO_PERMISSIVE:
        return "risk_plan_unclear"
    return UNKNOWN_FINDING_CATEGORY


def _apply_finding_category(data: dict) -> dict:
    if data["finding_category_source"] == ReviewFindingCategorySource.MANUAL:
        data["finding_category"] = _normalize_finding_category(data.get("finding_category"))
        return data
    data["finding_category_source"] = ReviewFindingCategorySource.DERIVED
    data["finding_category"] = classify_review_finding_data(data)
    return data


def _normalize_finding_category(value: str | None) -> str:
    if value is None:
        return UNKNOWN_FINDING_CATEGORY
    category = value.strip().lower().replace(" ", "_")
    return category or UNKNOWN_FINDING_CATEGORY


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
                "finding_category": entry.finding_category,
                "finding_category_source": entry.finding_category_source.value,
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


def _false_positive_patterns(entry: ReviewEntry) -> list[str]:
    patterns = [
        *_extract_patterns(entry.quality_blockers),
        *_extract_patterns(entry.no_trade_reasons),
        *_extract_patterns(entry.risk_flags),
    ]
    if entry.finding_category != UNKNOWN_FINDING_CATEGORY:
        patterns.append(entry.finding_category)
    return list(dict.fromkeys(patterns))


def _entry_payload_data(payload: ReviewEntryCreate | ReviewEntryUpdate) -> dict:
    data = payload.model_dump()
    if data.get("follow_up_issue_url") is not None:
        data["follow_up_issue_url"] = str(data["follow_up_issue_url"])
    data["symbol"] = data["symbol"].strip().upper()
    return data


def _record_entry_revision(db: Session, entry: ReviewEntry) -> None:
    revision = ReviewEntryRevision(
        entry_id=entry.id,
        batch_id=entry.batch_id,
        user_id=entry.user_id,
        revision_number=len(entry.revisions) + 1,
        changed_at=datetime.now(UTC),
        previous_values=_entry_revision_snapshot(entry),
    )
    db.add(revision)


def _entry_revision_snapshot(entry: ReviewEntry) -> dict:
    return {
        "signal_id": entry.signal_id,
        "symbol": entry.symbol,
        "asset_class": entry.asset_class.value,
        "strategy_type": entry.strategy_type.value,
        "stored_data_start": _fmt_optional_date(entry.stored_data_start),
        "stored_data_end": _fmt_optional_date(entry.stored_data_end),
        "benchmark_context": entry.benchmark_context,
        "signal_status": entry.signal_status.value,
        "score_class": entry.score_class.value if entry.score_class else None,
        "no_trade_reasons": entry.no_trade_reasons,
        "risk_flags": entry.risk_flags,
        "quality_blockers": entry.quality_blockers,
        "entry_price": _fmt_optional_decimal(entry.entry_price),
        "stop_loss": _fmt_optional_decimal(entry.stop_loss),
        "target_price": _fmt_optional_decimal(entry.target_price),
        "planned_risk_reward": _fmt_optional_decimal(entry.planned_risk_reward),
        "manual_review_label": entry.manual_review_label.value,
        "finding_category": entry.finding_category,
        "finding_category_source": entry.finding_category_source.value,
        "outcome_r": _fmt_optional_decimal(entry.outcome_r),
        "outcome_measurement_rule": entry.outcome_measurement_rule,
        "follow_up_needed": entry.follow_up_needed,
        "follow_up_issue_url": entry.follow_up_issue_url,
        "notes": entry.notes,
    }


def _fmt_optional_date(value) -> str | None:
    return None if value is None else value.isoformat()


def _fmt_optional_decimal(value: Decimal | None) -> str | None:
    return None if value is None else str(value)


def _validate_signal_ownership(db: Session, user_id: int, signal_id: int | None) -> None:
    if signal_id is None:
        return
    signal = db.get(Signal, signal_id)
    if signal is None or signal.user_id != user_id:
        raise ReviewEntryError("Signal not found.")


def _json_for_csv(value: list | dict | None) -> str:
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _fmt_decimal(value: Decimal | None) -> str:
    return "" if value is None else str(value)
