#!/usr/bin/env python3
"""Rewrite generated lecture final_notes.md into tutorial-grade study guides.

This script keeps deterministic provenance artifacts untouched in .pipeline/
and only upgrades learner-facing final_notes.md content.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent
from typing import Callable, Iterable


STOPWORDS = {
    "know",
    "basically",
    "thing",
    "things",
    "one",
    "these",
    "different",
    "same",
    "now",
    "get",
    "see",
    "understand",
    "word",
    "every",
    "people",
    "code",
    "function",
    "call",
    "dot",
}


@dataclass
class Concept:
    name: str
    what: str
    intuition: str
    why: str
    formula: str | None = None
    pitfall: str | None = None
    next_step: str | None = None


@dataclass
class CodeExample:
    title: str
    language: str
    purpose: str
    code: str
    explain: list[str]


@dataclass
class GuideConfig:
    title: str
    domain: str
    tags: list[str]
    session_focus: str
    why_this_session_matters: str
    prerequisites: list[str]
    outcomes: list[str]
    roadmap_mermaid: str
    systems_mermaid: str
    skyline_ascii: str
    concepts: list[Concept]
    math_intuition: list[tuple[str, str, str]]
    examples: list[CodeExample]
    advanced_scenario: str
    hots: list[str]
    faqs: list[tuple[str, str]]
    practice_plan: list[tuple[str, str]]
    next_improvements: list[str]
    related_notes: list[str] = field(default_factory=list)


def _extract_topics(topic_inventory_path: Path, limit: int = 12) -> list[str]:
    if not topic_inventory_path.exists():
        return []
    try:
        obj = json.loads(topic_inventory_path.read_text())
    except Exception:
        return []

    values: list[str] = []
    if isinstance(obj, dict):
        for key in ("topics", "keywords", "topic_inventory", "items", "terms"):
            v = obj.get(key)
            if isinstance(v, list):
                values = _flatten_topic_values(v)
                if values:
                    break
        if not values:
            for v in obj.values():
                if isinstance(v, list):
                    values = _flatten_topic_values(v)
                    if values:
                        break
    elif isinstance(obj, list):
        values = _flatten_topic_values(obj)

    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in values:
        t = " ".join(raw.lower().strip().split())
        if not t or t in STOPWORDS:
            continue
        if len(t) == 1:
            continue
        if t in seen:
            continue
        seen.add(t)
        cleaned.append(t)
        if len(cleaned) >= limit:
            break
    return cleaned


def _flatten_topic_values(values: list[object]) -> list[str]:
    out: list[str] = []
    for item in values:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            for key in ("topic", "name", "keyword", "term", "title", "concept"):
                v = item.get(key)
                if isinstance(v, str):
                    out.append(v)
                    break
    return out


def _fmt_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {x}" for x in items)


def _fmt_callout_list(items: Iterable[str], title: str, ctype: str = "tip") -> str:
    body = "\n".join(f"> - {x}" for x in items)
    return f"> [!{ctype}] {title}\n{body}"


def _render(cfg: GuideConfig, topic_index: list[str], folder_name: str) -> str:
    topic_block = _fmt_list(topic_index or ["topic extraction unavailable; see .pipeline/topic_inventory.json"])
    prereq_block = _fmt_list(cfg.prerequisites)
    outcome_block = _fmt_list(cfg.outcomes)

    concept_sections: list[str] = []
    for idx, c in enumerate(cfg.concepts, start=1):
        lines = [
            f"### {idx}. {c.name}",
            f"**What it is:** {c.what}",
            f"**Intuition first:** {c.intuition}",
            f"**Why it matters:** {c.why}",
        ]
        if c.formula:
            lines.append(f"**Math lens:** `{c.formula}`")
        if c.pitfall:
            lines.append(f"**Common mistake:** {c.pitfall}")
        if c.next_step:
            lines.append(f"**Next improvement:** {c.next_step}")
        concept_sections.append("\n".join(lines))

    math_sections: list[str] = []
    for name, formula, intuition in cfg.math_intuition:
        math_sections.append(
            f"### {name}\n- Formula: `{formula}`\n- Intuition: {intuition}"
        )

    example_sections: list[str] = []
    for ex in cfg.examples:
        explain = "\n".join(f"- {item}" for item in ex.explain)
        example_sections.append(
            "\n".join(
                [
                    f"### {ex.title}",
                    f"**Why this example:** {ex.purpose}",
                    "",
                    f"```{ex.language}",
                    ex.code.strip(),
                    "```",
                    "",
                    "**What this code is doing:**",
                    explain,
                ]
            )
        )

    faq_sections = "\n\n".join(
        f"### Q: {q}\nA: {a}" for q, a in cfg.faqs
    )
    hots_sections = "\n".join(f"{i}. {q}" for i, q in enumerate(cfg.hots, start=1))
    practice_sections = "\n".join(
        f"- **{window}:** {task}" for window, task in cfg.practice_plan
    )
    next_sections = _fmt_list(cfg.next_improvements)

    related_block = "\n".join(f"- {note}" for note in cfg.related_notes) or "- [[Bootcamp Index]]"

    rendered = dedent(
        f"""
        ---
        title: "{cfg.title}"
        domain: "{cfg.domain}"
        tags: [{", ".join(cfg.tags)}]
        type: "tutorial-note"
        status: "ready"
        ---

# 🎓 {cfg.title}

> [!summary] 🧠 Session Focus
> {cfg.session_focus}

> [!important] 🚨 Why This Session Matters
> {cfg.why_this_session_matters}

> [!tip] 🧭 How To Use This Guide
> 1. Read the intuition lines first.
> 2. Then execute code examples.
> 3. Then solve HOTS + practice plan.

## 🎯 Prerequisites
{prereq_block}

## 🧭 Sanitized Topic Index (From Transcript)
{topic_block}

## ✅ Learning Outcomes
{outcome_block}

## 🗺️ Conceptual Roadmap
```mermaid
{cfg.roadmap_mermaid.strip()}
```

## 🏗️ Systems Visualization
```mermaid
{cfg.systems_mermaid.strip()}
```

## 🌆 Skyline Intuition Diagram
```text
{cfg.skyline_ascii.strip()}
```

## 📚 Core Concepts (Intuition First)
{'\n\n'.join(concept_sections)}

## ➗ Mathematical Intuition
{'\n\n'.join(math_sections)}

## 💻 Coding Walkthroughs
{'\n\n'.join(example_sections)}

## 🚀 Advanced Real-World Scenario
{cfg.advanced_scenario}

## 🧩 HOTS (High-Order Thinking)
{hots_sections}

## ❓ FAQ
{faq_sections}

## 🛠️ Practice Roadmap
{practice_sections}

## 🔭 Next Improvements
{next_sections}

## 🔗 Related Notes
{related_block}

## 🧾 Traceability
> [!info] Audit Trail
> This learner-facing guide is sanitized for readability. Full deterministic traceability remains in:
> - `.pipeline/segment_ledger.jsonl`
> - `.pipeline/coverage_matrix.json`
        > - `.pipeline/validation_report.md`
        > - `.pipeline/topic_inventory.json`

        ---

        > [!quote] Final Reminder
        > Intuition before memorization, implementation before confidence, validation before conclusion.
        """
    ).strip() + "\n"

    # Keep markdown flush-left for cleaner rendering in Obsidian and Git viewers.
    lines = [line[8:] if line.startswith("        ") else line for line in rendered.splitlines()]
    return "\n".join(lines).rstrip() + "\n"


def _cfg_ai_fasttrack() -> GuideConfig:
    return GuideConfig(
        title="Fast-tracking the AI Course (AI/ML Bootcamp 1.0) - Master Study Guide",
        domain="AI/ML",
        tags=["study-guide", "bootcamp", "ai-ml", "roadmap", "intuition"],
        session_focus="A fast strategic orientation to AI/ML: what to learn first, what to delay, and how training, loss, gradients, transformers, and deployment connect.",
        why_this_session_matters="Most learners fail by learning advanced topics out of order. This session builds the dependency map so your future effort compounds instead of fragmenting.",
        prerequisites=[
            "Python basics (functions, loops, lists)",
            "High-school algebra and plotting intuition",
            "Basic coding workflow (run script, inspect output)",
        ],
        outcomes=[
            "Build a correct mental model of the ML pipeline from dataset to inference.",
            "Explain loss and gradient descent without memorized jargon.",
            "Understand where transformers fit relative to classical neural models.",
            "Create a realistic practice path from beginner to interview-ready.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[Problem Definition] --> B[Data Collection]
  B --> C[Feature or Token Representation]
  C --> D[Model Choice]
  D --> E[Training Loop]
  E --> F[Evaluation]
  F --> G[Inference]
  G --> H[Iteration]
""",
        systems_mermaid="""
flowchart TD
  X[Input Data] --> Y[Forward Pass]
  Y --> Z[Prediction]
  Z --> L[Loss]
  L --> G[Gradient]
  G --> U[Parameter Update]
  U --> Y
""",
        skyline_ascii="""
Data Quality    Model Capacity    Optimization    Evaluation
     /\\              /\\               /\\             /\\
    /  \\            /  \\             /  \\           /  \\
---/----\\----------/----\\-----------/----\\---------/----\\----> learning maturity
""",
        concepts=[
            Concept(
                name="Training Loop",
                what="A repeated cycle of predict -> measure error -> update parameters.",
                intuition="Like repeatedly tuning a guitar string: hear wrong pitch, adjust tension, re-check.",
                why="Without the loop, a model stays random and cannot improve.",
                formula="theta_new = theta_old - alpha * grad(loss)",
                pitfall="Optimizing only training loss and ignoring validation behavior.",
                next_step="Track both train and validation curves from day one.",
            ),
            Concept(
                name="Loss Landscape",
                what="A surface showing how good or bad parameter settings are.",
                intuition="A hilly terrain where you need to walk downhill to reach a valley.",
                why="Explains why learning rate and initialization matter so much.",
                formula="L(theta) = average(error over dataset)",
                pitfall="Assuming one gradient step always improves generalization.",
                next_step="Use small experiments to visualize overfitting and underfitting.",
            ),
            Concept(
                name="Transformer Positioning",
                what="Transformers are sequence models built around attention, not recurrence.",
                intuition="Instead of reading one token strictly in order, each token can consult relevant tokens directly.",
                why="Required for modern NLP/LLM systems.",
                formula="Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V",
                pitfall="Treating attention as magic without understanding tokenization and context length.",
                next_step="Implement a toy attention block on a tiny sentence dataset.",
            ),
        ],
        math_intuition=[
            (
                "Gradient Descent Update",
                "theta <- theta - alpha * dL/dtheta",
                "The gradient points uphill; subtracting it moves parameters downhill toward lower error.",
            ),
            (
                "Mean Squared Error",
                "MSE = (1/n) * sum((y_hat - y)^2)",
                "Squaring punishes large mistakes more, which helps the model correct big misses earlier.",
            ),
        ],
        examples=[
            CodeExample(
                title="Minimal Training Loop (NumPy)",
                language="python",
                purpose="Demonstrates the full predict-loss-update cycle in compact form.",
                code="""
import numpy as np

X = np.array([[1.0], [2.0], [3.0]])
y = np.array([[2.0], [4.0], [6.0]])

w = np.random.randn(1, 1)
b = np.zeros((1,))
lr = 0.05

for step in range(500):
    y_hat = X @ w + b
    err = y_hat - y
    loss = (err ** 2).mean()

    dw = (2 / len(X)) * X.T @ err
    db = (2 / len(X)) * err.sum(axis=0)

    w -= lr * dw
    b -= lr * db

print('w, b, loss:', w.ravel()[0], b[0], loss)
""",
                explain=[
                    "`y_hat` computes predictions with current parameters.",
                    "`loss` quantifies prediction error; lower is better.",
                    "`dw` and `db` are gradients used to update parameters.",
                    "Repeated updates gradually fit the line to data.",
                ],
            ),
            CodeExample(
                title="Tokenizer + Embedding Sketch",
                language="python",
                purpose="Connects text preprocessing to model-ready vectors.",
                code="""
import numpy as np

vocab = {'i': 0, 'love': 1, 'ai': 2}
embedding = np.random.randn(len(vocab), 8)

sentence = ['i', 'love', 'ai']
tokens = [vocab[w] for w in sentence]
vecs = embedding[tokens]

print('token ids:', tokens)
print('embedding shape:', vecs.shape)
""",
                explain=[
                    "Words become integer token IDs.",
                    "Embedding table maps each token to a dense vector.",
                    "These vectors are the actual inputs to neural models.",
                ],
            ),
        ],
        advanced_scenario=(
            "You are building a domain-specific QA assistant for legal docs. Use this roadmap to decide stage gates: data cleaning quality threshold, baseline model selection, loss tracking policy, and deployment acceptance criteria. The key point is pipeline discipline: weak data with a large model still fails in production."
        ),
        hots=[
            "If training loss decreases but validation loss rises, what exactly is happening, and which two interventions would you prioritize first?",
            "When would a smaller model outperform a larger model in real projects?",
            "How do you choose between adding data vs tuning architecture?",
            "Why is 'more epochs' sometimes harmful?",
        ],
        faqs=[
            (
                "Should I learn transformer internals before mastering gradient descent?",
                "No. If optimization basics are weak, transformer internals become memorization without control.",
            ),
            (
                "Can I skip math and still build AI apps?",
                "You can build demos, but debugging and scaling model behavior requires at least optimization intuition.",
            ),
        ],
        practice_plan=[
            ("Day 1", "Implement linear regression from scratch and log loss each 50 steps."),
            ("Week 1", "Train one MLP and one attention toy model; compare failure modes."),
            ("Week 2", "Write a one-page postmortem on overfitting in your own experiment."),
        ],
        next_improvements=[
            "Add experiment tracking (metrics, config, seeds) to every training run.",
            "Build a reusable evaluation checklist (accuracy + latency + robustness).",
            "Create one small end-to-end project with deployment, not just notebook results.",
        ],
        related_notes=[
            "[[Week 3 - AI and ML - Neural Networks from Scratch]]",
            "[[Week 3 - AI&ML - Transformers Part 1]]",
            "[[Week 4 - AI&ML - Transformers Part 2]]",
        ],
    )


def _cfg_ai_nn_scratch() -> GuideConfig:
    return GuideConfig(
        title="Week 3 AI/ML - Neural Networks from Scratch (Bootcamp 1.0) - Master Study Guide",
        domain="AI/ML",
        tags=["study-guide", "bootcamp", "ai-ml", "neural-networks", "math-intuition"],
        session_focus="Build neural networks from first principles: neuron equation, forward pass, loss, backpropagation, learning rate behavior, and optimization stability.",
        why_this_session_matters="If this session is strong, advanced AI topics become understandable instead of magical.",
        prerequisites=[
            "Matrix multiplication basics",
            "Python + NumPy basics",
            "Comfort with plotting simple curves",
        ],
        outcomes=[
            "Derive and explain `y_hat = wx + b` as a reusable building block.",
            "Explain how loss guides updates and why gradients encode direction.",
            "Diagnose bad learning rates by reading training behavior.",
            "Connect handwritten NumPy code to equivalent PyTorch abstractions.",
        ],
        roadmap_mermaid="""
flowchart TD
  A[Input Features] --> B[Weighted Sum]
  B --> C[Activation]
  C --> D[Prediction]
  D --> E[Loss]
  E --> F[Backpropagation]
  F --> G[Update Weights]
  G --> B
""",
        systems_mermaid="""
flowchart LR
  X[Small LR] --> Y[Slow but Stable]
  A[Right LR] --> B[Fast Convergence]
  M[Large LR] --> N[Oscillation or Divergence]
""",
        skyline_ascii="""
Loss
^                    x (too high LR bounce)
|            x
|       x
|   x
| x
+--------------------------------------> iterations
  smooth descent = good LR regime
""",
        concepts=[
            Concept(
                name="Neuron as a Function",
                what="A neuron computes a weighted combination plus bias, then optional non-linearity.",
                intuition="Think of each weight as a volume knob controlling feature influence.",
                why="Everything in deep learning is a stacked extension of this unit.",
                formula="z = w.x + b, y_hat = activation(z)",
                pitfall="Ignoring feature scaling, which destabilizes optimization.",
                next_step="Normalize inputs before training and compare convergence speed.",
            ),
            Concept(
                name="Loss and Error Signal",
                what="Loss translates prediction quality into a scalar objective.",
                intuition="A scoreboard that tells the model how wrong it is right now.",
                why="Without a differentiable loss, training cannot compute useful updates.",
                formula="MSE = (1/n) * sum((y_hat - y)^2)",
                pitfall="Comparing raw loss values across tasks with different scales.",
                next_step="Track trend and relative improvement, not just absolute value.",
            ),
            Concept(
                name="Backpropagation",
                what="Backprop applies chain rule to compute each parameter's contribution to error.",
                intuition="Blame assignment: which parameter caused how much of the mistake?",
                why="Enables learning in multi-layer networks with many parameters.",
                formula="dL/dw = dL/dy_hat * dy_hat/dz * dz/dw",
                pitfall="Updating with wrong sign and accidentally increasing loss.",
                next_step="Numerically check gradients with finite differences on tiny models.",
            ),
        ],
        math_intuition=[
            (
                "Linear Unit",
                "y_hat = w.x + b",
                "`w` controls slope/sensitivity; `b` shifts decision boundary without changing slope.",
            ),
            (
                "Gradient Step",
                "w <- w - alpha * dL/dw",
                "`alpha` decides step size; too low is slow, too high overshoots minima.",
            ),
            (
                "Binary Cross-Entropy (classification)",
                "BCE = -[y log(p) + (1-y) log(1-p)]",
                "Punishes confident wrong predictions heavily, which helps calibration.",
            ),
        ],
        examples=[
            CodeExample(
                title="Single-Layer Regression From Scratch",
                language="python",
                purpose="Shows end-to-end forward, loss, gradient, and update without frameworks.",
                code="""
import numpy as np

X = np.array([[1.0], [2.0], [3.0], [4.0]])
y = np.array([[3.0], [5.0], [7.0], [9.0]])  # y = 2x + 1

w = np.random.randn(1, 1)
b = np.zeros((1,))
lr = 0.03

for step in range(1000):
    z = X @ w + b
    y_hat = z
    err = y_hat - y
    loss = (err ** 2).mean()

    dw = (2 / len(X)) * X.T @ err
    db = (2 / len(X)) * err.sum(axis=0)

    w -= lr * dw
    b -= lr * db

print('learned:', w.ravel()[0], b[0], 'loss:', loss)
""",
                explain=[
                    "The model starts random and iteratively corrects itself.",
                    "Gradient direction comes from current error.",
                    "After enough iterations, learned parameters approximate ground truth.",
                ],
            ),
            CodeExample(
                title="Equivalent PyTorch Sketch",
                language="python",
                purpose="Bridges intuition from manual math to production tooling.",
                code="""
import torch

X = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
y = torch.tensor([[3.0], [5.0], [7.0], [9.0]])

model = torch.nn.Linear(1, 1)
opt = torch.optim.SGD(model.parameters(), lr=0.03)
loss_fn = torch.nn.MSELoss()

for _ in range(1000):
    pred = model(X)
    loss = loss_fn(pred, y)
    opt.zero_grad()
    loss.backward()
    opt.step()

print('weight,bias:', list(model.parameters()))
""",
                explain=[
                    "Framework APIs automate gradient computation and parameter updates.",
                    "The underlying math is still the same as the manual version.",
                    "This mapping is crucial for debugging real models.",
                ],
            ),
        ],
        advanced_scenario=(
            "You are predicting demand for a quick-commerce app. Sudden festivals create data shifts. Use your learning-rate and loss intuition to avoid unstable retraining. Add drift checks before blindly updating production weights."
        ),
        hots=[
            "How would you prove (not guess) that your learning rate is too high?",
            "If train loss decreases but business KPI worsens, what mismatch could explain it?",
            "When does MSE become a poor choice despite easy optimization?",
            "How would you explain backprop to a non-math teammate in 30 seconds?",
        ],
        faqs=[
            (
                "Do I need calculus to start?",
                "You can start with intuition and code; calculus depth helps when debugging optimization pathologies.",
            ),
            (
                "Why does normalization help?",
                "It keeps feature scales comparable so one feature does not dominate gradient updates unfairly.",
            ),
        ],
        practice_plan=[
            ("Today", "Implement XOR with one hidden layer and observe why linear models fail."),
            ("This week", "Run three learning rates and compare convergence curves."),
            ("Next week", "Rebuild the same model in PyTorch and annotate every API to math mapping."),
        ],
        next_improvements=[
            "Add gradient checking utility for custom layers.",
            "Log parameter norms to detect exploding updates.",
            "Introduce regularization and compare generalization impact.",
        ],
        related_notes=[
            "[[Fast-tracking the AI course]]",
            "[[Week 3 - AI&ML - Transformers Part 1]]",
        ],
    )


def _cfg_ai_transformers_p1() -> GuideConfig:
    return GuideConfig(
        title="Week 3 AI/ML - Transformers Part 1 (Bootcamp 1.0) - Master Study Guide",
        domain="AI/ML",
        tags=["study-guide", "bootcamp", "ai-ml", "transformers", "attention"],
        session_focus="Foundational transformer mechanics: tokenization, embeddings, positional information, and self-attention intuition.",
        why_this_session_matters="Part 1 is where transformer intuition is built. If this is weak, Part 2 feels like symbol memorization.",
        prerequisites=[
            "Neural network basics (forward pass + loss)",
            "Vectors and dot product intuition",
            "Basic NLP idea of words/tokens",
        ],
        outcomes=[
            "Explain why tokenization is not a cosmetic preprocessing step.",
            "Understand embedding vectors as learned semantic coordinates.",
            "Derive scaled dot-product attention at intuition level.",
            "Build a toy attention implementation for a short sentence.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[Raw Text] --> B[Tokenization]
  B --> C[Token Embeddings]
  C --> D[Positional Encoding]
  D --> E[Self-Attention]
  E --> F[Contextual Representation]
""",
        systems_mermaid="""
flowchart TD
  Q[Query] --> S[Similarity Scores]
  K[Key] --> S
  S --> W[Softmax Weights]
  W --> V[Weighted Sum of Values]
""",
        skyline_ascii="""
Token -> Embedding -> Position -> Attention -> Context Vector
           |             |            |          |
        semantics      order       relevance   meaning-in-context
""",
        concepts=[
            Concept(
                name="Tokenization",
                what="Converts text into model-consumable discrete units.",
                intuition="Like choosing the Lego brick size before building a structure.",
                why="Bad tokenization inflates sequence length and harms efficiency and meaning capture.",
                formula="text -> [t1, t2, ... tn]",
                pitfall="Assuming words are always tokens; many tokenizers split words into subwords.",
                next_step="Compare token counts for same sentence across tokenizers.",
            ),
            Concept(
                name="Embeddings + Position",
                what="Embeddings encode semantic identity; positional encoding injects order.",
                intuition="Content is 'what', position is 'where'. Both are needed to form sentence meaning.",
                why="Without position, bag-of-token ambiguity destroys sequence semantics.",
                formula="x_i = token_embed_i + pos_embed_i",
                pitfall="Treating embeddings as static dictionaries; they evolve during training.",
                next_step="Visualize cosine similarity between learned token vectors.",
            ),
            Concept(
                name="Self-Attention",
                what="Each token weighs other tokens to build context-aware representation.",
                intuition="Every word asks: which other words should I listen to, and by how much?",
                why="Allows long-range dependency modeling without recurrence.",
                formula="softmax(QK^T / sqrt(d_k))V",
                pitfall="Ignoring masking rules in sequence models.",
                next_step="Implement attention with and without mask; inspect output differences.",
            ),
        ],
        math_intuition=[
            (
                "Scaled Dot Product",
                "score_ij = (q_i · k_j) / sqrt(d_k)",
                "Scaling prevents large dot products from saturating softmax early.",
            ),
            (
                "Attention Weights",
                "a_ij = exp(score_ij) / sum_j exp(score_ij)",
                "Softmax converts similarity into probability-like weights.",
            ),
        ],
        examples=[
            CodeExample(
                title="Toy Attention Over 3 Tokens",
                language="python",
                purpose="Makes attention mechanics transparent without framework magic.",
                code="""
import numpy as np

X = np.array([
    [1.0, 0.0],
    [0.0, 1.0],
    [1.0, 1.0],
])

Q = X
K = X
V = X

scores = Q @ K.T / np.sqrt(Q.shape[-1])
weights = np.exp(scores) / np.exp(scores).sum(axis=1, keepdims=True)
context = weights @ V

print('weights:\n', weights)
print('context:\n', context)
""",
                explain=[
                    "`scores` measure pairwise relevance between tokens.",
                    "`weights` normalize relevance into attention allocation.",
                    "`context` is the meaning update after looking at other tokens.",
                ],
            ),
            CodeExample(
                title="PyTorch MultiheadAttention Quickstart",
                language="python",
                purpose="Bridges conceptual attention to real API usage.",
                code="""
import torch

mha = torch.nn.MultiheadAttention(embed_dim=32, num_heads=4, batch_first=True)
x = torch.randn(2, 6, 32)  # batch, seq_len, dim
out, attn = mha(x, x, x, need_weights=True)

print(out.shape)   # (2, 6, 32)
print(attn.shape)  # (2, 6, 6)
""",
                explain=[
                    "Self-attention uses same tensor as Q, K, V in encoder blocks.",
                    "Attention matrix exposes which positions influenced each token.",
                    "Inspecting attention maps is useful but not a full explanation tool.",
                ],
            ),
        ],
        advanced_scenario=(
            "You need a ticket-routing assistant for multilingual support chats. Use tokenizer diagnostics and embedding coverage checks before training any large transformer. Many failures in production start at tokenization mismatch, not at model size."
        ),
        hots=[
            "Why does tokenization quality directly affect model latency and cost?",
            "What breaks if positional encoding is removed from a transformer encoder?",
            "When can attention maps be misleading as explanations?",
            "How would you design an experiment to compare two tokenizers fairly?",
        ],
        faqs=[
            (
                "Is self-attention always better than RNNs?",
                "Not always. For very small datasets or strict latency constraints, simpler architectures may win.",
            ),
            (
                "Why split into multiple heads?",
                "Different heads can specialize in different relation patterns (syntax, coreference, position).",
            ),
        ],
        practice_plan=[
            ("Today", "Implement attention manually for a 3-token toy input."),
            ("This week", "Visualize attention weights for 20 sample sentences."),
            ("Next week", "Benchmark two tokenizers on same corpus and compare token inflation."),
        ],
        next_improvements=[
            "Add causal mask and compare bidirectional vs causal behavior.",
            "Study residual connections + layer norm before deeper stacks.",
            "Track memory complexity as sequence length grows.",
        ],
        related_notes=[
            "[[Week 3 - AI and ML - Neural Networks from Scratch]]",
            "[[Week 4 - AI&ML - Transformers Part 2]]",
        ],
    )


def _cfg_ai_transformers_p2() -> GuideConfig:
    return GuideConfig(
        title="Week 4 AI/ML - Transformers Part 2 (Bootcamp 1.0) - Master Study Guide",
        domain="AI/ML",
        tags=["study-guide", "bootcamp", "ai-ml", "transformers", "training"],
        session_focus="Transformer deepening: multi-head attention, masking, feed-forward blocks, optimization, and practical training behavior.",
        why_this_session_matters="Part 2 converts conceptual understanding into trainable system thinking and debugging discipline.",
        prerequisites=[
            "Transformers Part 1 fundamentals",
            "Softmax and matrix multiplication basics",
            "Loss and gradient descent intuition",
        ],
        outcomes=[
            "Explain why multi-head attention improves representational flexibility.",
            "Understand causal masking and why it prevents leakage.",
            "Trace full block flow: attention -> add&norm -> FFN -> add&norm.",
            "Connect model quality to optimization choices and evaluation metrics.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[Token + Position Embeddings] --> B[Multi-Head Attention]
  B --> C[Add & LayerNorm]
  C --> D[Feed Forward Network]
  D --> E[Add & LayerNorm]
  E --> F[Logits]
  F --> G[Cross-Entropy Loss]
""",
        systems_mermaid="""
flowchart TD
  M[Causal Mask] --> S[Masked Scores]
  Q[Queries] --> S
  K[Keys] --> S
  S --> W[Softmax]
  W --> V[Values]
  V --> O[Context Output]
""",
        skyline_ascii="""
Context Quality
^            stable training zone
|         _________
|        /         \\
|_______/           \\_______
+---------------------------------> model depth / complexity
  too shallow             too unstable
""",
        concepts=[
            Concept(
                name="Multi-Head Attention",
                what="Runs attention in parallel subspaces, then concatenates results.",
                intuition="Multiple experts reading same sentence, each focusing on different relation signals.",
                why="One head may miss structure that another head captures.",
                formula="head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)",
                pitfall="Increasing heads without enough embedding dimension can reduce per-head capacity.",
                next_step="Profile accuracy/latency tradeoff while varying head count.",
            ),
            Concept(
                name="Causal Masking",
                what="Prevents token i from attending to future tokens j > i during autoregressive training.",
                intuition="A student cannot peek at future answers while taking a test.",
                why="Without masking, training leaks future information and invalidates generation behavior.",
                formula="mask_ij = -inf for j > i",
                pitfall="Mask shape mismatch silently breaks training semantics.",
                next_step="Unit-test attention logits for masked positions.",
            ),
            Concept(
                name="Training Stability",
                what="Optimization behavior controlled by LR schedule, normalization, and gradient health.",
                intuition="Even strong architecture fails if optimization 'heartbeat' is unstable.",
                why="Large models amplify optimization mistakes quickly.",
                formula="perplexity = exp(cross_entropy)",
                pitfall="Reading only train loss without validation perplexity trends.",
                next_step="Track gradient norm and perplexity together.",
            ),
        ],
        math_intuition=[
            (
                "Cross-Entropy",
                "CE = -sum(y * log(p))",
                "Measures surprise: high penalty when model assigns low probability to true class.",
            ),
            (
                "Perplexity",
                "PPL = exp(CE)",
                "Approximate branching factor; lower means model is less uncertain.",
            ),
            (
                "LayerNorm",
                "LN(x) = (x - mean(x)) / sqrt(var(x)+eps)",
                "Keeps internal activations in stable range, improving optimization.",
            ),
        ],
        examples=[
            CodeExample(
                title="Causal Mask Attention Snippet",
                language="python",
                purpose="Demonstrates no-lookahead behavior needed for next-token prediction.",
                code="""
import torch

B, T, D = 2, 5, 8
x = torch.randn(B, T, D)
q = k = v = x
scores = q @ k.transpose(-1, -2) / (D ** 0.5)

mask = torch.triu(torch.ones(T, T), diagonal=1).bool()
scores = scores.masked_fill(mask, float('-inf'))
weights = torch.softmax(scores, dim=-1)
out = weights @ v

print(out.shape)
""",
                explain=[
                    "Upper triangular mask blocks future token access.",
                    "Softmax then allocates attention only to allowed positions.",
                    "This matches autoregressive training constraints.",
                ],
            ),
            CodeExample(
                title="Mini Transformer Block in PyTorch",
                language="python",
                purpose="Shows production-like block composition.",
                code="""
import torch

class TinyBlock(torch.nn.Module):
    def __init__(self, d=64, h=4):
        super().__init__()
        self.attn = torch.nn.MultiheadAttention(d, h, batch_first=True)
        self.ln1 = torch.nn.LayerNorm(d)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(d, 4*d),
            torch.nn.GELU(),
            torch.nn.Linear(4*d, d),
        )
        self.ln2 = torch.nn.LayerNorm(d)

    def forward(self, x):
        a, _ = self.attn(x, x, x, need_weights=False)
        x = self.ln1(x + a)
        f = self.ffn(x)
        return self.ln2(x + f)
""",
                explain=[
                    "Residual connections preserve gradient flow in deeper stacks.",
                    "LayerNorm stabilizes intermediate activations.",
                    "FFN expands and compresses features for richer transformations.",
                ],
            ),
        ],
        advanced_scenario=(
            "You are fine-tuning a support chatbot model. During training, perplexity improves but hallucinations increase on domain FAQs. Introduce targeted evaluation slices, retrieval grounding, and stricter validation prompts before concluding quality improved."
        ),
        hots=[
            "Why can lower perplexity still produce worse user trust?",
            "When does adding more heads stop helping?",
            "How would you detect mask bugs without inspecting code manually?",
            "Which metric set would you monitor for production chatbot readiness?",
        ],
        faqs=[
            (
                "Does higher parameter count always improve performance?",
                "No. Data quality, objective alignment, and optimization setup can dominate outcomes.",
            ),
            (
                "Why use GELU in FFN blocks?",
                "It provides smoother activation behavior than ReLU in many transformer training settings.",
            ),
        ],
        practice_plan=[
            ("Today", "Implement causal mask and validate no future leakage."),
            ("This week", "Train tiny transformer on character dataset; log perplexity."),
            ("Next week", "Compare 2-head vs 8-head versions under fixed parameter budget."),
        ],
        next_improvements=[
            "Add gradient clipping and compare stability.",
            "Experiment with cosine LR scheduling.",
            "Introduce evaluation suite for hallucination and factuality checks.",
        ],
        related_notes=[
            "[[Week 3 - AI&ML - Transformers Part 1]]",
            "[[Fast-tracking the AI course]]",
        ],
    )


def _cfg_webdev_async_foundations() -> GuideConfig:
    return GuideConfig(
        title="Week 3 Web Development - Promises, Callbacks, CPU vs IO Tasks (Bootcamp 1.0) - Master Study Guide",
        domain="Web Development",
        tags=["study-guide", "bootcamp", "web-development", "async", "javascript"],
        session_focus="Core async JavaScript foundations: CPU vs IO tasks, call stack behavior, callbacks, event loop, and the move toward promises.",
        why_this_session_matters="This is the base layer for backend servers and frontend responsiveness. Weak async foundations lead to flaky apps and interview failures.",
        prerequisites=[
            "JavaScript functions and scopes",
            "Basic Node.js runtime usage",
            "Comfort with reading asynchronous code",
        ],
        outcomes=[
            "Differentiate CPU-bound and IO-bound work with runtime implications.",
            "Explain how call stack, callback queue, and event loop interact.",
            "Identify callback hell and refactor paths.",
            "Reason about responsiveness under blocking code.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[JS Call Stack] --> B[Invoke Async API]
  B --> C[Web API / Libuv Handles IO]
  C --> D[Callback Queue]
  D --> E[Event Loop]
  E --> F[Callback Executes on Stack]
""",
        systems_mermaid="""
flowchart TD
  X[CPU-heavy loop] --> Y[Stack blocked]
  Y --> Z[UI/requests delayed]
  A[IO async call] --> B[Stack free]
  B --> C[Other work continues]
""",
        skyline_ascii="""
Task Type      CPU-bound            IO-bound
Latency        grows with compute   mostly waiting
Thread impact  blocks event loop    scheduled via runtime APIs
""",
        concepts=[
            Concept(
                name="CPU vs IO Tasks",
                what="CPU tasks consume compute cycles; IO tasks spend most time waiting on external systems.",
                intuition="Cooking analogy: chopping vegetables (CPU) vs waiting for water to boil (IO).",
                why="Determines whether your app should optimize algorithmic work or async orchestration.",
                formula="response_time ~= cpu_time + io_wait + queue_delay",
                pitfall="Calling sync file/network APIs in hot request path.",
                next_step="Profile code path and label each segment CPU or IO.",
            ),
            Concept(
                name="Event Loop Mechanics",
                what="The event loop moves ready callbacks onto the call stack when stack is free.",
                intuition="A dispatcher only sends next task when current desk is free.",
                why="Explains timer behavior, callback order, and starvation issues.",
                formula="throughput ~= 1 / avg_service_time",
                pitfall="Assuming async means parallel execution by default.",
                next_step="Run experiments with blocking loop + setTimeout to observe delay.",
            ),
            Concept(
                name="Callback Composition",
                what="Callbacks pass control continuation explicitly after async operations complete.",
                intuition="You hand over a phone number to be called when work is done.",
                why="Historical base for promises and async/await ergonomics.",
                pitfall="Nested callbacks reduce readability and centralize error confusion.",
                next_step="Promisify one callback chain and compare complexity.",
            ),
        ],
        math_intuition=[
            (
                "Latency Budget",
                "T_total = T_cpu + T_io + T_queue",
                "Even fast code feels slow when queue delay accumulates under load.",
            ),
            (
                "Service Throughput",
                "RPS ~ 1 / T_service",
                "Reducing blocking service time increases request capacity.",
            ),
        ],
        examples=[
            CodeExample(
                title="Blocking vs Non-Blocking Demo",
                language="js",
                purpose="Visualizes runtime difference between CPU blocking and async callback scheduling.",
                code="""
const fs = require('fs');

console.log('1. start');

setTimeout(() => {
  console.log('4. timer callback');
}, 0);

for (let i = 0; i < 1e8; i++) {}
console.log('2. after CPU loop');

fs.readFile(__filename, 'utf8', () => {
  console.log('5. file read callback');
});

console.log('3. script end');
""",
                explain=[
                    "The heavy loop blocks the stack first.",
                    "Timer callback cannot run until loop completes.",
                    "File read callback appears later once IO completes and loop is free.",
                ],
            ),
            CodeExample(
                title="Callback to Promise Refactor",
                language="js",
                purpose="Shows migration path to cleaner control flow.",
                code="""
const fs = require('fs');
const { promisify } = require('util');

const readFileAsync = promisify(fs.readFile);

async function loadConfig(path) {
  try {
    const text = await readFileAsync(path, 'utf8');
    return JSON.parse(text);
  } catch (err) {
    throw new Error(`Config load failed: ${err.message}`);
  }
}
""",
                explain=[
                    "`promisify` wraps callback APIs in promise interface.",
                    "`async/await` linearizes flow for readability.",
                    "Centralized `try/catch` simplifies error handling.",
                ],
            ),
        ],
        advanced_scenario=(
            "A Node.js API slows down during traffic spikes. You discover synchronous JSON parsing of huge payloads on request path. Split heavy work into worker threads or streaming parser, keep IO non-blocking, and add queue-depth monitoring."
        ),
        hots=[
            "Why does `setTimeout(fn, 0)` still execute later than expected?",
            "How would you detect event-loop blocking in production?",
            "When should you use worker threads instead of promises?",
            "Which code smells indicate callback hell before it becomes unmaintainable?",
        ],
        faqs=[
            (
                "Is JavaScript truly single-threaded?",
                "The JS execution thread is single-threaded, but runtime delegates IO and can use thread pools/workers.",
            ),
            (
                "Do promises make code faster?",
                "Mostly they improve structure and error flow; performance depends on actual IO/CPU work.",
            ),
        ],
        practice_plan=[
            ("Today", "Write one script demonstrating callback order with timers and file IO."),
            ("This week", "Refactor one callback-based utility to async/await."),
            ("Next week", "Instrument event loop lag and create alert threshold."),
        ],
        next_improvements=[
            "Study Node.js worker threads for CPU-heavy workloads.",
            "Add circuit breaker and retry policies for unstable IO dependencies.",
            "Practice interview questions around event loop and microtask/macrotask behavior.",
        ],
        related_notes=[
            "[[Week 4 - Web Development - Promises]]",
            "[[Node.js Event Loop Deep Dive]]",
        ],
    )


def _cfg_webdev_promises_deep() -> GuideConfig:
    return GuideConfig(
        title="Week 4 Web Development - Promises (Bootcamp 1.0) - Master Study Guide",
        domain="Web Development",
        tags=["study-guide", "bootcamp", "web-development", "promises", "async-await"],
        session_focus="Deep promise usage: chaining, error propagation, finally semantics, and designing resilient async flows.",
        why_this_session_matters="Promise literacy is the difference between production-safe async code and fragile chains that fail silently.",
        prerequisites=[
            "Callback and event loop foundations",
            "Basic JavaScript classes/functions",
            "Experience with Node.js or browser async APIs",
        ],
        outcomes=[
            "Predict order and behavior of `.then`, `.catch`, and `.finally` chains.",
            "Refactor callback APIs into promise-based interfaces.",
            "Handle partial failures in multi-request workflows.",
            "Design retries, timeouts, and cleanup paths intentionally.",
        ],
        roadmap_mermaid="""
flowchart TD
  A[Async Operation] --> B{Resolved?}
  B -->|Yes| C[then handler]
  B -->|No| D[catch handler]
  C --> E[Next then]
  D --> E
  E --> F[finally cleanup]
""",
        systems_mermaid="""
flowchart LR
  X[Legacy callback API] --> Y[promisify wrapper]
  Y --> Z[async/await service layer]
  Z --> Q[retry + timeout + logging]
""",
        skyline_ascii="""
naive async -> nested callbacks -> promise chains -> async/await + guardrails
                               (readability)                (reliability)
""",
        concepts=[
            Concept(
                name="Promise State Model",
                what="A promise is pending, then settles to fulfilled or rejected exactly once.",
                intuition="A courier order that eventually resolves to delivered or failed, never both.",
                why="Prevents race-condition misunderstandings in asynchronous logic.",
                pitfall="Trying to resolve/reject multiple times and expecting multiple transitions.",
                next_step="Instrument state transitions in your own wrapper for visibility.",
            ),
            Concept(
                name="Chain Propagation",
                what="Return values and thrown errors flow through chain links predictably.",
                intuition="Each `.then` is a processing station; outputs become next station inputs.",
                why="Essential for composing multi-step async workflows without nesting.",
                formula="next = Promise.resolve(handler(prev))",
                pitfall="Forgetting `return` inside `.then`, causing undefined propagation.",
                next_step="Write a chain with intentional errors and trace behavior step-by-step.",
            ),
            Concept(
                name="Failure Design",
                what="Reliable async code plans retries, timeout, fallback, and cleanup.",
                intuition="Airline operations always include disruption handling, not just ideal routes.",
                why="Real systems fail at boundaries (network, storage, third-party services).",
                pitfall="Catch-all error swallowing without logging or remediation path.",
                next_step="Add structured error categories and remediation actions.",
            ),
        ],
        math_intuition=[
            (
                "Expected Latency under Retry",
                "E[T] ~= T_base + p_fail * T_retry",
                "Retries improve success probability but increase tail latency.",
            ),
            (
                "Composite Success Probability",
                "P(success by n tries) = 1 - (p_fail)^n",
                "Useful for deciding retry count and cost tradeoff.",
            ),
        ],
        examples=[
            CodeExample(
                title="Promise Chain With Recovery",
                language="js",
                purpose="Shows linear success path with targeted recovery and cleanup.",
                code="""
function fetchJson(url) {
  return fetch(url).then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
}

fetchJson('/api/user')
  .then((u) => fetchJson(`/api/users/${u.id}/projects`))
  .then((projects) => ({ count: projects.length, projects }))
  .catch((err) => {
    console.error('primary flow failed:', err.message);
    return { count: 0, projects: [] };
  })
  .finally(() => {
    console.log('cleanup complete');
  });
""",
                explain=[
                    "Errors thrown in any handler move to nearest `.catch`.",
                    "Recovery object keeps downstream consumers stable.",
                    "`.finally` executes regardless of success or failure.",
                ],
            ),
            CodeExample(
                title="Retry + Timeout Wrapper",
                language="js",
                purpose="Demonstrates production-grade async guardrails.",
                code="""
async function withTimeout(promise, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('timeout')), ms)
  );
  return Promise.race([promise, timeout]);
}

async function retry(fn, attempts = 3) {
  let lastErr;
  for (let i = 1; i <= attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      if (i === attempts) throw err;
    }
  }
  throw lastErr;
}
""",
                explain=[
                    "`Promise.race` enforces deadline behavior.",
                    "Retry isolates transient failures without duplicating call sites.",
                    "Keep retry count bounded to avoid cascading load spikes.",
                ],
            ),
        ],
        advanced_scenario=(
            "Your checkout flow calls payment, inventory, and notification services. A payment success with inventory timeout must not produce inconsistent order state. Use idempotency keys, compensating actions, and explicit promise orchestration policy."
        ),
        hots=[
            "Why can over-retrying make an outage worse?",
            "Where should timeout live: caller, callee, or both?",
            "How would you design idempotent retries for payment APIs?",
            "What is the difference between business failure and technical failure in promise chains?",
        ],
        faqs=[
            (
                "Should I always use async/await instead of then/catch?",
                "Use whichever yields clearer control flow; both compile to promise semantics.",
            ),
            (
                "What does finally return behavior do?",
                "`finally` runs side effects and does not replace resolved value unless it throws.",
            ),
        ],
        practice_plan=[
            ("Today", "Refactor one callback chain to promise chain with explicit error categories."),
            ("This week", "Add timeout + retry wrappers to one API integration module."),
            ("Next week", "Run chaos tests for flaky endpoints and review fallback behavior."),
        ],
        next_improvements=[
            "Add circuit breaker for repeatedly failing dependencies.",
            "Instrument promise rejection telemetry with request correlation IDs.",
            "Adopt lint rules that prevent floating promises.",
        ],
        related_notes=[
            "[[Week 3 - Web Development - Promises, Callbacks, CPU vs IO Tasks]]",
            "[[Node.js Reliability Patterns]]",
        ],
    )


def _cfg_web3_intro() -> GuideConfig:
    return GuideConfig(
        title="Web3 - Introduction to Blockchains (Bootcamp 1.0) - Master Study Guide",
        domain="Web3",
        tags=["study-guide", "bootcamp", "web3", "blockchain", "foundations"],
        session_focus="Blockchain first principles: why blockchains exist, how transactions are validated, and how distributed trust is established.",
        why_this_session_matters="Without this base, wallet, smart contract, and token topics become disconnected buzzwords.",
        prerequisites=[
            "Basic internet/client-server understanding",
            "High-level cryptography intuition",
            "Curiosity about distributed systems",
        ],
        outcomes=[
            "Explain blockchain as append-only shared state.",
            "Trace transaction lifecycle from signing to finality.",
            "Compare centralized ledger trust vs decentralized consensus.",
            "Recognize common misconceptions around decentralization.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[User Creates Tx] --> B[Sign with Private Key]
  B --> C[Broadcast to Network]
  C --> D[Validator Verification]
  D --> E[Block Inclusion]
  E --> F[State Update]
  F --> G[Confirmation/Finality]
""",
        systems_mermaid="""
flowchart TD
  X[Node A Ledger] --> M[Consensus]
  Y[Node B Ledger] --> M
  Z[Node C Ledger] --> M
  M --> U[Shared Canonical State]
""",
        skyline_ascii="""
Centralized DB: one writer, one trust anchor
Blockchain   : many writers/validators, shared verification rules
""",
        concepts=[
            Concept(
                name="Distributed Ledger",
                what="A replicated state machine where multiple nodes store and validate state transitions.",
                intuition="A shared notebook where each new page must satisfy community-agreed rules.",
                why="Removes single points of trust and censorship resistance bottlenecks.",
                pitfall="Confusing replication with decentralization; governance concentration still matters.",
                next_step="Map validator concentration for a chosen chain.",
            ),
            Concept(
                name="Transaction + Signature",
                what="Transactions describe state changes and signatures prove authorization.",
                intuition="Like signed bank instructions where signature proves ownership intent.",
                why="Prevents unauthorized spending and preserves non-repudiation.",
                formula="verify(pubkey, message, signature) -> true/false",
                pitfall="Assuming broadcast means immediate finality.",
                next_step="Measure confirmation depth required for your risk tolerance.",
            ),
            Concept(
                name="Consensus and Finality",
                what="Consensus chooses valid ordering of transactions under adversarial conditions.",
                intuition="A distributed meeting protocol that must agree despite network delays.",
                why="Ordering determines balances and contract outcomes.",
                pitfall="Treating all chains as equivalent on finality speed and security model.",
                next_step="Compare probabilistic vs deterministic finality chains.",
            ),
        ],
        math_intuition=[
            (
                "Hash Pointer",
                "block_hash = H(block_header + tx_root + prev_hash)",
                "Any tampering changes hash and breaks chain linkage.",
            ),
            (
                "State Invariant",
                "total_supply_after = total_supply_before + minted - burned",
                "Ledger updates must preserve defined invariants after each block.",
            ),
        ],
        examples=[
            CodeExample(
                title="Toy Block Hashing",
                language="python",
                purpose="Builds intuition for tamper-evident chaining.",
                code="""
import hashlib
import json


def block_hash(prev_hash, txs, nonce):
    payload = json.dumps({
        'prev_hash': prev_hash,
        'txs': txs,
        'nonce': nonce,
    }, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()

h1 = block_hash('genesis', ['A->B:5'], 1)
h2 = block_hash(h1, ['B->C:2'], 9)
print(h1, h2)
""",
                explain=[
                    "Each block includes previous hash reference.",
                    "Changing older transaction data changes all downstream hashes.",
                    "This enables tamper evidence, not absolute impossibility of attack.",
                ],
            ),
            CodeExample(
                title="Transaction Validation Checklist (Pseudo)",
                language="text",
                purpose="Shows validator decision sequence.",
                code="""
1) Parse tx format
2) Verify signature against sender public key
3) Check nonce / replay protection
4) Check sender balance or account constraints
5) Simulate state transition
6) Accept into mempool if valid
""",
                explain=[
                    "Validation rejects malformed or unauthorized transactions early.",
                    "Replay checks prevent duplicate execution of old signed messages.",
                    "State simulation avoids invalid block proposals.",
                ],
            ),
        ],
        advanced_scenario=(
            "A remittance startup must choose a chain for cross-border transfers. Use throughput, finality, fee volatility, and validator decentralization as decision criteria instead of only token popularity."
        ),
        hots=[
            "Why is append-only history useful but not sufficient for trust minimization?",
            "How does mempool behavior impact user experience and MEV risk?",
            "When can a technically decentralized network still be governance-centralized?",
            "What confirmation depth should different payment sizes require and why?",
        ],
        faqs=[
            (
                "Are blockchains always slower than databases?",
                "For many workloads yes, because consensus adds overhead. The tradeoff buys trust minimization, not raw speed.",
            ),
            (
                "Is every token transfer a smart contract call?",
                "Depends on chain architecture; native transfers and program-based transfers differ.",
            ),
        ],
        practice_plan=[
            ("Today", "Draw full transaction lifecycle for one chain of your choice."),
            ("This week", "Compare finality and fee models of two chains."),
            ("Next week", "Simulate ledger state updates for 20 mock transactions."),
        ],
        next_improvements=[
            "Study consensus attacks and liveness/safety tradeoffs.",
            "Learn mempool and fee market dynamics in depth.",
            "Build a small block explorer-style parser for chain data.",
        ],
        related_notes=[
            "[[Week 3 - Web3 - Wallets and Private Keys]]",
            "[[Week 4 - Web3 - Token Program]]",
        ],
    )


def _cfg_web3_wallets() -> GuideConfig:
    return GuideConfig(
        title="Week 3 Web3 - Wallets and Private Keys (Bootcamp 1.0) - Master Study Guide",
        domain="Web3",
        tags=["study-guide", "bootcamp", "web3", "wallets", "security"],
        session_focus="Wallet and key management fundamentals: private/public keys, signatures, seed phrases, and operational security.",
        why_this_session_matters="Most catastrophic Web3 losses are key-management failures, not protocol-level cryptography breaks.",
        prerequisites=[
            "Blockchain transaction flow basics",
            "Basic understanding of hashing",
            "Awareness of phishing/social engineering risks",
        ],
        outcomes=[
            "Explain keypair generation and signature verification flow.",
            "Differentiate wallet UX from cryptographic ownership.",
            "Handle seed phrase and private key risk with practical controls.",
            "Design secure signing flow for user-facing applications.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[Seed Phrase] --> B[Derivation Path]
  B --> C[Private Key]
  C --> D[Public Key]
  D --> E[Address]
  C --> F[Sign Message]
  F --> G[Verify with Public Key]
""",
        systems_mermaid="""
sequenceDiagram
  participant U as User
  participant W as Wallet
  participant A as App
  participant N as Network
  U->>A: Initiate transaction
  A->>W: Request signature
  W->>U: Confirm details
  U->>W: Approve
  W->>A: Signed transaction
  A->>N: Broadcast
""",
        skyline_ascii="""
Security posture climbs with: hardware wallet + offline backup + strict verification
falls with: seed phrase screenshots + blind signing + reused devices
""",
        concepts=[
            Concept(
                name="Private/Public Key Pair",
                what="Private key signs; public key verifies.",
                intuition="Private key is a master stamp; public key is the verification template.",
                why="Core authorization primitive for blockchain ownership.",
                formula="signature = Sign(private_key, message)",
                pitfall="Sharing private key for support troubleshooting.",
                next_step="Use signing-only device separation for high-value wallets.",
            ),
            Concept(
                name="Seed Phrase",
                what="Human-readable backup encoding entropy for deterministic key derivation.",
                intuition="Master recovery root from which all wallet keys can regrow.",
                why="Loss means permanent fund loss; theft means full compromise.",
                pitfall="Storing seed in cloud notes or chat screenshots.",
                next_step="Create offline redundant backups in separate physical locations.",
            ),
            Concept(
                name="Signing Flow Hygiene",
                what="Users must verify recipient, amount, and program intent before signing.",
                intuition="Never sign a blank cheque, even if bank app looks familiar.",
                why="Malicious dApps exploit blind-signing behavior.",
                pitfall="Approving transactions with opaque payloads.",
                next_step="Add transaction decoding and simulation UI in wallet workflow.",
            ),
        ],
        math_intuition=[
            (
                "Verification Predicate",
                "Verify(pub, msg, sig) = true",
                "Valid signature proves holder of corresponding private key approved `msg`.",
            ),
            (
                "Address Derivation (conceptual)",
                "address = Encode(Hash(public_key))",
                "Address is a transformed representation of public key, not the private key itself.",
            ),
        ],
        examples=[
            CodeExample(
                title="Sign + Verify Message (Conceptual Python)",
                language="python",
                purpose="Demonstrates asymmetric signature workflow at high level.",
                code="""
from nacl.signing import SigningKey

sk = SigningKey.generate()
pk = sk.verify_key

message = b"pay 2 tokens to alice"
signed = sk.sign(message)

pk.verify(signed)  # raises if invalid
print('signature valid')
""",
                explain=[
                    "Only private key holder can produce valid signature.",
                    "Public key verification allows trust without revealing private key.",
                    "Message integrity is tied to signature payload.",
                ],
            ),
            CodeExample(
                title="Wallet Security Checklist",
                language="text",
                purpose="Translates theory into operational policy.",
                code="""
- Use hardware wallet for high-value accounts
- Never type seed phrase into websites
- Verify domain and transaction payload before sign
- Separate hot wallet (daily use) from vault wallet (savings)
- Enable passphrase if wallet supports it
""",
                explain=[
                    "Segmentation limits blast radius of compromise.",
                    "Human verification reduces phishing and approval attacks.",
                    "Operational discipline is as important as cryptography.",
                ],
            ),
        ],
        advanced_scenario=(
            "A DAO treasury signer receives an urgent multisig request from a spoofed admin account. Build a signing protocol with independent out-of-band verification, transaction simulation, and mandatory cooldown for large transfers."
        ),
        hots=[
            "Why can perfect cryptography still fail in real wallet operations?",
            "How would you design secure onboarding for non-technical wallet users?",
            "Which transaction metadata should a wallet always decode before signing?",
            "How do you balance convenience vs security for power users?",
        ],
        faqs=[
            (
                "Can I change my private key if leaked?",
                "You cannot rotate the same key; move assets to a new wallet generated from fresh entropy.",
            ),
            (
                "Is seed phrase same as private key?",
                "Not exactly. Seed phrase is root material used to derive one or many private keys.",
            ),
        ],
        practice_plan=[
            ("Today", "Set up hot-vs-cold wallet policy and document transfer rules."),
            ("This week", "Practice decoding and verifying signed transaction payloads."),
            ("Next week", "Run tabletop phishing simulation for wallet approval flow."),
        ],
        next_improvements=[
            "Integrate transaction simulation before sign in app UX.",
            "Adopt allowlist and spending limits for operational wallets.",
            "Formalize key rotation and incident response playbook.",
        ],
        related_notes=[
            "[[Web3 - Introduction to Blockchains]]",
            "[[Week 4 - Web3 - Token Program]]",
        ],
    )


def _cfg_web3_token_program() -> GuideConfig:
    return GuideConfig(
        title="Week 4 Web3 - Token Program (Bootcamp 1.0) - Master Study Guide",
        domain="Web3",
        tags=["study-guide", "bootcamp", "web3", "solana", "token-program"],
        session_focus="Token program mechanics on Solana-style account model: mint, token accounts, authority, transfers, and safety patterns.",
        why_this_session_matters="Token applications fail when teams misunderstand account model invariants and authority boundaries.",
        prerequisites=[
            "Wallet and signature basics",
            "Blockchain transaction model",
            "Basic JavaScript/TypeScript for Solana SDK",
        ],
        outcomes=[
            "Explain mint, token account, and associated token account roles.",
            "Trace token transfer flow including authority verification.",
            "Implement mint + transfer pipeline with proper checks.",
            "Identify common token-program security mistakes.",
        ],
        roadmap_mermaid="""
flowchart LR
  A[Mint Account] --> B[Mint Authority]
  A --> C[Token Accounts]
  C --> D[Owner Wallets]
  B --> E[Mint To]
  D --> F[Transfer]
  F --> G[Balance Updates]
""",
        systems_mermaid="""
sequenceDiagram
  participant Dev
  participant Mint
  participant ATA1 as Sender ATA
  participant ATA2 as Receiver ATA
  Dev->>Mint: createMint()
  Dev->>ATA1: createAssociatedTokenAccount()
  Dev->>Mint: mintTo(ATA1)
  ATA1->>ATA2: transfer(amount)
""",
        skyline_ascii="""
Token Integrity = correct mint authority + account ownership checks + supply invariants
""",
        concepts=[
            Concept(
                name="Mint vs Token Account",
                what="Mint defines token metadata/supply rules; token account stores a holder's balance for that mint.",
                intuition="Mint is the currency definition; token account is a wallet pocket for that currency.",
                why="Confusing these causes invalid program assumptions and transfer bugs.",
                formula="total_supply = sum(all token account balances for mint)",
                pitfall="Assuming one wallet address directly stores balances for all tokens.",
                next_step="Inspect on-chain account data for one token end-to-end.",
            ),
            Concept(
                name="Authority Design",
                what="Mint authority and freeze authority control privileged token operations.",
                intuition="Admin keys are root permissions; misuse can compromise trust instantly.",
                why="Security and governance depend on explicit authority policy.",
                pitfall="Leaving powerful authority keys in hot wallets indefinitely.",
                next_step="Move sensitive authorities to multisig or time-locked governance.",
            ),
            Concept(
                name="Transfer Constraints",
                what="Transfers require correct owner signer and account-program consistency checks.",
                intuition="Bank transfer must prove both account ownership and sufficient balance.",
                why="Prevents unauthorized spends and broken accounting.",
                pitfall="Failing to verify mint match between source and destination token accounts.",
                next_step="Add assertion tests for mint mismatch and authority mismatch paths.",
            ),
        ],
        math_intuition=[
            (
                "Supply Conservation",
                "sum(balances_before) = sum(balances_after) for transfer",
                "Transfers move value; they should not create or destroy supply.",
            ),
            (
                "Decimal Conversion",
                "human_amount = raw_amount / (10^decimals)",
                "Display precision is separate from raw integer accounting.",
            ),
        ],
        examples=[
            CodeExample(
                title="Create Mint + Mint Tokens (Solana JS)",
                language="ts",
                purpose="Shows canonical setup flow for token issuance.",
                code="""
import {
  createMint,
  getOrCreateAssociatedTokenAccount,
  mintTo,
} from '@solana/spl-token';

const mint = await createMint(connection, payer, mintAuthority.publicKey, null, 6);
const ata = await getOrCreateAssociatedTokenAccount(connection, payer, mint, owner.publicKey);
await mintTo(connection, payer, mint, ata.address, mintAuthority, 1_000_000n); // 1 token if decimals=6
""",
                explain=[
                    "`createMint` defines token and decimal precision.",
                    "Associated token account stores owner balance for that mint.",
                    "`mintTo` increases supply under mint authority.",
                ],
            ),
            CodeExample(
                title="Transfer Tokens Safely",
                language="ts",
                purpose="Illustrates standard transfer path with ownership checks.",
                code="""
import { transferChecked } from '@solana/spl-token';

await transferChecked(
  connection,
  payer,
  fromTokenAccount,
  mint,
  toTokenAccount,
  owner,
  500_000n,
  6,
);
""",
                explain=[
                    "`transferChecked` validates mint + decimals assumptions.",
                    "Owner signer proves authorization to spend source account.",
                    "Prefer checked APIs to reduce silent precision errors.",
                ],
            ),
        ],
        advanced_scenario=(
            "You are launching loyalty points as a token for a consumer app. Design authority governance, freeze policy, and mint schedule before writing UI. Most incidents come from authority misconfiguration, not transfer logic."
        ),
        hots=[
            "Why should mint authority strategy be decided before token launch announcement?",
            "How do decimal mistakes create financial reconciliation bugs?",
            "What invariants must hold after every transfer transaction?",
            "When should token operations be gated behind multisig approval?",
        ],
        faqs=[
            (
                "Can one wallet hold many tokens with one account?",
                "On Solana, each mint typically has its own token account per owner (often via ATA).",
            ),
            (
                "Why use transferChecked instead of transfer?",
                "It enforces mint/decimal correctness, reducing unit mismatch errors.",
            ),
        ],
        practice_plan=[
            ("Today", "Create a local mint and transfer token between two wallets."),
            ("This week", "Write tests for authority mismatch, mint mismatch, and insufficient balance."),
            ("Next week", "Add governance policy document for mint/freeze authority control."),
        ],
        next_improvements=[
            "Adopt multisig governance for sensitive authorities.",
            "Implement on-chain event indexing for auditability.",
            "Add integration tests for decimals and rounding behavior in UI/API.",
        ],
        related_notes=[
            "[[Web3 - Introduction to Blockchains]]",
            "[[Week 3 - Web3 - Wallets and Private Keys]]",
        ],
    )


def _resolve_config(folder_name: str) -> GuideConfig | None:
    matchers: list[tuple[Callable[[str], bool], Callable[[], GuideConfig]]] = [
        (lambda n: "Fast-tracking the AI course" in n, _cfg_ai_fasttrack),
        (lambda n: "Neural Networks from Scratch" in n, _cfg_ai_nn_scratch),
        (lambda n: "Transformers_ Part 1" in n, _cfg_ai_transformers_p1),
        (lambda n: "Transformers_ Part 2" in n, _cfg_ai_transformers_p2),
        (lambda n: "Promises, Callbacks, CPU vs IO Tasks" in n, _cfg_webdev_async_foundations),
        (lambda n: "Web Development _ Promises _" in n, _cfg_webdev_promises_deep),
        (lambda n: "Introduction to Blockchains" in n, _cfg_web3_intro),
        (lambda n: "Wallets and Private Keys" in n, _cfg_web3_wallets),
        (lambda n: "Token Program" in n, _cfg_web3_token_program),
    ]
    for predicate, builder in matchers:
        if predicate(folder_name):
            return builder()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Enhance final_notes.md into comprehensive study guides.")
    parser.add_argument(
        "--root",
        default=".",
        help="Root folder containing lecture session directories.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned rewrites without modifying files.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rewritten = 0
    skipped: list[str] = []

    for final_note in sorted(root.glob("*/final_notes.md")):
        folder = final_note.parent
        cfg = _resolve_config(folder.name)
        if cfg is None:
            skipped.append(folder.name)
            continue

        topic_index = _extract_topics(folder / ".pipeline" / "topic_inventory.json")
        content = _render(cfg, topic_index, folder.name)

        if args.dry_run:
            print(f"[DRY-RUN] would rewrite: {final_note}")
        else:
            final_note.write_text(content)
            print(f"rewrote: {final_note}")
        rewritten += 1

    print(f"done. rewritten={rewritten} skipped={len(skipped)}")
    if skipped:
        print("skipped sessions:")
        for name in skipped:
            print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
