# Domain Corrections Reference

Use this file during Stage 1 when evaluating likely transcript errors.

## Correction Policy

1. Never overwrite low-confidence content silently.
2. Keep alternatives for MEDIUM/LOW confidence in `uncertainty_report.json`.
3. Prefer context-supported correction over dictionary-only correction.
4. Keep original phrase when ambiguity remains.

## Confidence Heuristic

- `HIGH` (>= 0.85): clear domain fit + grammatical fit + repeated usage in nearby segments.
- `MEDIUM` (0.60-0.84): plausible domain fit but at least one credible alternative.
- `LOW` (< 0.60): unclear domain fit or multiple equally likely interpretations.

## AI/ML Corrections

| Noisy transcript | Candidate | Notes |
|---|---|---|
| lowest function | loss function | common speech-to-text confusion |
| lows | loss | use nearby model training context |
| epic | epoch | training context required |
| wait matrix | weight matrix | model-parameter context |
| by torch | PyTorch | framework mention |
| tender flow | TensorFlow | framework mention |
| propagation | backpropagation | if gradients/training discussed |
| activation fanction | activation function | typo normalization |

## Web3 Corrections

| Noisy transcript | Candidate | Notes |
|---|---|---|
| soul anna | Solana | blockchain context |
| public key hash | public key / hash | keep both if ambiguous |
| sea phrase | seed phrase | wallet context |
| smart count track | smart contract | EVM/program context |
| gas fees high | gas fees | normalize minor grammar only |
| token minting address | mint address | if Solana SPL context |

## WebDev Corrections

| Noisy transcript | Candidate | Notes |
|---|---|---|
| call back hell | callback hell | async JS context |
| promiss | promise | JS async context |
| event luke | event loop | runtime context |
| node js thread pool | Node.js thread pool | capitalization normalization |
| io tax | I/O tasks | CPU vs IO context |
| resolve reject handler | resolve/reject handlers | promise context |

## Ambiguity Examples

Input: `Palabi`

- If person-name context: `Pallavi` (MEDIUM)
- If technical split context: `Pa labi` (LOW)
- If unknown context: keep `Palabi` with alternatives (LOW)

Always record alternatives with reason.

## Required Logging Fields

For each corrected segment, populate:

- `segment_id`
- `raw_text`
- `corrected_text`
- `confidence_tier`
- `confidence_score`
- `reasoning`

For uncertain segments, include:

- `segment_id`
- `original_text`
- `alternatives`
- `confidence_tier`
- `confidence_score`
- `reasoning`
- `status`
