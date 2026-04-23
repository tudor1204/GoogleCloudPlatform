# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **kubernetes-engine-samples** — a collection of standalone sample applications and tutorials for [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine/). Each sample lives in its own subdirectory under a top-level topic category and is independently deployable.

Top-level topic directories:
- `ai-ml/` — LLM serving, GPU/TPU workloads, JAX, Ray, fine-tuning
- `autopilot/` — GKE Autopilot-specific patterns
- `batch/` — Batch workloads, Kueue, Airflow
- `cost-optimization/` — VPA, scheduled autoscaling, cost analysis
- `databases/` — Postgres, MySQL, Redis, Kafka, Spanner, vector DBs
- `management/` — GitOps, node pool migration
- `networking/` — Load balancing, gRPC, multi-cluster, network policies
- `observability/` — Distributed tracing, custom metrics, Elastic Stack
- `quickstarts/` — Hello-app, Guestbook, Whereami, language samples
- `security/` — Workload Identity, secrets
- `service-mesh/` — Istio
- `streaming/` — Kafka operators, stateful Kafka
- `workloads/` — Multi-arch migration
- `demos/` — Point-in-time blog/demo content; **not maintained**, excluded from Renovate

## CI Validation (GitHub Actions)

Each sample has its own workflow in `.github/workflows/<category>-<sample>-ci.yml`. Workflows trigger on `push`/`pull_request` only for changes to their own path and workflow file. All workflows run on `ubuntu-22.04`.

To validate a sample locally before pushing:

```bash
# Build a container image (the most common CI check)
cd <path/to/sample>
docker build --tag <image-name> .

# Validate Terraform
cd <path/to/terraform>
terraform init
terraform validate
```

New workflow file names follow the pattern: `<category>-<sample-title>-ci.yml`.

## Sample Requirements

Every new sample must include:

1. **A dedicated directory** under an appropriate top-level topic category.
2. **A `README.md`** with a link to the corresponding GKE documentation tutorial. Do not duplicate tutorial instructions in the README.
3. **A GitHub Actions workflow** at `.github/workflows/<name>-ci.yml` that at minimum builds Docker images (`docker build`) and/or validates Terraform (`terraform validate`).
4. **A `CODEOWNERS` entry** in `.github/CODEOWNERS`.
5. **Apache-2.0 license headers** on all source, manifest, Dockerfile, shell, SQL, and Terraform files (see below).

If the sample needs canonical public images, also add a `cloudbuild.yaml` and a Terraform resource in `.github/terraform/google-cloud-build-triggers.tf`. Images are pushed to `us-docker.pkg.dev/google-samples/containers/gke/<image-name>:latest`.

## License Headers

All source files (`.go`, `.py`, `.java`, `.js`, `.sh`, `.sql`, `.tf`, `.yaml`, `.yml`, `Dockerfile`) require an Apache-2.0 header with the current year and `Google LLC` as the copyright holder. `Chart.yaml` and `.github/workflows/**` files are exempt.

```
# Copyright <YEAR> Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# ...
```

## Region Tags

Code snippets embedded in GKE documentation must be wrapped in region tags:

```yaml
# [START gke_<topic>_<sample_title>_<file_name>]
... content ...
# [END gke_<topic>_<sample_title>_<file_name>]
```

Example: `[START gke_aiml_llm_multi_gpus_service]` / `[END gke_aiml_llm_multi_gpus_service]`.

## Dependency Management

Dependencies are updated weekly by Renovate, auto-merging minor/patch updates. Constraints:
- Python is pinned to `~=3.11.0` for `pip-compile` files (use `requirements.in`, not `requirements.txt` directly).
- Spring Boot v2 samples are capped below v3 (requires Java 17+).
- `demos/**` and `security/language-vulns/**` are excluded from Renovate.
- Dockerfile base images are **not** auto-updated by Renovate (`"dockerfile": {"enabled": false}`); update them manually.

## PR Checklist

Before opening a PR, confirm:
- Contributing guide followed
- Sample tested end-to-end
- Workflow file added/updated
- Region tags added (for new samples)
- All dependencies use up-to-date versions
- License headers present on all applicable files
