import { MOCK_SCAN_DETAIL } from '../../api/mockData'

const scan = MOCK_SCAN_DETAIL

/**
 * Build the React Flow node + edge graph from scan data
 * 
 * Layout: 5 columns
 *   Col 0: Trigger (PR Webhook)
 *   Col 1: Pre-Processing (AI Fingerprint, Prompt Router)
 *   Col 2: 7 Security Scan Engines
 *   Col 3: Post-Processing (Exploit Sim, Root Cause, Compliance)
 *   Col 4: Final Vibe Debt Score
 */
export function buildPipelineGraph() {
  // Count findings per scanner
  const findingsByType = {}
  scan.findings.forEach(f => {
    const key = f.type
    findingsByType[key] = (findingsByType[key] || 0) + 1
  })

  const nodes = [
    // ── Column 0: Trigger ─────────────────────────
    {
      id: 'trigger',
      type: 'trigger',
      position: { x: 0, y: 300 },
      data: {
        label: 'PR Webhook',
        pr: `#${scan.pr_number}`,
        repo: 'acme/vibe-app',
        branch: 'feat/chat-api',
      },
    },

    // ── Column 1: Pre-Processing ──────────────────
    {
      id: 'fingerprint',
      type: 'scanner',
      position: { x: 300, y: 120 },
      data: {
        label: 'AI Fingerprint',
        icon: '🤖',
        status: 'done',
        findings: findingsByType['AI_FINGERPRINT'] || 0,
        description: 'Detect AI-generated code patterns',
      },
    },
    {
      id: 'prompt-router',
      type: 'scanner',
      position: { x: 300, y: 380 },
      data: {
        label: 'Prompt Router',
        icon: '🔀',
        status: 'done',
        findings: 0,
        description: `Haiku: 7 · Sonnet: 3 · Saved ${scan.cost_savings_pct}%`,
      },
    },

    // ── Column 2: All 7 Security Scan Engines ─────
    {
      id: 'secrets',
      type: 'scanner',
      position: { x: 620, y: 0 },
      data: {
        label: 'Secret Detection',
        icon: '🔐',
        status: findingsByType['SECRET'] > 0 ? 'critical' : 'done',
        findings: findingsByType['SECRET'] || 0,
        description: 'API keys, tokens, credentials',
      },
    },
    {
      id: 'hallucinated-pkg',
      type: 'scanner',
      position: { x: 620, y: 110 },
      data: {
        label: 'Hallucinated Pkg Check',
        icon: '📦',
        status: findingsByType['PACKAGE'] > 0 ? 'critical' : 'done',
        findings: findingsByType['PACKAGE'] || 0,
        description: 'Phantom npm/PyPI package detection',
      },
    },
    {
      id: 'sql',
      type: 'scanner',
      position: { x: 620, y: 220 },
      data: {
        label: 'SQL Injection Scanner',
        icon: '💉',
        status: findingsByType['SQL'] > 0 ? 'critical' : 'done',
        findings: findingsByType['SQL'] || 0,
        description: 'Pattern & context analysis',
      },
    },
    {
      id: 'prompt-injection',
      type: 'scanner',
      position: { x: 620, y: 330 },
      data: {
        label: 'Prompt Injection Detector',
        icon: '💬',
        status: findingsByType['PROMPT'] > 0 ? 'critical' : 'done',
        findings: findingsByType['PROMPT'] || 0,
        description: 'LLM input sanitization checks',
      },
    },
    {
      id: 'antipattern',
      type: 'scanner',
      position: { x: 620, y: 440 },
      data: {
        label: 'LLM Anti-Pattern Scanner',
        icon: '⚠️',
        status: findingsByType['LLM_ANTIPATTERN'] > 0 ? 'critical' : 'done',
        findings: findingsByType['LLM_ANTIPATTERN'] || 0,
        description: 'CORS, rate-limit, permissive defaults',
      },
    },
    {
      id: 'git-history',
      type: 'scanner',
      position: { x: 620, y: 550 },
      data: {
        label: 'Git History Archaeology',
        icon: '📜',
        status: findingsByType['GIT'] > 0 ? 'critical' : 'done',
        findings: findingsByType['GIT'] || 0,
        description: 'Leaked secrets in old commits',
      },
    },
    {
      id: 'iac-auditor',
      type: 'scanner',
      position: { x: 620, y: 660 },
      data: {
        label: 'IaC Permission Auditor',
        icon: '🏗️',
        status: findingsByType['IAC'] > 0 ? 'critical' : 'done',
        findings: (findingsByType['IAC'] || 0) + (findingsByType['PIPELINE'] || 0),
        description: 'Terraform, CloudFormation, CI/CD',
      },
    },

    // ── Column 3: Post-Processing ─────────────────
    {
      id: 'exploit-sim',
      type: 'scanner',
      position: { x: 960, y: 80 },
      data: {
        label: 'Exploit Simulator',
        icon: '💥',
        status: 'done',
        findings: scan.findings.filter(f => f.exploit_payload).length,
        description: 'PoC attack payload generation',
      },
    },
    {
      id: 'root-cause',
      type: 'scanner',
      position: { x: 960, y: 280 },
      data: {
        label: 'Root Cause Explainer',
        icon: '🧠',
        status: 'done',
        findings: scan.findings.filter(f => f.root_cause).length,
        description: 'Why the LLM wrote insecure code',
      },
    },
    {
      id: 'compliance',
      type: 'scanner',
      position: { x: 960, y: 480 },
      data: {
        label: 'Compliance Mapper',
        icon: '🛡️',
        status: scan.compliance_summary.total_controls_violated > 0 ? 'critical' : 'done',
        findings: scan.compliance_summary.total_controls_violated,
        description: 'SOC2 · OWASP · CIS · WAF',
      },
    },

    // ── Column 4: Final Output ────────────────────
    {
      id: 'vibe-score',
      type: 'result',
      position: { x: 1300, y: 240 },
      data: {
        label: 'Vibe Debt Score',
        score: scan.vibe_risk_score,
        sublabel: `AI: ${scan.ai_confidence_score}% · Reliability: ${scan.code_reliability_score}`,
        icon: '🎯',
        scoreColor: scan.vibe_risk_score >= 81 ? 'text-red' : scan.vibe_risk_score >= 61 ? 'text-amber' : 'text-green',
      },
    },
  ]

  const edges = [
    // Trigger → Column 1 (Pre-Processing)
    { id: 'e-trigger-fp', source: 'trigger', target: 'fingerprint', animated: true },
    { id: 'e-trigger-router', source: 'trigger', target: 'prompt-router', animated: true },

    // Column 1 → Column 2 (All 7 Scan Engines)
    { id: 'e-fp-secrets', source: 'fingerprint', target: 'secrets' },
    { id: 'e-fp-pkg', source: 'fingerprint', target: 'hallucinated-pkg' },
    { id: 'e-fp-sql', source: 'fingerprint', target: 'sql' },
    { id: 'e-router-prompt', source: 'prompt-router', target: 'prompt-injection' },
    { id: 'e-router-anti', source: 'prompt-router', target: 'antipattern' },
    { id: 'e-router-git', source: 'prompt-router', target: 'git-history' },
    { id: 'e-router-iac', source: 'prompt-router', target: 'iac-auditor' },

    // Column 2 → Column 3 (Post-Processing)
    { id: 'e-secrets-exploit', source: 'secrets', target: 'exploit-sim' },
    { id: 'e-sql-exploit', source: 'sql', target: 'exploit-sim' },
    { id: 'e-pkg-exploit', source: 'hallucinated-pkg', target: 'exploit-sim' },
    { id: 'e-prompt-root', source: 'prompt-injection', target: 'root-cause' },
    { id: 'e-git-root', source: 'git-history', target: 'root-cause' },
    { id: 'e-anti-root', source: 'antipattern', target: 'root-cause' },
    { id: 'e-secrets-compliance', source: 'secrets', target: 'compliance' },
    { id: 'e-anti-compliance', source: 'antipattern', target: 'compliance' },
    { id: 'e-iac-compliance', source: 'iac-auditor', target: 'compliance' },

    // Column 3 → Result
    { id: 'e-exploit-score', source: 'exploit-sim', target: 'vibe-score', animated: true },
    { id: 'e-root-score', source: 'root-cause', target: 'vibe-score', animated: true },
    { id: 'e-compliance-score', source: 'compliance', target: 'vibe-score', animated: true },
  ]

  // Default edge style with smoothstep curves (ComfyUI aesthetic)
  const styledEdges = edges.map(e => ({
    ...e,
    type: 'smoothstep',
    style: {
      stroke: e.animated ? '#39d353' : '#3d3d3d',
      strokeWidth: e.animated ? 2 : 1.5,
    },
  }))

  return { nodes, edges: styledEdges }
}
