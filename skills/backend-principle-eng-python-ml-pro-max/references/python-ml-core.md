# Python ML Core Guidance (Concise)

## Default Stack
- Python: 3.11 or 3.12
- Training: PyTorch (default) or TensorFlow
- Data: Pandas + Arrow/Parquet; Spark or Ray for scale
- Orchestration: Airflow, Dagster, or Prefect
- Serving: FastAPI + Uvicorn; Triton or TorchServe for GPU
- Registry: MLflow or a managed registry

## Data and Features
- Validate schema and distributions on every ingest
- Use feature store when feature reuse is high
- Version datasets, features, and labels

## Evaluation
- Metrics aligned to product goals; avoid single-metric optimization
- Use time-based splits for temporal data
- Calibrate outputs and define decision thresholds

## Reliability
- Batch scoring jobs are idempotent and checkpointed
- Inference uses timeouts, retries, and fallbacks
- Record model version and feature version with every prediction

## Monitoring
- Track data drift, concept drift, and quality metrics
- Monitor latency P95/P99 and error rates
- Alert on quality regressions with runbooks

## Security and Privacy
- Restrict access to datasets and model artifacts
- Redact PII and enforce retention policies
- Encrypt data in transit and at rest

## Testing
- Unit tests for feature logic and preprocessing
- Integration tests for training and serving
- Data tests for schema, nulls, and ranges
