import { useState, useCallback, useMemo, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import ReactFlow, {
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'

import Navbar from '../components/shared/Navbar'
import ParticleBackground from '../components/shared/ParticleBackground'
import GradientOrb from '../components/shared/GradientOrb'
import ScanSummaryBar from '../components/scan/ScanSummaryBar'
import FindingsList from '../components/scan/FindingsList'
import FindingPanel from '../components/scan/FindingPanel'
import ScannerNode from '../components/scan/ScannerNode'
import ResultNode from '../components/scan/ResultNode'
import TriggerNode from '../components/scan/TriggerNode'
import { buildPipelineGraph } from '../components/scan/pipelineLayout'
import { getScanDetail } from '../api/client'

export default function ScanDetail() {
  const { repoId, prNumber } = useParams()
  const [scanData, setScanData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedFinding, setSelectedFinding] = useState(null)

  const nodeTypes = useMemo(() => ({
    scanner: ScannerNode,
    result: ResultNode,
    trigger: TriggerNode,
  }), [])

  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => buildPipelineGraph(scanData),
    [scanData],
  )
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [initialEdges, initialNodes, setEdges, setNodes])

  const onNodeClick = useCallback((event, node) => {
    if (node.data.findings > 0) {
      const typeMap = {
        fingerprint: 'AI_FINGERPRINT',
        secrets: 'SECRET',
        'hallucinated-pkg': 'PACKAGE',
        sql: 'SQL',
        'prompt-injection': 'PROMPT',
        'git-history': 'GIT',
        antipattern: 'LLM_ANTIPATTERN',
        'iac-auditor': 'IAC',
        'exploit-sim': 'SECRET',
        'root-cause': 'PROMPT',
        compliance: 'LLM_ANTIPATTERN',
      }
      const scanType = typeMap[node.id]
      if (scanType && scanData) {
        const finding = scanData.findings.find((f) => f.type === scanType)
        if (finding) setSelectedFinding(finding)
      }
    }
  }, [scanData])

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        setError(null)
        const data = await getScanDetail(repoId, prNumber)
        setScanData(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [repoId, prNumber])

  if (loading) return <div className="min-h-screen bg-bg flex items-center justify-center text-text text-xl">Calling AWS Bedrock AI... please wait.</div>
  if (error) return <div className="min-h-screen bg-bg flex items-center justify-center text-red text-xl">Error: {error}</div>
  if (!scanData) return <div className="min-h-screen bg-bg flex items-center justify-center text-text text-xl">No scan data found for this PR.</div>

  const repoFullName = scanData.repo_full_name || repoId
  const prUrl = repoFullName.includes('/') ? `https://github.com/${repoFullName}/pull/${scanData.pr_number}` : null

  return (
    <div className="min-h-screen bg-bg relative">
      <ParticleBackground />
      <GradientOrb />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />

        <main className="max-w-[1440px] mx-auto px-6 py-6 flex flex-col gap-5 flex-1 w-full">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-text">
                Scan Detail - PR #{scanData.pr_number}
              </h1>
              <p className="text-sm text-textMuted mt-0.5">
                {repoFullName} · AI Security Report
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                className="text-xs text-textMuted bg-surface border border-border px-3 py-1.5 rounded-lg hover:text-text transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => prUrl && window.open(prUrl, '_blank')}
                disabled={!prUrl}
              >
                View PR on GitHub →
              </button>
            </div>
          </div>

          <ScanSummaryBar scan={scanData} />

          <div className="relative glass-1 overflow-hidden" style={{ height: '780px' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              defaultEdgeOptions={{ type: 'smoothstep', animated: false }}
              fitView
              fitViewOptions={{ padding: 0.12 }}
              minZoom={0.3}
              maxZoom={1.5}
              snapToGrid
              snapGrid={[12, 12]}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#2a2a2a" gap={24} size={1} />
              <Controls />
              <MiniMap
                nodeColor={() => '#2a2a2a'}
                maskColor="rgba(10, 10, 10, 0.8)"
              />
            </ReactFlow>

            {selectedFinding && (
              <FindingPanel
                finding={selectedFinding}
                onClose={() => setSelectedFinding(null)}
              />
            )}
          </div>

          <FindingsList findings={scanData.findings} onSelectFinding={setSelectedFinding} />
        </main>
      </div>
    </div>
  )
}
