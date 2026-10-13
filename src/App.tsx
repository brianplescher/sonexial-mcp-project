import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Server, Database, Code, Terminal, Shield, BookOpen, 
  Users, Search, Zap, Globe, ChevronRight, Copy, Check,
  Cpu, Layers, FileText, GitBranch, Package, Play,
  ArrowRight, ExternalLink, Star, Lock, Wifi, Box
} from 'lucide-react'

// Sample data for demonstration
const sampleAuthors = [
  { id: 'sonexial:author:a1b2c3d4', name: 'Kael Thornwood', genres: ['cyberpunk', 'noir'], status: 'sonexial_verified', books: 3 },
  { id: 'sonexial:author:e5f6g7h8', name: 'Mira Solstice', genres: ['romantasy', 'fantasy'], status: 'verified_human', books: 3 },
  { id: 'sonexial:author:i9j0k1l2', name: 'Dante Ashcroft', genres: ['grimdark', 'cosmic horror'], status: 'sonexial_verified', books: 3 },
  { id: 'sonexial:author:m3n4o5p6', name: 'Luna Evergreen', genres: ['cozy fantasy'], status: 'verified_human', books: 2 },
  { id: 'sonexial:author:q7r8s9t0', name: 'Orion Steel', genres: ['space opera', 'hard-scifi'], status: 'sonexial_verified', books: 3 },
  { id: 'sonexial:author:u1v2w3x4', name: 'Seraphina Voss', genres: ['literary-speculative', 'climate-fiction'], status: 'verified_human', books: 2 },
  { id: 'sonexial:author:y5z6a7b8', name: 'Vex Nyx', genres: ['cyberpunk', 'techno-thriller'], status: 'unverified', books: 2 },
  { id: 'sonexial:author:c9d0e1f2', name: 'Nadia Riversong', genres: ['climate-fiction', 'solarpunk'], status: 'sonexial_verified', books: 3 },
]

const tools = [
  { name: 'ping', description: 'Health check. Returns service status and version.', category: 'system' },
  { name: 'search_authors', description: 'Search for indie authors by query, genre, tropes, and verification status.', category: 'authors' },
  { name: 'get_author', description: 'Get full author profile by ID.', category: 'authors' },
  { name: 'list_books', description: 'List all books by an author.', category: 'books' },
  { name: 'get_book', description: 'Get full book details by ID.', category: 'books' },
  { name: 'search_lore', description: 'Search lore entries by keyword across title, content, and tags.', category: 'lore' },
  { name: 'get_related_authors', description: 'Find authors related to a given author.', category: 'authors' },
  { name: 'get_author_llms_txt', description: 'Get a clean Markdown summary suitable for AI consumption.', category: 'authors' },
]

const toolExamples: Record<string, { input: string; output: string }> = {
  ping: {
    input: `{
  "tool": "ping",
  "arguments": {}
}`,
    output: `{
  "status": "ok",
  "service": "sonexial-author-mcp",
  "version": "0.1.0"
}`
  },
  search_authors: {
    input: `{
  "tool": "search_authors",
  "arguments": {
    "genre": "cyberpunk",
    "tropes": ["found-family"],
    "verified_only": false,
    "limit": 5
  }
}`,
    output: `{
  "status": "ok",
  "results": [
    {
      "id": "sonexial:author:a1b2c3d4",
      "name": "Kael Thornwood",
      "genres": ["cyberpunk", "noir"],
      "tropes": ["found-family", "underdog-protagonist"],
      "verification_status": "sonexial_verified",
      "website": "https://kaelthornwood.example.com",
      "match_reason": "genre: cyberpunk; tropes: found-family"
    }
  ],
  "total": 1,
  "limit": 5
}`
  },
  get_author: {
    input: `{
  "tool": "get_author",
  "arguments": {
    "author_id": "sonexial:author:a1b2c3d4"
  }
}`,
    output: `{
  "id": "sonexial:author:a1b2c3d4",
  "slug": "kael-thornwood",
  "name": "Kael Thornwood",
  "pen_names": ["K.T. Void"],
  "website": "https://kaelthornwood.example.com",
  "bio_short": "Cyberpunk and noir author exploring identity in digital worlds.",
  "genres": ["cyberpunk", "noir", "speculative fiction"],
  "tropes": ["found-family", "underdog-protagonist", "corporate-dystopia"],
  "verification_status": "sonexial_verified"
}`
  },
  search_lore: {
    input: `{
  "tool": "search_lore",
  "arguments": {
    "query": "ghost",
    "category": "technology",
    "limit": 5
  }
}`,
    output: `{
  "status": "ok",
  "results": [
    {
      "id": "sonexial:lore:abc123",
      "title": "The Ghost Signal",
      "category": "technology",
      "author_id": "sonexial:author:a1b2c3d4",
      "spoiler_level": "major",
      "tags": ["technology", "mystery", "ai"]
    }
  ],
  "total": 1,
  "limit": 5
}`
  }
}

function CodeBlock({ code, language = 'json' }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false)
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative group">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 p-1.5 rounded-md bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 hover:text-white opacity-0 group-hover:opacity-100 transition-all"
      >
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>
      <pre className="bg-gray-900 rounded-lg p-4 overflow-x-auto text-sm font-mono text-gray-300 border border-gray-700/50">
        <code>{code}</code>
      </pre>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string | number; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-5"
    >
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-lg ${color}`}>
          <Icon size={20} className="text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-sm text-gray-400">{label}</p>
        </div>
      </div>
    </motion.div>
  )
}

function TabButton({ active, onClick, children, icon: Icon }: { active: boolean; onClick: () => void; children: React.ReactNode; icon: any }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
        active
          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
          : 'text-gray-400 hover:text-white hover:bg-gray-800'
      }`}
    >
      <Icon size={16} />
      {children}
    </button>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedTool, setSelectedTool] = useState<string | null>('ping')

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Server size={18} className="text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">Sonexial Author MCP</h1>
                <p className="text-xs text-gray-500">v0.1.0 • Model Context Protocol Server</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Prototype Ready
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <nav className="flex flex-wrap gap-2 mb-8">
          <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} icon={Layers}>Overview</TabButton>
          <TabButton active={activeTab === 'tools'} onClick={() => setActiveTab('tools')} icon={Zap}>Tools</TabButton>
          <TabButton active={activeTab === 'data'} onClick={() => setActiveTab('data')} icon={Database}>Sample Data</TabButton>
          <TabButton active={activeTab === 'setup'} onClick={() => setActiveTab('setup')} icon={Terminal}>Setup</TabButton>
          <TabButton active={activeTab === 'deploy'} onClick={() => setActiveTab('deploy')} icon={Globe}>Deploy</TabButton>
        </nav>

        <AnimatePresence mode="wait">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-8"
            >
              {/* Hero */}
              <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-900/50 via-gray-900 to-purple-900/50 border border-gray-700/50 p-8 md:p-12">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-600/10 via-transparent to-transparent"></div>
                <div className="relative">
                  <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                    Indie Authors as Queryable AI Entities
                  </h2>
                  <p className="text-lg text-gray-300 max-w-2xl mb-6">
                    Sonexial Author MCP transforms passive author web pages into a structured, AI-callable data layer. 
                    AI assistants, agents, and developer tools can search authors, retrieve books, explore lore, 
                    and discover relationships—all through the Model Context Protocol.
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <a href="https://modelcontextprotocol.io" target="_blank" rel="noopener" className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition-colors">
                      MCP Specification <ExternalLink size={14} />
                    </a>
                    <span className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300">
                      <Github size={14} /> Python 3.11+
                    </span>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard icon={Users} label="Sample Authors" value={8} color="bg-blue-600" />
                <StatCard icon={BookOpen} label="Sample Books" value={21} color="bg-purple-600" />
                <StatCard icon={FileText} label="Lore Entries" value={30} color="bg-emerald-600" />
                <StatCard icon={Zap} label="MCP Tools" value={8} color="bg-amber-600" />
              </div>

              {/* Architecture */}
              <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Cpu size={20} className="text-indigo-400" />
                  Architecture
                </h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Wifi size={16} className="text-blue-400" />
                      <span className="font-medium text-sm">Transport Layer</span>
                    </div>
                    <p className="text-xs text-gray-400">stdio for local clients, HTTP/SSE for remote deployment. Bearer token auth for HTTP mode.</p>
                  </div>
                  <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap size={16} className="text-purple-400" />
                      <span className="font-medium text-sm">Tool Layer</span>
                    </div>
                    <p className="text-xs text-gray-400">8 MCP tools for search, retrieval, and relationship queries. Designed for extensibility.</p>
                  </div>
                  <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Database size={16} className="text-emerald-400" />
                      <span className="font-medium text-sm">Data Layer</span>
                    </div>
                    <p className="text-xs text-gray-400">SQLAlchemy 2.x with SQLite (dev) or PostgreSQL (prod). JSON fields for flexible metadata.</p>
                  </div>
                </div>
              </div>

              {/* Key Features */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                  <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                    <Shield size={18} className="text-emerald-400" />
                    Production Ready
                  </h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Docker & Docker Compose support</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Bearer token authentication</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Health check endpoints</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Structured error responses</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />VPS deployment guide included</li>
                  </ul>
                </div>
                <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                  <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                    <GitBranch size={18} className="text-indigo-400" />
                    Extensible Design
                  </h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2"><Check size={14} className="text-indigo-400 mt-0.5 shrink-0" />pgvector-ready for semantic search</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-indigo-400 mt-0.5 shrink-0" />PostgreSQL migration path</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-indigo-400 mt-0.5 shrink-0" />Clean tool registration pattern</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-indigo-400 mt-0.5 shrink-0" />Pydantic schema validation</li>
                    <li className="flex items-start gap-2"><Check size={14} className="text-indigo-400 mt-0.5 shrink-0" />Async throughout (SQLAlchemy 2.x)</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          )}

          {/* Tools Tab */}
          {activeTab === 'tools' && (
            <motion.div
              key="tools"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="grid md:grid-cols-3 gap-6">
                {/* Tool List */}
                <div className="md:col-span-1 space-y-2">
                  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Available Tools</h3>
                  {tools.map(tool => (
                    <button
                      key={tool.name}
                      onClick={() => setSelectedTool(tool.name)}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedTool === tool.name
                          ? 'bg-indigo-600/10 border-indigo-500/50 text-white'
                          : 'bg-gray-800/30 border-gray-700/30 text-gray-300 hover:bg-gray-800/60'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-sm font-medium">{tool.name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          tool.category === 'system' ? 'bg-gray-700 text-gray-300' :
                          tool.category === 'authors' ? 'bg-blue-900/50 text-blue-300' :
                          tool.category === 'books' ? 'bg-purple-900/50 text-purple-300' :
                          'bg-emerald-900/50 text-emerald-300'
                        }`}>{tool.category}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-1">{tool.description}</p>
                    </button>
                  ))}
                </div>

                {/* Tool Detail */}
                <div className="md:col-span-2 space-y-4">
                  {selectedTool && toolExamples[selectedTool] ? (
                    <>
                      <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5">
                        <h3 className="text-lg font-bold mb-1">{selectedTool}</h3>
                        <p className="text-sm text-gray-400">{tools.find(t => t.name === selectedTool)?.description}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-1">
                          <ArrowRight size={14} /> Request
                        </h4>
                        <CodeBlock code={toolExamples[selectedTool].input} />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-1">
                          <ChevronRight size={14} /> Response
                        </h4>
                        <CodeBlock code={toolExamples[selectedTool].output} />
                      </div>
                    </>
                  ) : (
                    <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-8 text-center">
                      <p className="text-gray-400">Select a tool to see example request/response payloads.</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Data Tab */}
          {activeTab === 'data' && (
            <motion.div
              key="data"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Database size={18} className="text-emerald-400" />
                  Sample Authors ({sampleAuthors.length})
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-2 px-3 text-gray-400 font-medium">Name</th>
                        <th className="text-left py-2 px-3 text-gray-400 font-medium">Genres</th>
                        <th className="text-left py-2 px-3 text-gray-400 font-medium">Status</th>
                        <th className="text-left py-2 px-3 text-gray-400 font-medium">Books</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sampleAuthors.map(author => (
                        <tr key={author.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                          <td className="py-2.5 px-3">
                            <span className="font-medium text-white">{author.name}</span>
                            <br />
                            <span className="text-xs text-gray-500 font-mono">{author.id}</span>
                          </td>
                          <td className="py-2.5 px-3">
                            <div className="flex flex-wrap gap-1">
                              {author.genres.map(g => (
                                <span key={g} className="px-1.5 py-0.5 text-xs rounded bg-gray-700/50 text-gray-300">{g}</span>
                              ))}
                            </div>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              author.status === 'sonexial_verified' ? 'bg-indigo-900/50 text-indigo-300' :
                              author.status === 'verified_human' ? 'bg-emerald-900/50 text-emerald-300' :
                              'bg-gray-700/50 text-gray-400'
                            }`}>{author.status.replace('_', ' ')}</span>
                          </td>
                          <td className="py-2.5 px-3 text-gray-300">{author.books}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5">
                  <h4 className="font-bold mb-3 flex items-center gap-2">
                    <BookOpen size={16} className="text-purple-400" />
                    Genres Represented
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {['cyberpunk', 'space opera', 'romantasy', 'cosmic horror', 'cozy fantasy', 'literary speculative', 'grimdark', 'climate fiction', 'solarpunk', 'noir', 'techno-thriller'].map(g => (
                      <span key={g} className="px-2 py-1 text-xs rounded-md bg-gray-700/50 text-gray-300 border border-gray-600/30">{g}</span>
                    ))}
                  </div>
                </div>
                <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5">
                  <h4 className="font-bold mb-3 flex items-center gap-2">
                    <Layers size={16} className="text-amber-400" />
                    Lore Categories
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {['character', 'location', 'faction', 'item', 'timeline', 'magic_system', 'technology'].map(c => (
                      <span key={c} className="px-2 py-1 text-xs rounded-md bg-gray-700/50 text-gray-300 border border-gray-600/30">{c}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5">
                <h4 className="font-bold mb-3">Data Model</h4>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-indigo-400 font-mono text-xs mb-1">Author</p>
                    <p className="text-gray-400 text-xs">id, slug, name, pen_names, website, bio_short, bio_long, genres, tropes, themes, audience, verification_status, source_urls, timestamps</p>
                  </div>
                  <div>
                    <p className="text-purple-400 font-mono text-xs mb-1">Book</p>
                    <p className="text-gray-400 text-xs">id, author_id, title, subtitle, series_name, series_position, publication_date, asin, isbn, blurb, genres, tropes, cover_url, book_status, word_count_estimate</p>
                  </div>
                  <div>
                    <p className="text-emerald-400 font-mono text-xs mb-1">LoreEntry</p>
                    <p className="text-gray-400 text-xs">id, author_id, book_id, title, category, content, tags, canonical, spoiler_level, timestamps</p>
                  </div>
                  <div>
                    <p className="text-amber-400 font-mono text-xs mb-1">AuthorRelationship</p>
                    <p className="text-gray-400 text-xs">id, source_author_id, target_author_id, relationship_type, weight, notes, timestamps</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Setup Tab */}
          {activeTab === 'setup' && (
            <motion.div
              key="setup"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Terminal size={18} className="text-indigo-400" />
                  Local Development Setup
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-400 mb-2">1. Clone and install dependencies:</p>
                    <CodeBlock code={`cd sonexial-mcp
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-2">2. Configure environment:</p>
                    <CodeBlock code={`cp .env.example .env
# Edit .env with your settings`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-2">3. Seed the database:</p>
                    <CodeBlock code={`python -m sonexial_mcp.seed`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-2">4. Run the server:</p>
                    <CodeBlock code={`# stdio mode (for local MCP clients like Claude Desktop)
python -m sonexial_mcp.cli --transport stdio

# HTTP mode (for remote clients)
python -m sonexial_mcp.cli --transport http`} />
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Package size={18} className="text-purple-400" />
                  Docker Setup
                </h3>
                <CodeBlock code={`# Build and run
docker compose up --build

# The server starts at http://localhost:8080
# Health check: curl http://localhost:8080/healthz`} />
              </div>

              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Play size={18} className="text-emerald-400" />
                  MCP Client Configuration
                </h3>
                <p className="text-sm text-gray-400 mb-3">Add to Claude Desktop config (claude_desktop_config.json):</p>
                <CodeBlock code={`{
  "mcpServers": {
    "sonexial-authors": {
      "command": "python",
      "args": ["-m", "sonexial_mcp.cli", "--transport", "stdio"],
      "cwd": "/path/to/sonexial-mcp"
    }
  }
}`} />
                <p className="text-sm text-gray-400 mt-4 mb-3">Or for remote HTTP:</p>
                <CodeBlock code={`{
  "mcpServers": {
    "sonexial-authors": {
      "url": "https://mcp.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}`} />
              </div>

              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Shield size={18} className="text-amber-400" />
                  Testing
                </h3>
                <CodeBlock code={`# Run all tests
pytest -v

# Run specific test
pytest tests/test_tools.py -v`} />
              </div>
            </motion.div>
          )}

          {/* Deploy Tab */}
          {activeTab === 'deploy' && (
            <motion.div
              key="deploy"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Globe size={18} className="text-indigo-400" />
                  VPS Deployment (Ubuntu/Debian)
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-400 mb-2">1. Install Docker on your VPS:</p>
                    <CodeBlock code={`curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-2">2. Clone and configure:</p>
                    <CodeBlock code={`git clone <your-repo> sonexial-mcp
cd sonexial-mcp
cp .env.example .env
# Edit .env: set SONEXIAL_MCP_API_KEY, AUTH_DISABLED=false`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-2">3. Deploy:</p>
                    <CodeBlock code={`docker compose up -d --build
curl http://localhost:8080/healthz`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400 mb-2">4. Set up Caddy reverse proxy with auto-TLS:</p>
                    <CodeBlock code={`# Install Caddy, then:
sudo cp Caddyfile.example /etc/caddy/Caddyfile
# Edit domain name in Caddyfile
sudo systemctl restart caddy`} />
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Lock size={18} className="text-emerald-400" />
                  Security Checklist
                </h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Set AUTH_DISABLED=false in production</li>
                  <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Generate a strong SONEXIAL_MCP_API_KEY (openssl rand -hex 32)</li>
                  <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Use TLS via Caddy or nginx with Let's Encrypt</li>
                  <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Configure firewall (UFW) to allow only 22, 80, 443</li>
                  <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Set up database backups</li>
                  <li className="flex items-start gap-2"><Check size={14} className="text-emerald-400 mt-0.5 shrink-0" />Monitor logs for errors and suspicious activity</li>
                </ul>
              </div>

              <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Box size={18} className="text-purple-400" />
                  Environment Variables (Production)
                </h3>
                <CodeBlock code={`SONEXIAL_MCP_ENV=production
SONEXIAL_MCP_HOST=0.0.0.0
SONEXIAL_MCP_PORT=8080
DATABASE_URL=sqlite+aiosqlite:////app/data/sonexial.db
SONEXIAL_MCP_API_KEY=<your-strong-secret-key>
AUTH_DISABLED=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-client-domain.com`} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              Sonexial Author MCP v0.1.0 — Prototype by Sonexial Labs
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Python 3.11+</span>
              <span>•</span>
              <span>MCP Protocol</span>
              <span>•</span>
              <span>SQLAlchemy 2.x</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Simple GitHub icon component
function Github({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  )
}
