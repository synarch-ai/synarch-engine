# Colab Notebook Explainer Pipeline

A dedicated AI/ML notebook-to-tutorial augmentation pipeline.

## Goal

For AI/ML classes with official Colab notebooks, this pipeline does all of the following deterministically:

1. Injects official class resources (slides/colab/video links) into `final_notes.md`.
2. Downloads each Colab notebook to the local session directory.
3. Extracts full code-cell dumps.
4. Builds deep explanatory appendices:
   - Import-by-import explanation
   - Function-by-function explanation
   - Part-by-part notebook flow
   - Cell-by-cell deep commentary
   - Line-by-line reading guide

## Command

```bash
cd /Users/praxlannister/Documents/Zoom/transcript-pipeline-kit
python3 scripts/run_colab_notebook_pipeline.py
```

Run a specific class only:

```bash
python3 scripts/run_colab_notebook_pipeline.py --only week5_tensors_pytorch
```

Dry run:

```bash
python3 scripts/run_colab_notebook_pipeline.py --dry-run
```

## Artifact Contract

For each Colab-enabled session:

- `<session>/final_notes.md` updated with resources + appendices
- `<session>/.pipeline/colab/<key>.ipynb`
- `<session>/.pipeline/colab/<key>_code_cells.py`
- `<session>/.pipeline/colab/<key>_manifest.json`

## Why This Is a Separate Pipeline

The transcript pipeline and the Colab explainer pipeline solve different problems:

- Transcript pipeline: source coverage, refinement, synthesis, pedagogical note generation.
- Colab pipeline: code pedagogy depth, API/function explanations, execution-level reasoning.

Separating them keeps each pipeline focused and composable.
