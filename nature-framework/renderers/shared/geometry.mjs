// nature-framework / renderers / shared / geometry.mjs
// Bounding boxes, overlap tests, path computation. Pure functions, no DOM.

export function bbox(pos, size) {
  return {
    x: pos[0],
    y: pos[1],
    w: size[0],
    h: size[1],
    x2: pos[0] + size[0],
    y2: pos[1] + size[1],
    cx: pos[0] + size[0] / 2,
    cy: pos[1] + size[1] / 2,
  };
}

export function bboxOfPoint(p, w, h) {
  return { x: p[0], y: p[1], w, h, x2: p[0] + w, y2: p[1] + h, cx: p[0] + w / 2, cy: p[1] + h / 2 };
}

export function bboxesOverlap(a, b, tol = 1) {
  // a and b overlap by more than tol in BOTH x and y
  const ox = Math.min(a.x2, b.x2) - Math.max(a.x, b.x);
  const oy = Math.min(a.y2, b.y2) - Math.max(a.y, b.y);
  return ox > tol && oy > tol;
}

export function bboxContains(outer, inner, tol = 0) {
  return (
    inner.x >= outer.x - tol &&
    inner.y >= outer.y - tol &&
    inner.x2 <= outer.x2 + tol &&
    inner.y2 <= outer.y2 + tol
  );
}

export function rectFromPoints(pts) {
  if (!pts.length) return null;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of pts) {
    if (p[0] < minX) minX = p[0];
    if (p[1] < minY) minY = p[1];
    if (p[0] > maxX) maxX = p[0];
    if (p[1] > maxY) maxY = p[1];
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY, x2: maxX, y2: maxY, cx: (minX + maxX) / 2, cy: (minY + maxY) / 2 };
}

// Segment-rect intersection (Liang-Barsky). Returns true if the open segment crosses the rect interior.
export function segmentIntersectsRect(p0, p1, r, tol = 0.5) {
  const [x0, y0] = p0;
  const [x1, y1] = p1;
  const dx = x1 - x0;
  const dy = y1 - y0;
  let t0 = 0, t1 = 1;
  const p = [-dx, dx, -dy, dy];
  const q = [x0 - r.x - tol, r.x2 - x0 + tol, y0 - r.y - tol, r.y2 - y0 + tol];
  for (let i = 0; i < 4; i++) {
    if (p[i] === 0) {
      if (q[i] < 0) return false; // parallel and outside
    } else {
      const t = q[i] / p[i];
      if (p[i] < 0) {
        if (t > t1) return false;
        if (t > t0) t0 = t;
      } else {
        if (t < t0) return false;
        if (t < t1) t1 = t;
      }
    }
  }
  return t0 < t1; // strict: only counts as crossing if there's a non-degenerate interval
}

// Distance from a point to a line segment.
export function pointToSegmentDist(p, a, b) {
  const ax = a[0], ay = a[1], bx = b[0], by = b[1], px = p[0], py = p[1];
  const dx = bx - ax, dy = by - ay;
  const len2 = dx * dx + dy * dy;
  if (len2 === 0) return Math.hypot(px - ax, py - ay);
  let t = ((px - ax) * dx + (py - ay) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  const cx = ax + t * dx, cy = ay + t * dy;
  return Math.hypot(px - cx, py - cy);
}

// Choose facing sides for a connection between two module bboxes.
export function chooseSides(fromB, toB) {
  const dx = toB.cx - fromB.cx;
  const dy = toB.cy - fromB.cy;
  if (Math.abs(dx) >= Math.abs(dy)) {
    return { fromSide: dx >= 0 ? "right" : "left", toSide: dx >= 0 ? "left" : "right" };
  }
  return { fromSide: dy >= 0 ? "bottom" : "top", toSide: dy >= 0 ? "top" : "bottom" };
}

export function sidePoint(b, side) {
  switch (side) {
    case "top": return [b.cx, b.y];
    case "bottom": return [b.cx, b.y2];
    case "left": return [b.x, b.cy];
    case "right": return [b.x2, b.cy];
    default: return [b.cx, b.cy];
  }
}

export function sideNormal(side) {
  switch (side) {
    case "top": return [0, -1];
    case "bottom": return [0, 1];
    case "left": return [-1, 0];
    case "right": return [1, 0];
    default: return [0, 0];
  }
}

// Resolve the from/to sides for a connection (explicit sides win, otherwise auto).
export function resolveSides(conn, fromB, toB) {
  let fromSide = conn.fromSide;
  let toSide = conn.toSide;
  if (!fromSide || !toSide) {
    const auto = chooseSides(fromB, toB);
    if (!fromSide) fromSide = auto.fromSide;
    if (!toSide) toSide = auto.toSide;
  }
  return { fromSide, toSide };
}

// Fan-in / fan-out endpoint spreading: when several connections share the same
// (module, side) attachment point, the arrowheads stack on one pixel and look
// broken. This computes one offset attachment point per connection so heads
// land side by side. Rules:
//   - group connections by (endpoint module, side);
//   - a group is spread only if it has >1 member AND none of them uses `via`
//     (via routes are hand-tuned — moving their endpoints would break the bend);
//   - spread span = 70% of the side's perpendicular length, ≥12px to bother;
//   - members are ordered by the opposite endpoint's center along the spread
//     axis, so lines never cross each other to reach their slots.
// Returns Map<conn, { p0?, p1? }> — only overridden endpoints are present.
export function spreadEndpoints(conns, bboxOf) {
  const overrides = new Map();
  const sides = new Map(); // conn → {fromSide, toSide}
  const groups = new Map(); // key → { axis, side, conns: [{conn, oppB, otherSide}] }
  for (const c of conns) {
    const fromB = bboxOf(c.from);
    const toB = bboxOf(c.to);
    if (!fromB || !toB) continue;
    const { fromSide, toSide } = resolveSides(c, fromB, toB);
    sides.set(c, { fromSide, toSide });
    const fromKey = `${c.from}|${fromSide}`;
    const toKey = `${c.to}|${toSide}`;
    if (!groups.has(fromKey)) groups.set(fromKey, { axis: fromSide === "left" || fromSide === "right" ? "y" : "x", side: fromSide, conns: [] });
    groups.get(fromKey).conns.push({ conn: c, oppB: toB, ownerB: fromB });
    if (!groups.has(toKey)) groups.set(toKey, { axis: toSide === "left" || toSide === "right" ? "y" : "x", side: toSide, conns: [] });
    groups.get(toKey).conns.push({ conn: c, oppB: fromB, ownerB: toB });
  }
  for (const { axis, side, conns } of groups.values()) {
    if (conns.length < 2) continue;
    if (conns.some(({ conn }) => Array.isArray(conn.via) && conn.via.length > 0)) continue;
    const ownerB = conns[0].ownerB; // the module that owns the shared side
    const sideLen = side === "top" || side === "bottom" ? ownerB.w : ownerB.h;
    const span = sideLen * 0.7;
    if (span < 12) continue;
    const ordered = [...conns].sort((a, b) =>
      (axis === "x" ? a.oppB.cx - b.oppB.cx : a.oppB.cy - b.oppB.cy));
    const n = ordered.length;
    ordered.forEach(({ conn }, i) => {
      const mid = sidePoint(ownerB, side);
      const offset = n > 1 ? (i / (n - 1) - 0.5) * span : 0;
      const p = axis === "x" ? [mid[0] + offset, mid[1]] : [mid[0], mid[1] + offset];
      const cur = overrides.get(conn) || {};
      if (side === (sides.get(conn).fromSide)) cur.p0 = p; else cur.p1 = p;
      overrides.set(conn, cur);
    });
  }
  return overrides;
}

// Build a path string (for SVG d=) from a connection spec.
// Returns { d, points, length, bbox }
// `endpoints` (optional) overrides the computed attachment points: { p0, p1 }.
export function buildConnectionPath(conn, fromB, toB, endpoints = null) {
  const { fromSide, toSide } = resolveSides(conn, fromB, toB);
  const p0 = (endpoints && endpoints.p0) || sidePoint(fromB, fromSide);
  const p1 = (endpoints && endpoints.p1) || sidePoint(toB, toSide);
  const route = conn.route || "straight";
  const via = conn.via || [];
  let points = [p0, ...via, p1];
  let d;

  if (route === "straight" || via.length >= 2) {
    d = "M " + points.map((p) => `${round(p[0])},${round(p[1])}`).join(" L ");
  } else if (route === "orthogonal-h") {
    const mid = (p0[0] + p1[0]) / 2;
    points = [p0, [mid, p0[1]], [mid, p1[1]], p1];
    d = `M ${round(p0[0])},${round(p0[1])} L ${round(mid)},${round(p0[1])} L ${round(mid)},${round(p1[1])} L ${round(p1[0])},${round(p1[1])}`;
  } else if (route === "orthogonal-v") {
    const mid = (p0[1] + p1[1]) / 2;
    points = [p0, [p0[0], mid], [p1[0], mid], p1];
    d = `M ${round(p0[0])},${round(p0[1])} L ${round(p0[0])},${round(mid)} L ${round(p1[0])},${round(mid)} L ${round(p1[0])},${round(p1[1])}`;
  } else if (route === "curved") {
    const n = sideNormal(fromSide);
    const m = sideNormal(toSide);
    const k = Math.max(40, Math.abs(p1[0] - p0[0]) + Math.abs(p1[1] - p0[1])) * 0.45;
    const c0 = [p0[0] + n[0] * k, p0[1] + n[1] * k];
    const c1 = [p1[0] + m[0] * k, p1[1] + m[1] * k];
    points = [p0, c0, c1, p1];
    d = `M ${round(p0[0])},${round(p0[1])} C ${round(c0[0])},${round(c0[1])} ${round(c1[0])},${round(c1[1])} ${round(p1[0])},${round(p1[1])}`;
  } else {
    d = `M ${round(p0[0])},${round(p0[1])} L ${round(p1[0])},${round(p1[1])}`;
  }

  // sample points along the path for overlap/clearance testing
  const samples = samplePath(points, route);
  const len = pathLength(samples);
  const bb = rectFromPoints(samples);
  return { d, points, samples, length: len, bbox: bb, fromSide, toSide, p0, p1 };
}

export function round(n) {
  return Math.round(n * 100) / 100;
}

export function samplePath(points, route, step = 4) {
  if (route === "curved" && points.length === 4) {
    const [p0, c0, c1, p1] = points;
    const out = [];
    const N = 24;
    for (let i = 0; i <= N; i++) {
      const t = i / N;
      out.push(bezier3(p0, c0, c1, p1, t));
    }
    return out;
  }
  // polyline
  const out = [];
  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i], b = points[i + 1];
    const dist = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const n = Math.max(1, Math.ceil(dist / step));
    for (let j = 0; j < n; j++) {
      const t = j / n;
      out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
    }
  }
  out.push(points[points.length - 1]);
  return out;
}

function bezier3(p0, c0, c1, p1, t) {
  const u = 1 - t;
  const x = u * u * u * p0[0] + 3 * u * u * t * c0[0] + 3 * u * t * t * c1[0] + t * t * t * p1[0];
  const y = u * u * u * p0[1] + 3 * u * u * t * c0[1] + 3 * u * t * t * c1[1] + t * t * t * p1[1];
  return [x, y];
}

export function pathLength(samples) {
  let len = 0;
  for (let i = 1; i < samples.length; i++) {
    len += Math.hypot(samples[i][0] - samples[i - 1][0], samples[i][1] - samples[i - 1][1]);
  }
  return len;
}

// Shared-lane collinearity test for the "edge-edge overlap" check.
// Returns the length of any sub-8px-or-more collinear run.
export function collinearRunLen(samplesA, samplesB) {
  let best = 0;
  for (let i = 0; i < samplesA.length - 1; i++) {
    const a0 = samplesA[i], a1 = samplesA[i + 1];
    for (let j = 0; j < samplesB.length - 1; j++) {
      const b0 = samplesB[j], b1 = samplesB[j + 1];
      // check both segments are (near) parallel and overlap
      const run = collinearRun(a0, a1, b0, b1);
      if (run > best) best = run;
    }
  }
  return best;
}

function collinearRun(a0, a1, b0, b1) {
  const ax = a1[0] - a0[0], ay = a1[1] - a0[1];
  const bx = b1[0] - b0[0], by = b1[1] - b0[1];
  const cross = ax * by - ay * bx;
  if (Math.abs(cross) > 0.001) return 0; // not parallel
  // both segments parallel: check if they share a collinear axis (same x or same y)
  const sameX = Math.abs(a0[0] - b0[0]) < 1.5 && Math.abs(a1[0] - b1[0]) < 1.5;
  const sameY = Math.abs(a0[1] - b0[1]) < 1.5 && Math.abs(a1[1] - b1[1]) < 1.5;
  if (!sameX && !sameY) {
    // maybe parallel but offset (different lane) — count if offset < 4px
    const offset = sameX ? Math.abs(a0[0] - b0[0]) : Math.abs(a0[1] - b0[1]);
    if (offset >= 4) return 0;
  }
  // overlap in the running axis
  if (sameY) {
    const lo = Math.max(Math.min(a0[0], a1[0]), Math.min(b0[0], b1[0]));
    const hi = Math.min(Math.max(a0[0], a1[0]), Math.max(b0[0], b1[0]));
    return Math.max(0, hi - lo);
  }
  if (sameX) {
    const lo = Math.max(Math.min(a0[1], a1[1]), Math.min(b0[1], b1[1]));
    const hi = Math.min(Math.max(a0[1], a1[1]), Math.max(b0[1], b1[1]));
    return Math.max(0, hi - lo);
  }
  return 0;
}
