#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


ROOT = Path('/Users/praxlannister/Documents/Zoom')


@dataclass
class NotebookSpec:
    key: str
    file_path: Path
    resources_md: str
    colab_id: str | None = None
    colab_url: str | None = None


SPECS: list[NotebookSpec] = [
    NotebookSpec(
        key='week1_fasttrack',
        file_path=ROOT / '2026-01-17 22.40.53 Fast-tracking the AI course _ AI&ML Bootcamp 1.0/final_notes.md',
        resources_md=(
            "## 🔗 Official Class Resources\n"
            "- **Week 0 - AI and ML Orientation | 09/01/2026**\n"
            "  - Slides: https://drive.google.com/file/d/1vYuRDxfmKeDN8hVMpQ-1mVB8A8rgAdyc/view?usp=drive_link\n"
            "- **Week 1 - Fast-tracking the course of AI | 18/01/2026**\n"
            "  - Slides: https://drive.google.com/file/d/1B8Dltp-P_-ZFuf_On_FcwJFLYVTyNN5T/view?usp=sharing\n"
            "  - LLM visualization: https://bbycroft.net/llm\n"
            "  - Jailbreaking AI: https://github.com/elder-plinius/L1B3RT4S\n"
            "\n"
            "> [!note] Colab Status\n"
            "> No official Colab notebook link was provided for this Fast-tracking session.\n"
        ),
    ),
    NotebookSpec(
        key='week2_nn',
        file_path=ROOT / '2026-01-24 22.46.12 Week 3_ AI and ML _ Neural Networks from Scratch _ Bootcamp 1.0/final_notes.md',
        resources_md=(
            "## 🔗 Official Class Resources\n"
            "- **Week 2 - AI and ML | Neural Networks from Scratch | 24/01/2026**\n"
            "  - Slides: https://drive.google.com/file/d/1wDBIvKpq69d37ki_aoOuiy1grpuWNicR/view?usp=sharing\n"
            "  - Colab: https://colab.research.google.com/drive/1OuJA1KC2IUexv0TXGkkQTTl1B-kJKV-P?usp=sharing\n"
        ),
        colab_id='1OuJA1KC2IUexv0TXGkkQTTl1B-kJKV-P',
        colab_url='https://colab.research.google.com/drive/1OuJA1KC2IUexv0TXGkkQTTl1B-kJKV-P?usp=sharing',
    ),
    NotebookSpec(
        key='week3_transformers_p1',
        file_path=ROOT / '2026-01-31 21.24.17 Week 3 - AI&ML _ Transformers_ Part 1 _ Bootcamp 1.0/final_notes.md',
        resources_md=(
            "## 🔗 Official Class Resources\n"
            "- **Week 3 - AI and ML | Transformers- Part 1 | 31/01/2026**\n"
            "  - Slides: https://drive.google.com/file/d/1TfTlTvVGw9WsXf9V0h_XpG51TYoKwO8F/view\n"
            "  - Colab: https://colab.research.google.com/drive/13KJpq-2zr3b8NcTiIpwBmHHuhMUWSk1T?usp=sharing\n"
        ),
        colab_id='13KJpq-2zr3b8NcTiIpwBmHHuhMUWSk1T',
        colab_url='https://colab.research.google.com/drive/13KJpq-2zr3b8NcTiIpwBmHHuhMUWSk1T?usp=sharing',
    ),
    NotebookSpec(
        key='week4_transformers_p2',
        file_path=ROOT / '2026-02-07 21.50.32 Week 4 - AI&ML _ Transformers_ Part 2 _ Bootcamp 1.0/final_notes.md',
        resources_md=(
            "## 🔗 Official Class Resources\n"
            "- **Week 4 - AI&ML | Transformers: Part 2 | 06/02/2026**\n"
            "  - Slides: https://drive.google.com/file/d/1opPJYcDjthlw9cnNyYh0Dcuyj09toPrQ/view?usp=drive_link\n"
            "  - Colab: https://colab.research.google.com/drive/1GI4cHskjgsmT1KupN5shNXa51ZcOyPWK?usp=sharing\n"
        ),
        colab_id='1GI4cHskjgsmT1KupN5shNXa51ZcOyPWK',
        colab_url='https://colab.research.google.com/drive/1GI4cHskjgsmT1KupN5shNXa51ZcOyPWK?usp=sharing',
    ),
    NotebookSpec(
        key='week5_tensors_pytorch',
        file_path=ROOT / '2026-02-14 22.36.52 Week 5 - AI&ML _ Introduction to Tensors and PyTorch _ Bootcamp 1.0/final_notes.md',
        resources_md=(
            "## 🔗 Official Class Resources\n"
            "- **Week 5 - AI&ML | Introduction to Tensors and PyTorch | 14/02/2026**\n"
            "  - Slides: https://drive.google.com/file/d/1kwR7-MmcYeNrI_M4zSkKyNl3108WWBPq/view?usi=drive_link\n"
            "  - Colab: https://colab.research.google.com/drive/1V5qEIwUu4fD6jfTR_x_L3BlEeJwAYvsT?usp=sharing\n"
            "  - YT video on tensors: https://youtu.be/f5liqUk0ZTw?si=AVkGGRRNO_rm3-Q0\n"
        ),
        colab_id='1V5qEIwUu4fD6jfTR_x_L3BlEeJwAYvsT',
        colab_url='https://colab.research.google.com/drive/1V5qEIwUu4fD6jfTR_x_L3BlEeJwAYvsT?usp=sharing',
    ),
]


IMPORT_GUIDE = {
    'numpy': (
        'Numerical tensor/vector operations used for manual ML math (dot products, matrix transforms, array broadcasting).',
        'NumPy is the calculator brain of the notebook. It lets us express neural/attention math directly.',
        'Most operations are vectorized; complexity depends on matrix size. Example: matrix multiply is roughly O(n*m*k).',
    ),
    'matplotlib.pyplot': (
        'Plotting curves and geometric intuition visuals (decision boundaries, embedding plots, learning curves).',
        'Think of it as the visual debugger for model behavior.',
        'Rendering overhead is usually secondary; plotting dense points is roughly O(num_points).',
    ),
    'torch': (
        'PyTorch tensor engine and autograd runtime for trainable neural models.',
        'If NumPy is a calculator, PyTorch is the calculator + gradient accountant.',
        'Kernel complexity follows tensor ops; autograd adds graph bookkeeping.',
    ),
    'torch.nn': (
        'Layer/module abstractions (`Linear`, `Module`) to define trainable architecture cleanly.',
        'This turns raw equations into reusable building blocks.',
        'Forward complexity equals underlying math; module overhead is negligible.',
    ),
    'torch.optim': (
        'Optimization utilities (e.g., SGD) to update parameters using gradients.',
        'Optimizer is the step-policy: how to move in the loss landscape.',
        'Per-step complexity scales with total parameter count O(P).',
    ),
    'tiktoken': (
        'Tokenizer used to convert text into model tokens (integer IDs).',
        'Tokenizer is the gateway from language to math.',
        'Encoding is roughly linear in input length O(L).',
    ),
    'sklearn.decomposition.PCA': (
        'Dimensionality reduction to visualize high-dimensional embeddings in 2D.',
        'PCA is like rotating/compressing space so humans can inspect patterns.',
        'Fit complexity depends on samples/features, often around O(min(n^2d, nd^2)).',
    ),
    'gensim.downloader': (
        'Loads pretrained embeddings (Word2Vec/GloVe style) for semantic similarity demos.',
        'Provides a ready-made semantic memory without training from scratch.',
        'Lookup is near O(1) per word after model load; initial load dominates runtime.',
    ),
    'matplotlib.patches.Patch': (
        'Legend/annotation helpers to make embedding visualizations readable.',
        'Labels matter for intuition. This improves visual storytelling.',
        'Negligible computational cost.',
    ),
}


FUNC_GUIDE = {
    'sigmoid': (
        'Applies non-linear squashing to map real numbers to (0, 1).',
        'Turns raw neuron scores into interpretable activation strength/probability-like output.',
        'Element-wise operation: O(n).',
    ),
    'sigmoid_derivative': (
        'Computes local slope used during backpropagation.',
        'This tells learning how sensitive output is to small input changes.',
        'Element-wise operation: O(n).',
    ),
    'forward': (
        'Runs a forward pass through layers to get predictions.',
        'This is the model’s current answer before correction.',
        'For dense layers roughly O(batch * (input_dim*hidden_dim + hidden_dim*out_dim)).',
    ),
    'compute_loss': (
        'Measures prediction error (objective to minimize).',
        'Loss is the training feedback signal, not just a number for logging.',
        'Typically O(batch * output_dim).',
    ),
    'backward': (
        'Computes gradients and propagates error backward.',
        'Backprop is blame assignment across parameters.',
        'Same order as forward for dense nets, with extra gradient ops.',
    ),
    'forward_small': (
        'Forward pass variant for reduced hidden-size experiments.',
        'Used to demonstrate capacity limits and underfitting behavior.',
        'Similar to forward, smaller hidden dimension reduces cost.',
    ),
    'backward_small': (
        'Backward pass variant for reduced hidden-size experiments.',
        'Lets us compare how lower capacity changes learning dynamics.',
        'Same structure as backward with fewer hidden neurons.',
    ),
    'get_positional_encoding': (
        'Generates sinusoidal positional vectors to inject order into token embeddings.',
        'Without position, attention sees tokens as a set; this restores sequence awareness.',
        'Building table is roughly O(max_len * d_model).',
    ),
    'softmax': (
        'Converts raw scores to normalized attention weights.',
        'Softmax turns similarity into relative importance distribution.',
        'Per row complexity O(n).',
    ),
    'self_attention': (
        'Computes Q/K/V attention pipeline and contextual token outputs.',
        'Each token asks which other tokens matter and by how much.',
        'Core cost dominated by QK^T and weight-value multiply: O(seq_len^2 * d).',
    ),
}


PARTS_GUIDE = {
    'week2_nn': [
        ('Part 1: XOR setup and visualization', 'Maps the non-linear XOR problem; connects to why linear models fail.'),
        ('Part 2: Parameter initialization and network architecture', 'Introduces trainable weights/biases and model capacity decisions.'),
        ('Part 3: Activation + forward pass', 'Shows how raw inputs become predictions through non-linear transforms.'),
        ('Part 4: Loss + backpropagation + training loop', 'Connects error feedback to iterative parameter updates.'),
        ('Part 5: Failure experiments', 'Demonstrates low learning-rate and low-capacity failure modes explicitly.'),
        ('Part 6: PyTorch rewrite', 'Bridges from from-scratch intuition to production-grade deep-learning tooling.'),
    ],
    'week3_transformers_p1': [
        ('Part 1: Tokenization', 'Shows why text segmentation quality controls model efficiency and behavior.'),
        ('Part 2: Embeddings', 'Maps token IDs to dense semantic vectors and explores similarity structure.'),
        ('Part 3: Positional encoding', 'Adds order information so attention can distinguish sequence structure.'),
    ],
    'week4_transformers_p2': [
        ('Part 1: Tokenization recap', 'Reinforces token granularity impact on downstream attention.'),
        ('Part 2: Embeddings recap', 'Strengthens semantic-space intuition before attention mechanics.'),
        ('Part 3: Positional encoding recap', 'Re-establishes order injection before full self-attention.'),
        ('Part 4: Self-attention implementation', 'Implements Q/K/V, score matrix, normalization, and contextual aggregation.'),
        ('Part 5: End-to-end pipeline summary', 'Connects tokenizer -> embeddings -> position -> attention into one mental model.'),
    ],
    'week5_tensors_pytorch': [
        ('Part 1: Tensor fundamentals', 'Builds scalar/vector/matrix/tensor intuition and shape literacy.'),
        ('Part 2: PyTorch tensor creation', 'Demonstrates constructors (`tensor`, `zeros`, `ones`, `randn`, `arange`, `linspace`).'),
        ('Part 3: Shape operations', 'Explains `view`, `permute`, and how axis order changes semantics.'),
        ('Part 4: Device and performance', 'Compares CPU/GPU execution paths and practical speed intuition.'),
        ('Part 5: Autograd and training loop mechanics', 'Covers `requires_grad`, `backward`, gradient accumulation, and `zero_grad` discipline.'),
    ],
}


def _download_notebook(file_id: str) -> dict:
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return json.loads(response.text)


def _extract_code_cells(nb: dict) -> list[str]:
    cells = []
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        source = ''.join(cell.get('source', []))
        cells.append(source.rstrip())
    return cells


def _combined_code(cells: list[str]) -> str:
    blocks: list[str] = []
    for i, code in enumerate(cells, start=1):
        blocks.append(f'# ===== Colab Code Cell {i} =====\n{code}')
    return '\n\n'.join(blocks).rstrip() + '\n'


def _filter_for_ast(code: str) -> str:
    lines = []
    for ln in code.splitlines():
        if ln.lstrip().startswith('!'):
            continue
        if ln.lstrip().startswith('%'):
            continue
        lines.append(ln)
    return '\n'.join(lines)


def _extract_imports_and_functions(code: str) -> tuple[list[str], list[tuple[str, str]]]:
    filtered = _filter_for_ast(code)
    tree = ast.parse(filtered)

    imports = []
    seen_imports = set()
    functions = []

    class ParentAnnotator(ast.NodeVisitor):
        def generic_visit(self, node):
            for child in ast.iter_child_nodes(node):
                child.parent = node
                self.visit(child)

    ParentAnnotator().visit(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name not in seen_imports:
                    seen_imports.add(name)
                    imports.append(name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ''
            for alias in node.names:
                name = f'{mod}.{alias.name}' if mod else alias.name
                if name not in seen_imports:
                    seen_imports.add(name)
                    imports.append(name)

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        parent = getattr(node, 'parent', None)
        if isinstance(parent, ast.ClassDef):
            display = f'{parent.name}.{node.name}'
        else:
            display = node.name

        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        sig = f"{display}({', '.join(args)})"
        functions.append((display, sig))

    # Preserve first appearance order
    ordered_funcs = []
    seen = set()
    for item in functions:
        if item[0] in seen:
            continue
        seen.add(item[0])
        ordered_funcs.append(item)

    return imports, ordered_funcs


def _render_import_table(imports: list[str]) -> str:
    rows = [
        '| Import | What it does in this notebook | Intuition | Complexity impact |',
        '|---|---|---|---|',
    ]
    for imp in imports:
        key = imp
        if key not in IMPORT_GUIDE:
            # try collapsing dot-path for fallback
            if imp.startswith('numpy'):
                key = 'numpy'
            elif imp.startswith('matplotlib.pyplot'):
                key = 'matplotlib.pyplot'
            elif imp.startswith('torch.nn'):
                key = 'torch.nn'
            elif imp.startswith('torch.optim'):
                key = 'torch.optim'
            elif imp.startswith('torch'):
                key = 'torch'
            elif imp.startswith('tiktoken'):
                key = 'tiktoken'
            elif imp.startswith('sklearn.decomposition.PCA'):
                key = 'sklearn.decomposition.PCA'
            elif imp.startswith('gensim.downloader'):
                key = 'gensim.downloader'
            elif imp.startswith('matplotlib.patches.Patch'):
                key = 'matplotlib.patches.Patch'

        desc = IMPORT_GUIDE.get(key, (
            'Used in notebook execution.',
            'Supports one part of the pipeline implementation.',
            'Complexity depends on call-site usage.',
        ))
        rows.append(f'| `{imp}` | {desc[0]} | {desc[1]} | {desc[2]} |')
    return '\n'.join(rows)


def _render_functions(functions: list[tuple[str, str]], topic_context: str) -> str:
    chunks: list[str] = []
    for name, sig in functions:
        guide_key = name.split('.')[-1] if name not in FUNC_GUIDE else name
        desc = FUNC_GUIDE.get(guide_key, (
            'Implements a notebook-specific computation step.',
            'This function operationalizes one concept from the lecture pipeline.',
            'Complexity depends on tensor/array sizes and internal loops.',
        ))

        chunks.append(
            '\n'.join([
                f'### `{sig}`',
                f'- **Purpose:** {desc[0]}',
                f'- **Intuition:** {desc[1]}',
                f'- **How it connects to lecture topic:** {topic_context}',
                f'- **Complexity intuition:** {desc[2]}',
            ])
        )
    return '\n\n'.join(chunks)


def _render_parts(parts: Iterable[tuple[str, str]]) -> str:
    lines = []
    for idx, (title, explanation) in enumerate(parts, start=1):
        lines.append(f'{idx}. **{title}**')
        lines.append(f'   - {explanation}')
    return '\n'.join(lines)


def _first_nonempty_line(code: str) -> str:
    for ln in code.splitlines():
        clean = ln.strip()
        if clean:
            return clean
    return '(empty cell)'


def _cell_topic_context(spec_key: str) -> str:
    return {
        'week2_nn': 'Supports neural-network-from-scratch learning: XOR non-linearity, forward pass, loss, and backpropagation.',
        'week3_transformers_p1': 'Supports transformer foundations: tokenization, embeddings, and positional encoding.',
        'week4_transformers_p2': 'Supports advanced transformer flow: positional awareness and self-attention mechanics.',
        'week5_tensors_pytorch': 'Supports tensor/PyTorch foundations: shape reasoning, tensor ops, and autograd mechanics.',
    }.get(spec_key, 'Supports lecture implementation and experimentation workflow.')


def _classify_cell(code: str, spec_key: str) -> tuple[str, str, str, str, str]:
    text = code.strip()
    lower = text.lower()

    if not text:
        return (
            'Notebook spacer / reset cell',
            'Acts as a visual separator so the learner can pause between conceptual phases.',
            'A clean break prevents cognitive overload when transitioning from one idea to the next.',
            'No computational complexity.',
            'Use this pause to summarize what changed in model behavior before moving ahead.',
        )

    if lower.startswith('!pip install') or '\n!pip install' in lower:
        return (
            'Environment setup cell',
            'Installs dependencies required for the notebook to run consistently.',
            'Think of this as preparing lab equipment before an experiment.',
            'One-time setup cost; runtime depends on package download/install time.',
            'Pin package versions to improve reproducibility across reruns.',
        )

    effective_lines = [
        ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith('#')
    ]
    import_only = bool(effective_lines) and all(
        ln.startswith('import ') or ln.startswith('from ')
        for ln in effective_lines
    )

    if import_only:
        return (
            'Dependency import and runtime initialization',
            'Loads libraries and initializes base runtime objects.',
            'Imports define the toolbox; everything later depends on this setup.',
            'Negligible algorithmic cost; mainly module load overhead.',
            'Remove duplicate imports and keep only libraries used in later cells.',
        )

    if 'def ' in text or 'class ' in text:
        return (
            'Reusable logic definition cell',
            'Defines core functions/classes that encode the algorithmic heart of the tutorial.',
            'Instead of repeating equations manually, we package behavior into reusable units.',
            'Definition phase itself is cheap; complexity appears when these functions are invoked.',
            'Add mini unit checks (shape/value assertions) right after definitions.',
        )

    if 'plt.' in text or 'matplotlib' in lower:
        return (
            'Visualization / intuition-building cell',
            'Plots model behavior or data geometry for visual reasoning.',
            'Plots are the fastest way to catch conceptual misunderstandings early.',
            'Mostly O(number_of_points) for plotting; dominated by rendered sample size.',
            'Vary colors/scales and annotate key regions to sharpen intuition.',
        )

    if 'embedding' in lower and ('np.random' in lower or 'api.load' in lower or 'most_similar' in lower):
        return (
            'Embedding construction / semantic-space analysis',
            'Builds or loads vector representations to show semantic structure.',
            'Embeddings map symbolic tokens into geometric neighborhoods.',
            'Lookup is near O(1) per token; similarity search depends on vocabulary size.',
            'Compare nearest neighbors before/after changing context or model source.',
        )

    if 'pca(' in lower or 'fit_transform' in lower:
        return (
            'Embedding space projection / visualization',
            'Projects high-dimensional vectors to 2D for human-interpretable structure inspection.',
            'Projection helps you see clustering and semantic neighborhoods directly.',
            'PCA fitting cost grows with sample and dimension sizes.',
            'Try changing sampled words/classes and compare cluster separation.',
        )

    if 'positional' in lower or 'sin(' in lower or 'cos(' in lower:
        return (
            'Positional encoding cell',
            'Injects sequence-order information into token representations.',
            'Without position, attention sees a bag of tokens, not an ordered sequence.',
            'Building positional tables is roughly O(max_len * d_model).',
            'Change sequence length/dimension and observe encoding periodicity shifts.',
        )

    if 'tokenizer.encode' in lower or 'tiktoken' in lower:
        return (
            'Tokenization behavior exploration',
            'Converts text to token IDs and inspects segmentation patterns.',
            'This is where language becomes model-consumable integers.',
            'Typically O(input_length) per encode operation.',
            'Try difficult strings (code, emojis, multilingual text) and compare token counts.',
        )

    if 'self_attention' in lower or ('q =' in lower and 'k =' in lower and 'v =' in lower):
        return (
            'Self-attention mechanics cell',
            'Computes attention scores/weights and contextualized outputs.',
            'Each token asks: who should I listen to, and how much?',
            'Dominant cost is O(seq_len^2 * d) from score matrix operations.',
            'Add masking and compare outputs to validate causal constraints.',
        )

    if ('for ' in text and 'range' in text and ('epoch' in lower or 'step' in lower or 'iter' in lower)) or 'loss' in lower:
        return (
            'Training loop / optimization dynamics cell',
            'Runs repeated prediction-error-update cycles.',
            'Learning emerges from many small corrective updates, not one perfect step.',
            'Often O(epochs * batch_size * model_compute).',
            'Sweep learning rate and plot loss trajectories to diagnose stability.',
        )

    if 'print(' in text:
        return (
            'Diagnostic output cell',
            'Prints intermediate values for sanity checks and interpretation.',
            'Diagnostics are checkpoints that keep mental model aligned with execution.',
            'Usually negligible; string formatting/output bound.',
            'Convert repeated prints into structured logging tables for cleaner debugging.',
        )

    return (
        'Computation / experiment cell',
        'Executes a concrete experiment step in the notebook pipeline.',
        'Each cell advances one hypothesis about model behavior.',
        'Complexity depends on tensor sizes and loop structure in this cell.',
        'Perturb one parameter in this cell and explain how outputs shift.',
    )


def _render_cell_by_cell(cells: list[str], spec_key: str) -> str:
    lines = [
        '## 🧬 Appendix C - Cell-by-Cell Deep Commentary',
        '',
        '> [!important] Why this section exists',
        '> This is the execution-level breakdown: every code cell is explained in terms of purpose, intuition, complexity,',
        '> and how it connects back to what was taught in the lecture.',
        '',
    ]

    topic_context = _cell_topic_context(spec_key)

    for idx, code in enumerate(cells, start=1):
        signature = _first_nonempty_line(code).replace('`', '\\`')
        if len(signature) > 120:
            signature = signature[:117] + '...'
        line_count = len(code.splitlines()) if code else 0
        focus, why, intuition, complexity, tweak = _classify_cell(code, spec_key)

        lines.extend(
            [
                f'### Cell {idx} ({line_count} lines)',
                f'- **Cell signature:** `{signature}`',
                f'- **Primary role:** {focus}',
                f'- **Why this cell exists:** {why}',
                f'- **Intuition:** {intuition}',
                f'- **Connection to tutorial topics:** {topic_context}',
                f'- **Complexity intuition:** {complexity}',
                f'- **Try-this improvement:** {tweak}',
                '',
            ]
        )

    return '\n'.join(lines).rstrip() + '\n'


def _render_line_by_line(cells: list[str]) -> str:
    lines = [
        '## 🧯 Appendix D - Line-by-Line Reading Guide',
        '',
        '> [!warning] How to use this section',
        '> This section explains each executable line pattern so learners do not need to assume hidden prerequisite knowledge.',
        '> It is intentionally verbose: read alongside the original code cells.',
        '',
    ]

    for idx, cell in enumerate(cells, start=1):
        cell_lines = [ln for ln in cell.splitlines()]
        if not cell_lines:
            continue
        lines.append(f'### Cell {idx} - Line Walkthrough')
        for ln_idx, raw in enumerate(cell_lines, start=1):
            stripped = raw.strip()
            if not stripped:
                continue

            if stripped.startswith('#'):
                note = 'Comment line: describes intent/context. Keep it concise and aligned with nearby code behavior.'
            elif stripped.startswith('import ') or stripped.startswith('from '):
                note = (
                    'Import line: pulls a library/module into runtime namespace. '
                    'This defines what APIs are available to subsequent lines.'
                )
            elif stripped.startswith('def '):
                note = (
                    'Function definition: declares reusable logic with explicit input arguments and implicit output expectations.'
                )
            elif stripped.startswith('class '):
                note = (
                    'Class definition: bundles state + behavior. In notebooks this often structures model components.'
                )
            elif '.backward(' in stripped or stripped.startswith('loss.backward'):
                note = (
                    'Backward pass trigger: computes gradients by traversing the autograd graph in reverse.'
                )
            elif 'zero_grad' in stripped:
                note = (
                    'Gradient reset: prevents unintended gradient accumulation across optimization steps.'
                )
            elif '.step(' in stripped:
                note = (
                    'Optimizer step: updates parameters using gradients and optimizer policy.'
                )
            elif 'torch.' in stripped:
                note = (
                    'PyTorch operation: manipulates tensors, shape, dtype, device, or computation graph state.'
                )
            elif 'np.' in stripped:
                note = (
                    'NumPy operation: vectorized array math. Semantics usually mirror linear algebra operations.'
                )
            elif stripped.startswith('for ') or stripped.startswith('while '):
                note = (
                    'Iteration control: repeats computation. Runtime grows with loop bounds and nested operations.'
                )
            elif stripped.startswith('if ') or stripped.startswith('elif ') or stripped.startswith('else'):
                note = (
                    'Branch logic: controls execution path based on condition checks.'
                )
            elif 'print(' in stripped:
                note = (
                    'Diagnostic output: inspect values/shapes to verify assumptions and catch silent bugs early.'
                )
            elif '=' in stripped:
                note = (
                    'Assignment/evaluation line: computes RHS expression and binds result to variable name.'
                )
            else:
                note = (
                    'Execution statement: contributes to data flow/state update. Read with previous and next lines for full meaning.'
                )

            display = raw.replace('`', '\\`')
            if len(display) > 160:
                display = display[:157] + '...'
            lines.append(f'- **L{ln_idx}:** `{display}`')
            lines.append(f'  - {note}')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def _build_appendix(
    spec: NotebookSpec,
    code: str,
    code_cells: list[str],
    imports: list[str],
    functions: list[tuple[str, str]],
) -> str:
    topic_context = {
        'week2_nn': 'Directly supports neural-network fundamentals: forward pass, backprop, optimization stability.',
        'week3_transformers_p1': 'Directly supports Part 1 concepts: tokenization, embeddings, positional encoding.',
        'week4_transformers_p2': 'Directly supports Part 2 concepts: attention mechanics, masking, and transformer pipeline thinking.',
        'week5_tensors_pytorch': 'Directly supports Part 5 concepts: tensor abstractions, PyTorch ops, and autograd behavior.',
    }.get(spec.key, 'Directly supports session concepts and practical implementation.')

    parts = PARTS_GUIDE.get(spec.key, [])

    return (
        '## 🧪 Appendix A - Colab Notebook (Full Code Dump)\n'
        f'> [!info] Source Notebook\n'
        f'> {spec.colab_url}\n'
        '> Full code copied into this note for offline reference and deep study.\n\n'
        '```python\n'
        f'{code}'
        '```\n\n'
        '## 🧩 Appendix B - Code Decomposition (Import-by-Import, Function-by-Function)\n\n'
        '### B.1 Import Map\n'
        f'{_render_import_table(imports)}\n\n'
        '### B.2 Function and Class Method Breakdown\n'
        f'{_render_functions(functions, topic_context)}\n\n'
        '### B.3 Part-by-Part Notebook Flow (and why each part exists)\n'
        f'{_render_parts(parts)}\n\n'
        f'{_render_cell_by_cell(code_cells, spec.key)}\n\n'
        f'{_render_line_by_line(code_cells)}\n\n'
        '> [!tip] How to study this appendix\n'
        '> 1) Run each part in order.\n'
        '> 2) Predict output before execution.\n'
        '> 3) Modify one hyperparameter/value and explain behavior shift.\n'
        '> 4) Connect each behavior back to the concept section above.\n'
    )


def _upsert_resources(text: str, resources_md: str) -> str:
    if '## 🔗 Official Class Resources' in text:
        text = re.sub(
            r'\n## 🔗 Official Class Resources[\s\S]*?(?=\n## )',
            '\n',
            text,
            count=1,
        )

    markers = [
        '## 🗺️ Conceptual Roadmap',
        '## 🗺️ Big Picture Roadmap',
        '## 1️⃣ Core Intuition: What Is a Tensor?',
    ]
    for marker in markers:
        if marker in text:
            return text.replace(marker, f'{resources_md}\n\n{marker}', 1)
    return text.rstrip() + f'\n\n{resources_md}\n'


def _upsert_appendix(text: str, appendix_md: str) -> str:
    # Remove old appendix block if it already exists.
    text = re.sub(
        r'\n## 🧪 Appendix A - Colab Notebook \(Full Code Dump\)[\s\S]*?(?=\n---\n\n> \[!quote\] Final Reminder)',
        '\n',
        text,
        count=1,
    )

    marker = '\n---\n\n> [!quote] Final Reminder'
    if marker in text:
        return text.replace(marker, f'\n\n{appendix_md}{marker}', 1)

    return text.rstrip() + '\n\n' + appendix_md + '\n'


def _save_colab_artifacts(spec: NotebookSpec, notebook: dict, code_cells: list[str], code: str) -> list[Path]:
    session_dir = spec.file_path.parent
    out_dir = session_dir / '.pipeline' / 'colab'
    out_dir.mkdir(parents=True, exist_ok=True)

    notebook_path = out_dir / f'{spec.key}.ipynb'
    notebook_path.write_text(json.dumps(notebook, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')

    code_path = out_dir / f'{spec.key}_code_cells.py'
    code_path.write_text(code, encoding='utf-8')

    cell_manifest = {
        'key': spec.key,
        'colab_url': spec.colab_url,
        'code_cells': len(code_cells),
        'artifacts': {
            'notebook_ipynb': str(notebook_path),
            'code_cells_py': str(code_path),
        },
    }
    manifest_path = out_dir / f'{spec.key}_manifest.json'
    manifest_path.write_text(json.dumps(cell_manifest, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    return [notebook_path, code_path, manifest_path]


def _select_specs(keys: list[str] | None) -> list[NotebookSpec]:
    if not keys:
        return SPECS
    keyset = set(keys)
    selected = [s for s in SPECS if s.key in keyset]
    missing = sorted(keyset - {s.key for s in selected})
    if missing:
        raise ValueError(f'Unknown --only keys: {", ".join(missing)}')
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description='Update AI/ML notes with resources + Colab deep explainer appendices.')
    parser.add_argument(
        '--only',
        action='append',
        help='Run for specific notebook key(s). Repeatable. Example: --only week5_tensors_pytorch',
    )
    parser.add_argument('--dry-run', action='store_true', help='Do not write note files; only print planned work.')
    args = parser.parse_args()

    specs = _select_specs(args.only)
    for spec in specs:
        if not spec.file_path.exists():
            raise FileNotFoundError(f'Missing note: {spec.file_path}')

        text = spec.file_path.read_text()
        text = _upsert_resources(text, spec.resources_md)

        if spec.colab_id:
            nb = _download_notebook(spec.colab_id)
            code_cells = _extract_code_cells(nb)
            code = _combined_code(code_cells)
            imports, functions = _extract_imports_and_functions(code)
            appendix = _build_appendix(spec, code, code_cells, imports, functions)
            text = _upsert_appendix(text, appendix)
            artifacts = [] if args.dry_run else _save_colab_artifacts(spec, nb, code_cells, code)
        else:
            artifacts = []

        if args.dry_run:
            print(f'[dry-run] update: {spec.file_path}')
        else:
            spec.file_path.write_text(text)
            print(f'updated: {spec.file_path}')
        for p in artifacts:
            print(f'  artifact: {p}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
