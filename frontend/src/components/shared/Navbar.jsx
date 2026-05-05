import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()

  return (
    <nav className="flex items-center justify-between z-50 sticky top-0 px-6 py-4 w-full">
      {/* Logo */}
      <div className="flex items-center gap-2.5">
        <div className="logo-dot" />
        <h2 className="logo-text">RedFlag CI</h2>
      </div>

      {/* Nav Pills */}
      <div className="flex items-center gap-1 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.055)] rounded-[999px] p-1">
        <Link
          to="/"
          className={`nav-pill ${location.pathname === '/' ? 'active' : ''}`}
        >
          Dashboard
        </Link>
        <a
          href="https://github.com/Ayaan1911/Project-RedFlag-CI"
          target="_blank"
          rel="noopener noreferrer"
          className="nav-pill"
        >
          GitHub
        </a>
      </div>
      
      {/* Empty spacer for alignment */}
      <div className="w-[100px]"></div>
    </nav>
  )
}
