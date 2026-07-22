# LYR Explorer (planned — M5)

The interactive knowledge explorer. A TypeScript app built **on top of** the
Python knowledge engine's primitives — it is intentionally not part of v0.1.

Rather than only offering chat, the Explorer will expose an *explorable knowledge
space* over the engine's layers and provenance:

- **Timeline** — how knowledge formed over time
- **Subjects / Concepts** — entities and higher-level ideas
- **Knowledge Layers** — move between Source → Semantic → Durable → Cognitive
- **Evidence Graph** — expand any abstraction back to supporting records
- **Version History** — inspect how a node evolved (v1 → v2 → v3) and why

It will consume the engine through a thin read API over the same `Store` and
`provenance` primitives the Python package already exposes. Scaffolding lands
once the engine's layers (M3/M4) are further along.
