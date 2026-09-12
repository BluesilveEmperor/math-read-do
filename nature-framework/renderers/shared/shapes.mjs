// nature-framework / renderers / shared / shapes.mjs
// Canonical module-type → shape mapping. Shared by the renderer (draw) and the
// validator (text-fit checks need to know the effective text width of a shape).

export const SHAPE_DEFAULTS = {
  input: "parallelogram",
  output: "parallelogram",
  embedding: "rect",
  encoder: "rounded",
  decoder: "rounded",
  attention: "trapezoid",
  ffn: "rect",
  norm: "circle",
  activation: "circle",
  pooling: "trapezoid",
  residual: "circle",
  concat: "circle",
  custom: "rect",
  // operator-level types for high-granularity figures
  linear: "rect",
  matmul: "circle",
  scale: "circle",
  softmax_op: "circle",
  add: "circle",
  layernorm: "rect",
  gelu: "circle",
  scaled_dot_product_attention: "rounded",
  // research-framework / structure vocabulary
  problem: "parallelogram",
  content: "rect",
  goal: "parallelogram",
  outcome: "parallelogram",
  chapter: "rounded",
  // experiment vocabulary
  dataset: "parallelogram",
  preprocess: "rounded",
  train: "rounded",
  eval: "rounded",
  metric: "circle",
  baseline: "rect",
  ablation: "rect",
  // system vocabulary
  client: "rounded",
  service: "rect",
  storage: "rounded",
};

// Font metrics mirrored by the renderer's CSS (.pf-mod-label etc.) and used by
// the validator's text-fit checks. Keep in sync with render-model.mjs.
export const TEXT_METRICS = {
  label: { font: 12, lineHeight: 15 },
  sub: { font: 10, lineHeight: 13 },
  tensor: { font: 9, lineHeight: 11 },
  connLabel: { font: 10, lineHeight: 12 },
  groupLabel: { font: 10, lineHeight: 12 },
};
