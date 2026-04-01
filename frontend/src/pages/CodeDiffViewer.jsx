import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';
import { getScanDetail } from '../api/client';

export default function CodeDiffViewer() {
  const { repoId, prNumber, findingIndex } = useParams();
  const navigate = useNavigate();
  const [finding, setFinding] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // repoId: handled loosely, we mock fetching based on pr
    getScanDetail(repoId, prNumber).then(data => {
      setFinding(data.findings[parseInt(findingIndex)]);
      setLoading(false);
    });
  }, [repoId, prNumber, findingIndex]);

  if (loading) return <div style={{ color: '#F1F5F9', padding: '24px' }}>Loading diff...</div>;
  if (!finding) return <div style={{ color: '#E63946', padding: '24px' }}>Finding not found.</div>;

  const severityColor = {
    CRITICAL: '#E63946', HIGH: '#FBBF24',
    MEDIUM: '#60A5FA', LOW: '#4ADE80'
  }[finding.severity] || '#9CA3AF';

  return (
    <div style={{ background: '#0D0F14', minHeight: '100vh', padding: '24px' }}>

      {/* ── HEADER BAR ── */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '16px',
        marginBottom: '24px', borderBottom: '1px solid #1F2937',
        paddingBottom: '16px'
      }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            background: 'transparent', border: '1px solid #1F2937',
            color: '#9CA3AF', padding: '6px 14px', borderRadius: '8px',
            cursor: 'pointer', fontSize: '13px', fontFamily: 'monospace'
          }}
        >
          ← back
        </button>

        <span style={{
          background: severityColor + '22', color: severityColor,
          border: `1px solid ${severityColor}44`,
          padding: '3px 10px', borderRadius: '20px',
          fontSize: '11px', fontWeight: 'bold', fontFamily: 'monospace',
          letterSpacing: '1px'
        }}>
          {finding.severity}
        </span>

        <span style={{
          background: '#111827', color: '#E63946',
          border: '1px solid #1F2937', padding: '3px 10px',
          borderRadius: '20px', fontSize: '11px',
          fontFamily: 'monospace', letterSpacing: '1px'
        }}>
          {finding.type}
        </span>

        <span style={{ color: '#F1F5F9', fontFamily: 'monospace', fontSize: '14px' }}>
          {finding.file}
          <span style={{ color: '#6B7280' }}> : line {finding.line}</span>
        </span>

        <span style={{ color: '#6B7280', fontSize: '13px', marginLeft: 'auto' }}>
          Fixed by Amazon Bedrock · Claude Sonnet 4.5
        </span>
      </div>

      {/* ── DESCRIPTION ── */}
      <p style={{
        color: '#9CA3AF', fontSize: '14px', marginBottom: '20px',
        fontFamily: 'monospace', borderLeft: `3px solid ${severityColor}`,
        paddingLeft: '12px'
      }}>
        {finding.description}
      </p>

      {/* ── DIFF PANEL ── */}
      {finding.original_code && finding.fix_code ? (
        <div style={{
          borderRadius: '12px', overflow: 'hidden',
          border: '1px solid #1F2937', marginBottom: '24px'
        }}>
          <ReactDiffViewer
            oldValue={finding.original_code}
            newValue={finding.fix_code}
            splitView={true}
            compareMethod={DiffMethod.LINES}
            leftTitle="Vulnerable Code (AI-Generated)"
            rightTitle="AI-Fixed Code (Amazon Bedrock)"
            useDarkTheme={true}
            styles={{
              variables: {
                dark: {
                  diffViewerBackground:    '#0D0F14',
                  diffViewerColor:         '#F1F5F9',
                  addedBackground:         '#0d2214',
                  addedColor:              '#4ADE80',
                  removedBackground:       '#2e0d0d',
                  removedColor:            '#E63946',
                  wordAddedBackground:     '#1a3d1a',
                  wordRemovedBackground:   '#3d1a1a',
                  addedGutterBackground:   '#0a1a0a',
                  removedGutterBackground: '#1a0a0a',
                  gutterBackground:        '#111827',
                  gutterColor:             '#374151',
                  codeFoldBackground:      '#111827',
                  codeFoldColor:           '#6B7280',
                  emptyLineBackground:     '#0D0F14',
                  titleColor:              '#9CA3AF',
                  diffViewerTitleBackground: '#111827',
                  diffViewerTitleBorderColor: '#1F2937',
                }
              },
              line: { fontFamily: 'Fira Code, Courier New, monospace', fontSize: '13px' },
              titleBlock: { fontFamily: 'monospace', fontSize: '12px', letterSpacing: '1px', borderBottom: '1px solid #1F2937' },
            }}
          />
        </div>
      ) : (
        <div style={{ padding: '24px', background: '#111827', border: '1px solid #1F2937', color: '#9CA3AF', marginBottom: '24px', borderRadius: '12px' }}>
          No direct code diff available for this finding.
        </div>
      )}

      {/* ── THREE INFO CARDS ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr) minmax(0,1fr)', gap: '16px', marginBottom: '24px' }}>

        {/* Exploit Payload */}
        {finding.exploit_payload && (
          <div style={{
            background: '#111827', border: '1px solid #1F2937',
            borderLeft: '3px solid #E63946', borderRadius: '0 8px 8px 0',
            padding: '16px'
          }}>
            <div style={{ color: '#E63946', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '2px', marginBottom: '10px' }}>
              EXPLOIT PAYLOAD
            </div>
            <code style={{
              display: 'block', background: '#0D0F14', color: '#E63946',
              padding: '10px', borderRadius: '6px', fontSize: '12px',
              fontFamily: 'Fira Code, monospace', marginBottom: '8px',
              wordBreak: 'break-all', lineHeight: '1.6'
            }}>
              {finding.exploit_payload.payload}
            </code>
            <p style={{ color: '#9CA3AF', fontSize: '12px', fontFamily: 'monospace', margin: 0 }}>
              {finding.exploit_payload.impact}
            </p>
          </div>
        )}

        {/* Root Cause */}
        {finding.root_cause && (
          <div style={{
            background: '#111827', border: '1px solid #1F2937',
            borderLeft: '3px solid #FBBF24', borderRadius: '0 8px 8px 0',
            padding: '16px'
          }}>
            <div style={{ color: '#FBBF24', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '2px', marginBottom: '10px' }}>
              WHY THE AI GENERATED THIS
            </div>
            <p style={{ color: '#F1F5F9', fontSize: '13px', fontFamily: 'monospace', marginBottom: '8px', lineHeight: '1.6' }}>
              {finding.root_cause.why_llm_generated_this}
            </p>
            <div style={{
              background: '#0D0F14', padding: '8px 10px', borderRadius: '6px',
              color: '#FBBF24', fontSize: '11px', fontFamily: 'monospace', marginBottom: '8px'
            }}>
              Pattern: {finding.root_cause.llm_behavioral_pattern}
            </div>
            <p style={{ color: '#6B7280', fontSize: '12px', fontFamily: 'monospace', margin: 0 }}>
              Fix: {finding.root_cause.how_to_avoid}
            </p>
          </div>
        )}

        {/* Compliance */}
        {finding.compliance_violations?.length > 0 && (
          <div style={{
            background: '#111827', border: '1px solid #1F2937',
            borderLeft: '3px solid #3B82F6', borderRadius: '0 8px 8px 0',
            padding: '16px'
          }}>
            <div style={{ color: '#3B82F6', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '2px', marginBottom: '10px' }}>
              COMPLIANCE VIOLATIONS
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '10px' }}>
              {finding.compliance_violations.map(v => (
                <span key={v} style={{
                  background: '#1e3a5f', color: '#93C5FD',
                  border: '1px solid #2563EB44', padding: '2px 8px',
                  borderRadius: '20px', fontSize: '11px', fontFamily: 'monospace'
                }}>
                  {v}
                </span>
              ))}
            </div>
            <p style={{ color: '#EF4444', fontSize: '12px', fontFamily: 'monospace', margin: 0 }}>
              {finding.audit_impact}
            </p>
          </div>
        )}
      </div>

      {/* ── ACTION BUTTONS ── */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button style={{
          background: '#E63946', color: '#fff', border: 'none',
          padding: '10px 24px', borderRadius: '8px', cursor: 'pointer',
          fontFamily: 'monospace', fontSize: '13px', fontWeight: 'bold'
        }}
          onClick={() => window.open(finding.auto_fix_pr_url || '#', '_blank')}
        >
          View Auto-Fix PR →
        </button>

        <button style={{
          background: 'transparent', color: '#9CA3AF',
          border: '1px solid #1F2937', padding: '10px 24px',
          borderRadius: '8px', cursor: 'pointer',
          fontFamily: 'monospace', fontSize: '13px'
        }}
          onClick={() => navigator.clipboard.writeText(finding.fix_code || '')}
        >
          Copy Fixed Code
        </button>
      </div>

    </div>
  );
}
