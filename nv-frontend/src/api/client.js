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
  const res = await fetch(`${BASE_URL}/api/scans/${repoId}/${prNumber}`);
  if (!res.ok) throw new Error(`Failed to fetch scan detail: ${res.status}`);
  return res.json();
};
