# RedFlag CI — Frontend Work Plan
## Team Neural Forge · HACK'A'WAR 2026 · Sprint Edition
### Owners: Nikhil Virdi (NV) + Shivam Bhardwaj (SB)

---

## 🎯 THEME & AESTHETIC BIBLE
> **Reference Image**: Dark node-canvas UI (like ComfyUI / n8n) — connected box nodes with arrows,
> dot-grid background, floating panels, dark #0d0d0d base, neon green/red accents, monospace fonts.

### Design Tokens (MUST BE IDENTICAL ACROSS BOTH DEVS)

```js
// tailwind.config.js — SB OWNS THIS FILE, NV reads it
colors: {
  bg:         '#0a0a0a',      // base canvas
  surface:    '#141414',      // card/node background
  surfaceAlt: '#1c1c1c',      // slightly lifted surface
  border:     '#2a2a2a',      // node borders
  borderGlow: '#3d3d3d',      // hover border
  red:        '#E63946',      // CRITICAL / danger
  redDim:     '#7a1a20',      // dimmed red bg
  green:      '#39d353',      // safe / trusted
  greenDim:   '#1a3d1f',      // dimmed green bg
  amber:      '#f0a500',      // HIGH / suspicious
  amberDim:   '#3d2a00',      // dimmed amber bg
  blue:       '#58a6ff',      // info / links
  purple:     '#bc8cff',      // AI confidence
  text:       '#e6edf3',      // primary text
  textMuted:  '#8b949e',      // secondary text
  textDim:    '#484f58',      // placeholder text
}
fontFamily: {
  mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
  sans: ['"Space Grotesk"', 'sans-serif'],   // headers only
}
```

### Global CSS Rules (shared, in index.css)
```css
body { background: #0a0a0a; color: #e6edf3; }
.dot-grid {
  background-image: radial-gradient(circle, #2a2a2a 1px, transparent 1px);
  background-size: 24px 24px;
}
.node-card {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
}
.node-card:hover { border-color: #3d3d3d; }
.glow-red  { box-shadow: 0 0 12px rgba(230,57,70,0.3); }
.glow-green { box-shadow: 0 0 12px rgba(57,211,83,0.3); }
```

---

## 📁 COMPLETE FILE STRUCTURE

```
/frontend/
├── src/
│   ├── api/
│   │   └── client.js                ← NV owns
│   ├── components/
│   │   ├── shared/                  ← SB owns ALL shared
│   │   │   ├── Navbar.jsx
│   │   │   ├── SeverityBadge.jsx
│   │   │   ├── NodeCard.jsx         (reusable node wrapper)
│   │   │   ├── ConnectorLine.jsx    (SVG arrow between nodes)
│   │   │   ├── LoadingState.jsx
│   │   │   └── ErrorState.jsx
│   │   ├── dashboard/               ← SB owns ALL dashboard
│   │   │   ├── MetricCards.jsx      (6 stat cards)
│   │   │   ├── VibeDebtChart.jsx    (3-line Recharts)
│   │   │   ├── ScanTable.jsx        (recent scans)
│   │   │   └── RouterSavingsCard.jsx
│   │   ├── findings/                ← NV owns ALL findings
│   │   │   ├── FindingDetail.jsx
│   │   │   ├── ExploitPanel.jsx
│   │   │   ├── RootCausePanel.jsx
│   │   │   ├── ComplianceBadges.jsx
│   │   │   └── ReputationBadge.jsx
│   │   ├── repo/                    ← SB owns ALL repo
│   │   │   ├── WAFScoreCard.jsx
│   │   │   ├── FinOpsCostCard.jsx
│   │   │   ├── PipelineFinding.jsx
│   │   │   └── VulnerabilityLifecycle.jsx
│   │   └── scan/                   ← NV owns ALL scan
│   │       ├── ScannerNodeGraph.jsx  (THE LIVE NODE CANVAS)
│   │       ├── ScannerNode.jsx       (individual node box)
│   │       ├── ScanResultsPanel.jsx
│   │       └── ScannerEdge.jsx       (SVG connector arrows)
│   ├── pages/
│   │   ├── Dashboard.jsx            ← SB owns
│   │   ├── RepoDetail.jsx           ← SB owns
│   │   └── ScanDetail.jsx           ← NV owns
│   ├── hooks/
│   │   ├── useScans.js              ← NV owns
│   │   └── useScanDetail.js         ← NV owns
│   ├── utils/
│   │   └── scoring.js               ← NV owns
│   ├── index.css                    ← SB owns (global styles + dot grid)
│   ├── App.jsx                      ← SB owns (routing)
│   └── main.jsx                     ← SB owns
├── tailwind.config.js               ← SB owns
├── vite.config.js                   ← SB owns
└── package.json                     ← SB owns
```

---

## 👤 SB — Shivam Bhardwaj Work Breakdown

### Hour 0–1.5 | Project Scaffold + Shared Infrastructure

**Files to create:**
- `package.json` — deps: react, react-dom, react-router-dom, recharts, tailwindcss
- `vite.config.js` — standard Vite React config
- `tailwind.config.js` — FULL design token config (colors, fonts, spacing as above)
- `src/index.css` — global styles: dot-grid bg, scrollbar, font imports (JetBrains Mono + Space Grotesk from Google Fonts)
- `src/main.jsx` — ReactDOM.createRoot
- `src/App.jsx` — React Router v6: routes for `/`, `/repo/:repoId`, `/scan/:repoId/:prNumber`

**Shared components:**
- `src/components/shared/Navbar.jsx` — top bar: RedFlag CI logo (red text, maze-style), nav links, user avatars (like reference image), "Share" button stub
- `src/components/shared/SeverityBadge.jsx` — pill badge: CRITICAL=red, HIGH=amber, MEDIUM=blue, LOW=gray. Props: `severity`
- `src/components/shared/NodeCard.jsx` — reusable dark card with green/red dot indicator in top-left corner, title, children. Props: `title`, `status`, `children`
- `src/components/shared/ConnectorLine.jsx` — SVG component that draws animated dashed arrow between two DOM elements using getBoundingClientRect. Props: `fromId`, `toId`, `color`
- `src/components/shared/LoadingState.jsx` — scanning animation: pulsing red dot + "Scanning..." text in mono font
- `src/components/shared/ErrorState.jsx` — red border card with error icon + message + retry button

---

### Hour 1.5–4 | Dashboard Page (Page 1)

**File: `src/pages/Dashboard.jsx`**

Layout:
```
[Navbar]
[dot-grid canvas background]
  [Row: 6 MetricCards side by side]
  [Row: VibeDebtChart (left 60%) | RouterSavingsCard (right 40%)]
  [ScanTable full width]
```

**`src/components/dashboard/MetricCards.jsx`**
6 cards in a grid. Each card: mono font number, label, trend arrow.
- PRs Scanned (green accent)
- Secrets Blocked (red accent)  
- Critical Findings (red, glowing)
- Active Repos (blue accent)
- Bedrock Cost Savings (purple accent) — "90% saved"
- Compliance Violations (amber accent)

Mock data hardcoded initially, replaced later with `client.js`.

**`src/components/dashboard/VibeDebtChart.jsx`**
Recharts `LineChart`. Three lines:
- Security Risk (red, `vibe_risk_score`)
- AI Confidence (purple, `ai_confidence_score`)
- Code Reliability (green, `code_reliability_score`)
Dark chart bg, custom tooltip, legend at bottom. X-axis: PR numbers.

**`src/components/dashboard/ScanTable.jsx`**
Table rows: Repo | PR # | Vibe Score (colored) | Critical | High | Timestamp | Status
Clicking a row navigates to `/repo/:repoId`.

**`src/components/dashboard/RouterSavingsCard.jsx`**
Node-style card: shows `$0.003 actual` vs `$0.031 without routing`. Progress bar showing 90% savings. Bedrock icon placeholder.

---

### Hour 4–6 | Repo Detail Page (Page 2)

**File: `src/pages/RepoDetail.jsx`**

Layout:
```
[Navbar]
[Repo header: name, branch, last scan time, overall Vibe Score gauge]
[Row: WAFScoreCard | FinOpsCostCard]
[VulnerabilityLifecycle full width]
[PipelineFinding list]
[Link to ScanDetail]
```

**`src/components/repo/WAFScoreCard.jsx`**
6-pillar grid (Security, Reliability, Performance, Cost, OpEx, Sustainability). Each pillar: score bar + color (red if violations). Compact dark card layout.

**`src/components/repo/FinOpsCostCard.jsx`**
Per IaC finding cost display. Shows: breach_cost (big red number), fix_cost_delta (green "$0"), monthly_risk_exposure badge.

**`src/components/repo/PipelineFinding.jsx`**
Card per pipeline finding. SECURITY findings: red left border. EFFICIENCY findings: amber left border. Shows: file path, issue, estimated_time_saved chip.

**`src/components/repo/VulnerabilityLifecycle.jsx`**
Horizontal timeline chart (Recharts BarChart horizontal). Each bar = one vuln. Color: red=active, green=fixed. Stat callouts above: "Avg detection lag: 87 hrs" | "Avg fix time: 27 min".

---

### Hour 6–8 | Polish + Connect API + Deploy

- Replace all mock data with `client.js` calls (once NV merges)
- Full responsive pass — mobile → desktop
- Verify dot-grid background renders on all pages
- Projector visibility check — minimum 14px font everywhere
- Deploy to AWS Amplify

---

## 👤 NV — Nikhil Virdi Work Breakdown

### Hour 0–1.5 | API Client Layer

**File: `src/api/client.js`**
```js
const BASE_URL = import.meta.env.VITE_API_URL;

export const getScans = (repoId) =>
  fetch(`${BASE_URL}/api/scans/${repoId}`).then(r => r.json());

export const getScanDetail = (repoId, prNumber) =>
  fetch(`${BASE_URL}/api/scans/${repoId}/${prNumber}`).then(r => r.json());
```

Include full TypeScript-style JSDoc comments matching the frozen API schema from WorkPlan v3 Section 4.

**Mock data** (`src/api/mockData.js`):
Full mock scan response matching the v3 schema with all new fields: `exploit_payload`, `root_cause`, `compliance_violations`, `reputation`, `waf_pillar`, `cost_impact`, `pipeline_findings`, `ai_confidence_score`, `code_reliability_score`, `bedrock_cost_usd`, `cost_savings_pct`.

**Hooks:**
- `src/hooks/useScans.js` — `useScanList(repoId)` → `{ data, loading, error }`
- `src/hooks/useScanDetail.js` — `useScanDetail(repoId, prNumber)` → `{ data, loading, error }`

**`src/utils/scoring.js`**
- `getScoreColor(score)` → tailwind color class
- `getSeverityWeight(severity)` → number
- `formatTimestamp(iso)` → readable string

---

### Hour 1.5–4 | Finding Components

**`src/components/findings/FindingDetail.jsx`**
Master finding card. Shows: type badge, severity badge, file path + line, description. Conditionally renders ExploitPanel, RootCausePanel, ComplianceBadges, ReputationBadge as sub-panels. Props: `finding` object.

**`src/components/findings/ExploitPanel.jsx`**
Red-bordered collapsible panel (default HIDDEN, toggle to reveal). Shows:
- `payload` in dark code block with mono font
- `impact` text in red
- `curl_example` in copyable code block
Header: "⚠ Exploit Payload — Click to Reveal" (toggle button)

**`src/components/findings/RootCausePanel.jsx`**
Amber-bordered info card. Three sections:
- "Why AI generated this:" — `why_llm_generated_this`
- "Pattern:" — `llm_behavioral_pattern` (chip/badge)
- "How to avoid:" — `how_to_avoid` in mono font blockquote

**`src/components/findings/ComplianceBadges.jsx`**
Row of colored pill badges. Parsing `compliance_violations` array:
- `OWASP:*` → red badge
- `SOC2:*` → amber badge
- `CIS:*` → blue badge
Below badges: `audit_impact` text in small red italic.

**`src/components/findings/ReputationBadge.jsx`**
For PACKAGE type only. Large badge: TRUSTED (green border), SUSPICIOUS (amber border), DANGEROUS (red border, pulsing glow). Shows: download count, age in days, has_repository boolean icon.

---

### Hour 4–7 | Scan Detail Page (Page 3) — THE NODE GRAPH

**File: `src/pages/ScanDetail.jsx`**

This is the signature page — the live node canvas matching the reference image exactly.

Layout:
```
[Navbar with "PR #X | repo-name" breadcrumb tab like reference image]
[Full-screen dot-grid canvas]
  [Node graph — positioned absolutely]
  [Right panel — Preview/Results panel]
```

**`src/components/scan/ScannerNodeGraph.jsx`**
The core component. Uses absolute positioning to place nodes on the dark canvas.

Node layout (mirroring reference image structure):
```
[Prompt/PR Info Node] ──→ [Secret Scanner Node]  ──→
                      ──→ [Package Checker Node] ──→
                      ──→ [SQL Scanner Node]     ──→ [Results Aggregator Node] ──→ [Output Panel]
                      ──→ [Prompt Injection Node]──→
                      ──→ [IaC Auditor Node]     ──→
                      ──→ [Git Archaeology Node] ──→
                      ──→ [LLM Antipattern Node] ──→
```

SVG overlay for arrows — absolute positioned `<svg>` covering entire canvas, draws animated dashed paths between nodes using computed positions.

**`src/components/scan/ScannerNode.jsx`**
Individual node box. Props: `title`, `status` ('idle'|'scanning'|'done'|'error'), `findings`, `inputs`, `outputs`.

Visual states:
- idle: gray dot, dim border
- scanning: pulsing green dot, bright border, shimmer animation
- done: static green/red dot based on findings count
- error: red dot, red border glow

Each node shows: scan type label, finding count chip (red if >0), input/output connector dots on left/right edges (matching reference image exactly).

**`src/components/scan/ScannerEdge.jsx`**
SVG `<path>` element. Animated dashed stroke. Color matches source node status. Cubic bezier curve. Props: `x1,y1,x2,y2`, `color`, `animated`.

**`src/components/scan/ScanResultsPanel.jsx`**
Right side panel (like "Preview Image" in reference). Shows:
- Vibe Risk Score gauge (large number, color coded)
- AI Confidence + Code Reliability scores
- Findings list — each row expandable into FindingDetail
- Compliance summary chips
- "View Auto-Fix PR →" link button

---

### Hour 7–8 | Connect + Wire Everything

- Wire `useScanDetail` into `ScanDetail.jsx` — replace mock with live data
- Wire `useScanList` into `Dashboard.jsx` ScanTable via props
- Export all hooks and utilities clearly
- Verify `client.js` BASE_URL reads from `VITE_API_URL` env var

---

## 🔗 MERGE CONTRACT — How to Merge Without Conflicts

### Rule: Zero file overlap. Ever.

| File Path | Owner | Never Touch |
|-----------|-------|-------------|
| `src/api/*` | NV | SB |
| `src/hooks/*` | NV | SB |
| `src/utils/*` | NV | SB |
| `src/components/findings/*` | NV | SB |
| `src/components/scan/*` | NV | SB |
| `src/pages/ScanDetail.jsx` | NV | SB |
| `src/components/shared/*` | SB | NV |
| `src/components/dashboard/*` | SB | NV |
| `src/components/repo/*` | SB | NV |
| `src/pages/Dashboard.jsx` | SB | NV |
| `src/pages/RepoDetail.jsx` | SB | NV |
| `tailwind.config.js` | SB | NV |
| `src/index.css` | SB | NV |
| `src/App.jsx` | SB | NV |

### Merge Steps (Hour 8)
1. SB runs: `git push origin branch/sb-frontend`
2. NV runs: `git push origin branch/nv-frontend`
3. One person (SB) creates PR: `branch/sb-frontend → main`
4. Second PR: `branch/nv-frontend → main`
5. Zero conflicts guaranteed by the table above
6. Run `npm run build` — verify no import errors
7. Deploy to AWS Amplify

---

## ⚡ COMPONENT INTERFACE CONTRACTS

NV's components consume SB's shared components like this — interfaces are FROZEN:

```jsx
// NV uses SB's shared components — import paths only, never edit them
import NodeCard from '../shared/NodeCard';
import SeverityBadge from '../shared/SeverityBadge';
import LoadingState from '../shared/LoadingState';

// SB uses NV's hooks — import paths only, never edit them
import { useScans } from '../../hooks/useScans';
import { useScanDetail } from '../../hooks/useScanDetail';
import { getScoreColor } from '../../utils/scoring';
```

### NodeCard Props (SB defines, NV uses)
```ts
NodeCard: {
  title: string,
  status: 'idle' | 'scanning' | 'done' | 'error',
  children: ReactNode,
  className?: string
}
```

### SeverityBadge Props (SB defines, NV uses)
```ts
SeverityBadge: {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
}
```

### useScans Hook (NV defines, SB uses)
```ts
useScans(repoId: string): {
  data: ScanSummary[] | null,
  loading: boolean,
  error: string | null
}
```

### useScanDetail Hook (NV defines, SB uses)
```ts
useScanDetail(repoId: string, prNumber: number): {
  data: ScanDetail | null,
  loading: boolean,
  error: string | null
}
```

---

## 📦 DEPENDENCIES (package.json)

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.22.0",
    "recharts": "^2.12.0"
  },
  "devDependencies": {
    "vite": "^5.2.0",
    "@vitejs/plugin-react": "^4.3.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

Google Fonts import in `index.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap');
```

---

## 🖥️ PAGE BREAKDOWN SUMMARY

| Page | Route | Owner | Key Components |
|------|-------|-------|----------------|
| Dashboard | `/` | SB | MetricCards, VibeDebtChart, ScanTable, RouterSavingsCard |
| Repo Detail | `/repo/:repoId` | SB | WAFScoreCard, FinOpsCostCard, VulnerabilityLifecycle, PipelineFinding |
| Scan Detail | `/scan/:repoId/:prNumber` | NV | ScannerNodeGraph, ScannerNode, ScannerEdge, ScanResultsPanel, FindingDetail, ExploitPanel, RootCausePanel, ComplianceBadges |

---

## ⏱️ FINAL HOUR TIMELINE

| Hour | SB | NV |
|------|----|----|
| 0–1.5 | Scaffold + Navbar + Shared components | API client + mock data + hooks |
| 1.5–4 | Dashboard page (all 4 components) | FindingDetail + ExploitPanel + RootCausePanel |
| 4–6 | RepoDetail page (all 4 components) | ComplianceBadges + ReputationBadge |
| 6–8 | Polish + responsive + connect API | ScanDetail page + full node graph |
| 8–9 | Deploy to Amplify + visual test | Wire live data + verify node animations |
| 9–10 | Full projector walkthrough | End-to-end demo run |

---

## 🚨 CRITICAL RULES — READ BEFORE WRITING CODE

1. **Every component uses `font-mono` (JetBrains Mono) for all data/numbers/code. `font-sans` (Space Grotesk) only for page titles.**
2. **Background is ALWAYS `bg-[#0a0a0a]` with `.dot-grid` class on the page wrapper div.**
3. **No white backgrounds. Ever. Lightest surface is `bg-[#1c1c1c]`.**
4. **Node borders: `border border-[#2a2a2a] hover:border-[#3d3d3d]` — subtle, not glowing unless status is active.**
5. **CRITICAL findings get `glow-red` class. Safe status gets `glow-green`.**
6. **ConnectorLine / ScannerEdge arrows: animated dashed SVG stroke — not CSS borders.**
7. **The Scan Detail page node graph MUST visually match the reference image — connected boxes with input/output dots, SVG arrows, dark canvas.**

---

*RedFlag CI — Team Neural Forge — HACK'A'WAR 2026*
*Vibe code freely. Ship safely.*
