// Extended mock data for Repo Detail page

export const MOCK_REPO = {
  name: 'acme/vibe-app',
  description: 'Full-stack AI-powered SaaS application',
  language: 'JavaScript',
  lastScan: '2026-04-01T10:30:00Z',
  totalScans: 42,
  defaultBranch: 'main',
  vibeCodeRatio: 78, // % of code that is AI-generated
  techDebtScore: 87,
}

export const MOCK_WAF_SCORES = {
  overall: 72,
  categories: [
    { name: 'Input Validation', score: 45, maxScore: 100, violations: 3, icon: '🛡️' },
    { name: 'Authentication', score: 80, maxScore: 100, violations: 1, icon: '🔐' },
    { name: 'Data Protection', score: 55, maxScore: 100, violations: 2, icon: '💾' },
    { name: 'Rate Limiting', score: 30, maxScore: 100, violations: 4, icon: '⏱️' },
    { name: 'Error Handling', score: 90, maxScore: 100, violations: 0, icon: '🧯' },
    { name: 'Logging & Monitoring', score: 85, maxScore: 100, violations: 1, icon: '📋' },
  ],
}

export const MOCK_FINOPS = {
  totalCost: 0.0482,
  totalWithoutRouting: 0.4200,
  savingsPercent: 88.5,
  modelBreakdown: [
    { model: 'Claude 3.5 Haiku', calls: 34, cost: 0.0068, color: '#58a6ff' },
    { model: 'Claude Sonnet 4', calls: 8, cost: 0.0414, color: '#bc8cff' },
  ],
  scanCostHistory: [
    { scan: 'PR #33', cost: 0.003, costNoRoute: 0.031 },
    { scan: 'PR #36', cost: 0.008, costNoRoute: 0.065 },
    { scan: 'PR #38', cost: 0.004, costNoRoute: 0.042 },
    { scan: 'PR #41', cost: 0.012, costNoRoute: 0.095 },
    { scan: 'PR #42', cost: 0.005, costNoRoute: 0.048 },
  ],
}

export const MOCK_VULNERABILITY_LIFECYCLE = [
  { id: 'VUL-001', type: 'SECRET', severity: 'CRITICAL', file: 'config/settings.py', detectedAt: '2026-03-28', status: 'open', age: 4, pr: '#38' },
  { id: 'VUL-002', type: 'SQL', severity: 'CRITICAL', file: 'routes/users.js', detectedAt: '2026-03-29', status: 'open', age: 3, pr: '#36' },
  { id: 'VUL-003', type: 'PACKAGE', severity: 'CRITICAL', file: 'package.json', detectedAt: '2026-04-01', status: 'open', age: 0, pr: '#42' },
  { id: 'VUL-004', type: 'PROMPT', severity: 'HIGH', file: 'routes/chat.js', detectedAt: '2026-04-01', status: 'open', age: 0, pr: '#42' },
  { id: 'VUL-005', type: 'GIT', severity: 'HIGH', file: 'config.js', detectedAt: '2026-03-30', status: 'remediated', age: 2, pr: '#38', fixedAt: '2026-03-31' },
  { id: 'VUL-006', type: 'LLM_ANTIPATTERN', severity: 'MEDIUM', file: 'server.js', detectedAt: '2026-03-29', status: 'accepted', age: 3, pr: '#36' },
  { id: 'VUL-007', type: 'SECRET', severity: 'CRITICAL', file: 'lib/auth.js', detectedAt: '2026-03-25', status: 'remediated', age: 7, pr: '#33', fixedAt: '2026-03-26' },
  { id: 'VUL-008', type: 'IAC', severity: 'MEDIUM', file: 'terraform/s3.tf', detectedAt: '2026-04-01', status: 'open', age: 0, pr: '#42' },
]

export const MOCK_COMPLIANCE_POSTURE = {
  frameworks: [
    {
      name: 'OWASP Top 10',
      icon: '🌐',
      totalControls: 10,
      violated: 3,
      violations: ['A03:2021 — Injection', 'A06:2021 — Vuln Components', 'A07:2021 — Auth Failures'],
    },
    {
      name: 'SOC 2 Type II',
      icon: '📜',
      totalControls: 64,
      violated: 5,
      violations: ['CC6.1', 'CC6.6', 'CC6.7', 'CC7.1', 'CC8.1'],
    },
    {
      name: 'CIS Benchmarks',
      icon: '🏛️',
      totalControls: 20,
      violated: 3,
      violations: ['2.1 — Asset Inventory', '13.1 — Data Protection', '18.1 — Pen Testing'],
    },
    {
      name: 'OWASP LLM Top 10',
      icon: '🤖',
      totalControls: 10,
      violated: 1,
      violations: ['LLM01:2025 — Prompt Injection'],
    },
  ],
}

export const MOCK_SCAN_HISTORY = [
  { pr: '#42', score: 87, findings: 10, criticals: 3, timestamp: '2026-04-01T10:30:00Z', status: 'failed' },
  { pr: '#41', score: 45, findings: 7, criticals: 1, timestamp: '2026-03-31T16:00:00Z', status: 'warning' },
  { pr: '#38', score: 12, findings: 4, criticals: 0, timestamp: '2026-03-30T09:15:00Z', status: 'passed' },
  { pr: '#36', score: 68, findings: 6, criticals: 2, timestamp: '2026-03-29T14:45:00Z', status: 'failed' },
  { pr: '#33', score: 5, findings: 2, criticals: 0, timestamp: '2026-03-28T11:20:00Z', status: 'passed' },
]
