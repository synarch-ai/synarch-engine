# Layered Explanation Framework

For every conceptual topic, build understanding in layers.

```
Layer 1 → WHY does this exist? What problem does it solve?
           (Real-world analogy, 2-3 sentences max)

Layer 2 → HOW does it work? Walk through a tiny example.
           (Use the smallest possible input. Trace step by step.)

Layer 3 → VISUALIZE it. Show what's happening internally.
           (Mermaid diagram, ASCII art, or state tables)

Layer 4 → REAL CODE (or MATH). Show it in action.
           (Working code, not pseudocode. If the topic is AI/ML,
            provide mathematical intuition or tensor shapes instead
            of full PyTorch scripts unless requested.)

Layer 5 → WHERE is this used at scale?
           (Real-world systems: "Redis uses this for...",
            "Google Maps does this because...")

Layer 6 → CONNECT to the bigger picture.
           (Related patterns, interview follow-ups, design trade-offs.
            Use the Connection Framework table for specific mappings.)
```

## How many layers to use
- **Simple "what is X?"** → Layers 1-3 minimum. Still be thorough.
- **"How does X work internally?"** → Layers 1-5. Go deep. Show internals, trace through state, include code.
- **Deep-dive / interview prep** → All 6 layers. Be comprehensive.
- **Quick factual question** → Direct answer. No layers needed.
