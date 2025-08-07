"""
Custom OpenTelemetry File Exporter
Writes traces to a JSON file instead of console output.
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Optional
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan


class FileSpanExporter(SpanExporter):
    """Custom span exporter that writes traces to a JSON file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    def _timestamp_to_iso(self, timestamp_ns: int) -> str:
        """Convert nanoseconds timestamp to ISO format."""
        # Convert nanoseconds to seconds
        timestamp_s = timestamp_ns / 1_000_000_000
        dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
        return dt.isoformat()
    
    def export(self, spans: List[ReadableSpan]) -> SpanExportResult:
        """Export spans to a JSON file."""
        try:
            # Convert spans to JSON-serializable format
            span_data = []
            for span in spans:
                span_dict = {
                    "name": span.name,
                    "context": {
                        "trace_id": format(span.context.trace_id, '032x'),
                        "span_id": format(span.context.span_id, '016x'),
                        "trace_state": str(span.context.trace_state)
                    },
                    "kind": str(span.kind),
                    "parent_id": format(span.parent.span_id, '016x') if span.parent else None,
                    "start_time": self._timestamp_to_iso(span.start_time),
                    "end_time": self._timestamp_to_iso(span.end_time),
                    "status": {
                        "status_code": str(span.status.status_code)
                    },
                    "attributes": dict(span.attributes),
                    "events": [
                        {
                            "name": event.name,
                            "timestamp": self._timestamp_to_iso(event.timestamp),
                            "attributes": dict(event.attributes)
                        }
                        for event in span.events
                    ],
                    "links": [
                        {
                            "context": {
                                "trace_id": format(link.context.trace_id, '032x'),
                                "span_id": format(link.context.span_id, '016x')
                            },
                            "attributes": dict(link.attributes)
                        }
                        for link in span.links
                    ],
                    "resource": {
                        "attributes": dict(span.resource.attributes),
                        "schema_url": span.resource.schema_url
                    }
                }
                span_data.append(span_dict)
            
            # Write to file (append mode)
            with open(self.file_path, 'a', encoding='utf-8') as f:
                for span in span_data:
                    f.write(json.dumps(span, indent=2) + '\n')
            
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"Error exporting spans to file: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self):
        """Clean up resources."""
        pass 