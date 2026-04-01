import { useState, useCallback, useMemo } from 'react'
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
import { MOCK_SCAN_DETAIL } from '../api/mockData'

export default function ScanDetail() {
  const [selectedFinding, setSelectedFinding] = useState(null)

  const nodeTypes = useMemo(() => ({
    scanner: ScannerNode,
    result: ResultNode,
    trigger: TriggerNode,
  }), [])

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => buildPipelineGraph(), [])
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onNodeClick = useCallback((event, node) => {
    // When a scanner node is clicked, show its first related finding
    if (node.data.findings > 0) {
      // Find first finding matching this scanner type
      const typeMap = {
        'fingerprint': 'AI_FINGERPRINT',
        'secrets': 'SECRET',
        'hallucinated-pkg': 'PACKAGE',
        'sql': 'SQL',
        'prompt-injection': 'PROMPT',
        'git-history': 'GIT',
        'antipattern': 'LLM_ANTIPATTERN',
        'iac-auditor': 'IAC',
        'exploit-sim': 'SECRET',
        'root-cause': 'PROMPT',
        'compliance': 'LLM_ANTIPATTERN',
      }
      const scanType = typeMap[node.id]
      if (scanType) {
        const finding = MOCK_SCAN_DETAIL.findings.find(f => f.type === scanType)
        if (finding) setSelectedFinding(finding)
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-bg relative">
      <ParticleBackground />
      <GradientOrb />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />

        <main className="max-w-[1440px] mx-auto px-6 py-6 flex flex-col gap-5 flex-1 w-full">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-text">
                Scan Detail — PR #42
              </h1>
              <p className="text-sm text-textMuted mt-0.5">
                acme/vibe-app · feat/chat-api
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button className="text-xs text-textMuted bg-surface border border-border px-3 py-1.5 rounded-lg hover:text-text transition-colors">
                View PR on GitHub ↗
              </button>
            </div>
          </div>

          {/* Summary Bar */}
          <ScanSummaryBar />

          {/* React Flow Canvas */}
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

            {/* Finding Panel Overlay */}
            {selectedFinding && (
              <FindingPanel
                finding={selectedFinding}
                onClose={() => setSelectedFinding(null)}
              />
            )}
          </div>

          {/* Findings List */}
          <FindingsList onSelectFinding={setSelectedFinding} />
        </main>
      </div>
    </div>
  )
}
