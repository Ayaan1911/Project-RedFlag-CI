export default function GradientOrb() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden" style={{ background: '#0D0D14' }}>
      {/* Shell background to give depth */}
      <div className="absolute inset-0 bg-[#111118] bg-opacity-80" />
      
      {/* Primary ambient glow — top left, blue/purple */}
      <div
        className="absolute rounded-full blur-[140px] animate-orb-drift"
        style={{
          width: '700px',
          height: '700px',
          top: '20%',
          left: '20%',
          transform: 'translate(-50%, -50%)',
          background: 'radial-gradient(ellipse at center, rgba(100,80,255,0.08) 0%, transparent 60%)',
        }}
      />
      {/* Secondary ambient glow — bottom right, green/teal */}
      <div
        className="absolute rounded-full blur-[140px] animate-orb-drift-reverse"
        style={{
          width: '600px',
          height: '600px',
          bottom: '20%',
          right: '20%',
          transform: 'translate(50%, 50%)',
          background: 'radial-gradient(ellipse at center, rgba(0,210,150,0.06) 0%, transparent 55%)',
        }}
      />
    </div>
  )
}
