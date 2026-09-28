"""TypedDicts for `claude plugin eval --json` output — only the fields pairing.py/wrapper.py read."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class GraderResult(TypedDict):
    name: str
    passed: bool
    weight: float
    scored: NotRequired[bool]


class RunResult(TypedDict):
    score: float
    error: NotRequired[str | None]
    costUsd: NotRequired[float]
    skippedPaidGraders: NotRequired[bool]
    tracePath: NotRequired[str | None]
    graders: NotRequired[list[GraderResult]]


class CaseAggregates(TypedDict):
    score: NotRequired[float]
    scoreWithout: NotRequired[float]
    delta: NotRequired[float]


class CaseResult(TypedDict):
    name: str
    arms: NotRequired[dict[str, list[RunResult]]]
    aggregates: NotRequired[CaseAggregates]


class EvalResult(TypedDict):
    cases: list[CaseResult]
