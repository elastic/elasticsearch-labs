"""
OpenTelemetry bootstrap for the Search Analytics demo.

-------------------------------------------------------------------------------
TUTORIAL NOTE — you can skim or skip this file
-------------------------------------------------------------------------------

The blog series teaches **what to put on spans** in app.py (search.* attributes,
SemConv fields, etc.). This module is **demo plumbing** so the project works
reliably when people copy values from Elastic Cloud:

  - Skip export when .env still has placeholder values (search still works)
  - Fail fast with a clear message if OTLP headers aren't URL-encoded (%20)
  - Re-apply Authorization after EDOT init (EDOT only passes User-Agent today)
  - Force http/protobuf for Elastic managed OTLP (EDOT defaults to gRPC)

Setup for readers is still just three env vars in .env — see README.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.auto_instrumentation._load import (
    _load_configurators,
    _load_distro,
)
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Values from .env.example — treat as "OTel not configured yet"
_PLACEHOLDER_MARKERS = (
    "your-deployment",
    "your-search-cluster",
    "your-base64",
    "your-api-key",
    "changeme",
    "example.com",
)


def is_otel_configured() -> bool:
    """Return True when OTLP endpoint and headers look like real credentials."""
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not endpoint:
        return False
    if any(m in endpoint.lower() for m in _PLACEHOLDER_MARKERS):
        return False
    headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "").strip()
    if headers and any(m in headers.lower() for m in _PLACEHOLDER_MARKERS):
        return False
    return True


def validate_otlp_headers() -> None:
    """
    Fail fast if OTLP headers contain a literal space instead of %20.

    Elastic's UI shows `Authorization=ApiKey <base64-key>`, but OpenTelemetry
    requires the header value to be URL-encoded (`%20` for the space). An
    unencoded space silently breaks auth with an opaque HTTP 401, so we catch
    it at startup with an actionable message instead of letting export fail.
    """
    raw = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "").strip()
    if " " not in raw:
        return

    raise SystemExit(
        "\n".join(
            [
                "",
                "✗ OTEL_EXPORTER_OTLP_HEADERS contains a literal space.",
                "",
                "  Elastic's UI shows:   Authorization=ApiKey <base64-key>",
                "  OpenTelemetry needs:  Authorization=ApiKey%20<base64-key>",
                "",
                "  Replace the space after 'ApiKey' with %20 in your .env file.",
                "",
            ]
        )
    )


def _parsed_otlp_headers() -> dict[str, str]:
    from opentelemetry.util.re import parse_env_headers

    return dict(
        parse_env_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS", ""), liberal=True)
    )


def _inject_otlp_auth_headers() -> None:
    """EDOT passes headers= without Authorization — merge env auth onto exporters."""
    auth_headers = _parsed_otlp_headers()
    if not auth_headers:
        print("⚠ OTel: could not parse OTEL_EXPORTER_OTLP_HEADERS (check .env quoting)")
        return

    tp = trace.get_tracer_provider()
    processor = getattr(tp, "_active_span_processor", None)
    if processor is None:
        return

    processors = getattr(processor, "_span_processors", None) or [processor]
    for span_processor in processors:
        exporter = getattr(span_processor, "span_exporter", None)
        if exporter is None:
            continue
        session = getattr(exporter, "_session", None)
        if session is not None:
            session.headers.update(auth_headers)
        elif hasattr(exporter, "_headers") and isinstance(exporter._headers, dict):
            exporter._headers.update(auth_headers)


def _apply_resource_defaults() -> None:
    """Map OTEL_SERVICE_NAME → OTEL_RESOURCE_ATTRIBUTES when not set."""
    service_name = os.getenv("OTEL_SERVICE_NAME", "").strip()
    if service_name and not os.getenv("OTEL_RESOURCE_ATTRIBUTES"):
        os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"service.name={service_name}"


def init_otel(app: FastAPI) -> trace.Tracer:
    """
    Enable EDOT export to Elastic managed OTLP, or return a no-op tracer.

    Call once at startup. Instrumentation + export details live in this file;
    span attributes for search analytics live in app.py.
    """
    if not is_otel_configured():
        print(
            "⚠ OTel disabled: set OTEL_EXPORTER_OTLP_ENDPOINT and "
            "OTEL_EXPORTER_OTLP_HEADERS in .env (search still works)"
        )
        return trace.get_tracer("search-api")

    validate_otlp_headers()
    _apply_resource_defaults()
    os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")
    os.environ.setdefault("OTEL_LOGS_EXPORTER", "none")
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"

    distro = _load_distro()
    distro.configure()
    _load_configurators()
    _inject_otlp_auth_headers()

    FastAPIInstrumentor.instrument_app(app)
    if not ElasticsearchInstrumentor().is_instrumented_by_opentelemetry:
        ElasticsearchInstrumentor().instrument()

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    print(f"✓ OTel enabled: exporting to {endpoint}")
    return trace.get_tracer("search-api")
