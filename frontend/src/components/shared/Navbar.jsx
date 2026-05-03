import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()

  const navItems = [
    { label: 'Overview', path: '/' },
    { label: 'Repository', path: '/repo/demo' },
    { label: 'Scan Insights', path: '/repo/demo/scan/42' },
  ]

  return (
    <nav className="flex items-center justify-between z-50 sticky top-0 px-6 py-4 w-full">
      {/* Logo */}
      <div className="flex items-center gap-2.5">
        <div className="logo-dot" />
        <h2 className="logo-text">RedFlag CI</h2>
      </div>

      {/* Nav Pills (Resq.io Style) */}
      <div className="flex items-center gap-1 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.055)] rounded-[999px] p-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || (location.pathname.startsWith(item.path) && item.path !== '/')
          return (
            <Link
              key={item.label}
              to={item.path}
              className={`nav-pill ${isActive ? 'active' : ''}`}
            >
              {item.label}
            </Link>
          )
        })}
      </div>

      {/* Right Icons */}
      <div className="flex items-center gap-3">
        <button className="nav-icon-btn group">
          <span className="text-[16px] group-hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]">🔍</span>
        </button>
        <button className="nav-icon-btn relative group">
          <span className="text-[16px] group-hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]">🔔</span>
          <span className="absolute top-[8px] right-[8px] w-2 h-2 bg-brandPink rounded-full shadow-[0_0_8px_rgba(255,45,107,0.8)]"></span>
        </button>
        <div className="nav-avatar flex items-center justify-center ml-2 shadow-[0_0_14px_rgba(74,108,247,0.25)]">
          NV
        </div>
      </div>
    </nav>
  )
}
