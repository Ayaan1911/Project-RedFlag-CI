const BASE_URL = import.meta.env.VITE_API_URL || 'https://k5au64ad1h.execute-api.ap-south-1.amazonaws.com';

/**
 * Fetch all scans for a repository
 * @param {string} repoId
 * @returns {Promise<Array>}
 */
export const getScans = async (repoId) => {
  const res = await fetch(`${BASE_URL}/api/scans/${repoId}`);
  if (!res.ok) throw new Error(`Failed to fetch scans: ${res.status}`);
  return res.json();
};

/**
 * Fetch detailed scan results for a specific PR
 * @param {string} repoId
 * @param {number} prNumber
 * @returns {Promise<Object>}
 */
export const getScanDetail = async (repoId, prNumber) => {
  const { MOCK_SCAN_DETAIL } = await import('./mockData.js');
  
  // Hackathon Lifeline bypass
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ...MOCK_SCAN_DETAIL,
        pr_number: prNumber
      });
    }, 1200); // add slight delay to show loading animation
  });
};

export const getRepoDetail = async (repoId) => {
  const mockData = await import('./repoMockData.js');
  return {
    ...mockData.MOCK_REPO,
    vibeDebt: mockData.MOCK_REPO.techDebtScore,
    aiGeneratedPct: mockData.MOCK_REPO.vibeCodeRatio,
    wafScores: mockData.MOCK_WAF_SCORES.categories,
    complianceSummary: mockData.MOCK_COMPLIANCE_POSTURE.frameworks,
    costBreakdown: {
      actual: mockData.MOCK_FINOPS.totalCost,
      withoutRouting: mockData.MOCK_FINOPS.totalWithoutRouting,
      saved: (mockData.MOCK_FINOPS.totalWithoutRouting - mockData.MOCK_FINOPS.totalCost).toFixed(4),
      pct: mockData.MOCK_FINOPS.savingsPercent,
      haiku: mockData.MOCK_FINOPS.modelBreakdown[0],
      sonnet: mockData.MOCK_FINOPS.modelBreakdown[1],
      perPR: mockData.MOCK_FINOPS.scanCostHistory.map(row => ({
        pr: row.scan,
        withRouter: row.cost,
        withoutRouter: row.costNoRoute
      }))
    }
  };
};

export const getRepoScans = async (repoId) => {
  const scans = await getScans(repoId);
  return scans.map(row => ({
    prNumber: row.pr_number,
    vibeScore: row.vibe_risk_score,
    aiConf: row.ai_confidence_score, 
    critical: row.findings_summary?.critical || 0,
    high: row.findings_summary?.high || 0,
    medium: row.findings_summary?.medium || 0,
    time: row.timestamp
  }));
};

export const getRepoFindings = async (repoId, filters = {}) => {
  const { MOCK_FINDINGS } = await import('./repoMockData.js');
  return MOCK_FINDINGS;
};

export const getVulnLifecycle = async (repoId) => {
  const { MOCK_VULNERABILITY_LIFECYCLE } = await import('./repoMockData.js');
  return MOCK_VULNERABILITY_LIFECYCLE.map(v => ({
    name: v.type + ' ' + v.id,
    type: v.type,
    introducedPR: '#33',
    fixedPR: v.status === 'remediated' ? v.pr : null,
    status: v.status === 'open' ? 'active' : 'fixed',
    durationHours: v.age * 24 + 1.5
  }));
};
