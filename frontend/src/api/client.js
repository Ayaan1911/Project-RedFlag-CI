const BASE_URL = import.meta.env.VITE_API_URL || ''

/**
 * Fetch all scans for a repository
 * @param {string} repoId
 * @returns {Promise<Array>}
 */
export const getScans = async (repoId) => {
  const res = await fetch(`${BASE_URL}/api/scans/${repoId}`)
  if (!res.ok) throw new Error(`Failed to fetch scans: ${res.status}`)
  return res.json()
}

/**
 * Fetch detailed scan results for a specific PR
 * @param {string} repoId
 * @param {number|string} prNumber
 * @returns {Promise<Object>}
 */
export const getScanDetail = async (repoId, prNumber) => {
  const res = await fetch(`${BASE_URL}/api/scans/${repoId}/${prNumber}`)
  if (!res.ok) throw new Error(`Failed to fetch scan detail: ${res.status}`)
  return res.json()
}

export const getRepoDetail = async (repoId) => {
  const scans = await getScans(repoId)
  const latestScan = scans[0] || null
  const latestDetail = latestScan ? await getScanDetail(repoId, latestScan.pr_number) : null

  const complianceSummary = latestDetail?.compliance_summary || {
    owasp_violations: [],
    soc2_violations: [],
    cis_violations: [],
    waf_violations: [],
    llm_owasp_violations: [],
    total_controls_violated: 0,
    audit_ready: true,
  }

  const repoName = latestScan?.repo_full_name || latestDetail?.repo_full_name || repoId
  const repoUrl = repoName.includes('/') ? `https://github.com/${repoName}` : null

  const findings = latestDetail?.findings || []
  const wafScores = buildWafScores(findings)

  return {
    repo: {
      id: repoId,
      name: repoName,
      fullName: repoName,
      description: 'Repository activity derived from RedFlag CI scan history',
      language: inferPrimaryLanguage(findings),
      lastScan: latestScan?.timestamp || null,
      totalScans: scans.length,
      vibeCodeRatio: latestScan?.ai_confidence_score || 0,
      techDebtScore: latestScan?.vibe_risk_score || 0,
      repoUrl,
    },
    latestScan: latestDetail,
    scans: scans.map((scan) => ({
      repoId,
      repoFullName: scan.repo_full_name || repoName,
      prNumber: scan.pr_number,
      vibeScore: scan.vibe_risk_score,
      aiConf: scan.ai_confidence_score,
      codeReliability: scan.code_reliability_score,
      critical: scan.findings_summary?.critical || 0,
      high: scan.findings_summary?.high || 0,
      medium: scan.findings_summary?.medium || 0,
      low: scan.findings_summary?.low || 0,
      time: scan.timestamp,
    })),
    findings,
    complianceSummary,
    costBreakdown: latestDetail ? {
      actual: latestDetail.bedrock_cost_usd || 0,
      withoutRouting: latestDetail.bedrock_cost_without_routing_usd || 0,
      saved: (latestDetail.bedrock_cost_without_routing_usd || 0) - (latestDetail.bedrock_cost_usd || 0),
      pct: latestDetail.cost_savings_pct || 0,
      perPR: scans.map((scan) => ({
        scan: `PR #${scan.pr_number}`,
        cost: scan.pr_number === latestScan?.pr_number ? (latestDetail.bedrock_cost_usd || 0) : 0,
        costNoRoute: scan.pr_number === latestScan?.pr_number ? (latestDetail.bedrock_cost_without_routing_usd || 0) : 0,
      })),
    } : null,
    wafScores,
    vulnerabilityTimeline: buildVulnerabilityTimeline(findings, latestDetail?.pr_number),
  }
}

function inferPrimaryLanguage(findings) {
  const file = findings.find((finding) => finding.file)?.file || ''
  const ext = file.split('.').pop()?.toLowerCase()
  const languageMap = {
    js: 'JavaScript',
    jsx: 'JavaScript',
    ts: 'TypeScript',
    tsx: 'TypeScript',
    py: 'Python',
    java: 'Java',
    go: 'Go',
    rb: 'Ruby',
    php: 'PHP',
  }
  return languageMap[ext] || 'Unknown'
}

function buildWafScores(findings) {
  const buckets = [
    { name: 'Input Validation', score: 100, violations: 0, icon: 'Shield' },
    { name: 'Authentication', score: 100, violations: 0, icon: 'Lock' },
    { name: 'Data Protection', score: 100, violations: 0, icon: 'Disk' },
    { name: 'Rate Limiting', score: 100, violations: 0, icon: 'Timer' },
    { name: 'Error Handling', score: 100, violations: 0, icon: 'Scan' },
    { name: 'Logging & Monitoring', score: 100, violations: 0, icon: 'List' },
  ]

  findings.forEach((finding) => {
    if (finding.type === 'SQL' || finding.type === 'PROMPT') {
      buckets[0].violations += 1
    }
    if (finding.type === 'SECRET' || finding.type === 'GIT') {
      buckets[2].violations += 1
    }
    if (finding.type === 'LLM_ANTIPATTERN') {
      buckets[1].violations += 1
      buckets[3].violations += 1
    }
    if (finding.type === 'PACKAGE') {
      buckets[5].violations += 1
    }
    if (finding.type === 'IAC') {
      buckets[4].violations += 1
    }
  })

  const categories = buckets.map((bucket) => ({
    ...bucket,
    score: Math.max(0, 100 - bucket.violations * 15),
  }))

  const overall = categories.length
    ? Math.round(categories.reduce((sum, item) => sum + item.score, 0) / categories.length)
    : 0

  return { overall, categories }
}

function buildVulnerabilityTimeline(findings, prNumber) {
  return findings.map((finding, index) => ({
    id: `${finding.file || 'finding'}-${finding.line || 0}-${index}`,
    name: finding.type,
    introduced: Number(prNumber || 0),
    fixed: null,
    active: true,
  }))
}
