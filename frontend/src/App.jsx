import { useState } from 'react'
import { Search, TrendingUp, Sparkles, Github, ExternalLink } from 'lucide-react'
import SearchBar from './components/SearchBar'
import SummaryCard from './components/SummaryCard'
import TrendingTopics from './components/TrendingTopics'
import SentimentChart from './components/SentimentChart'
import { summarizeTopic, getTrendingTopics } from './services/api'
import './App.css'

function App() {
    const [query, setQuery] = useState('')
    const [summary, setSummary] = useState(null)
    const [trending, setTrending] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleSearch = async () => {
        if (!query.trim()) return

        setLoading(true)
        setError(null)

        try {
            const result = await summarizeTopic(query, 24)
            setSummary(result)
        } catch (err) {
            setError(err.message || 'Failed to generate summary')
            console.error('Search error:', err)
        } finally {
            setLoading(false)
        }
    }

    const loadTrending = async () => {
        try {
            const topics = await getTrendingTopics(10, 24)
            setTrending(topics)
        } catch (err) {
            console.error('Failed to load trending topics:', err)
        }
    }

    // Load trending on mount
    useState(() => {
        loadTrending()
    }, [])

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <Sparkles className="w-8 h-8 text-indigo-600" />
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                    SMAART
                                </h1>
                                <p className="text-xs text-gray-600">Social Media Analytics & Real-Time Trends</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            <a
                                href="https://github.com/yourusername/SMAART"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition"
                            >
                                <Github className="w-5 h-5" />
                                <span className="hidden md:inline">GitHub</span>
                            </a>
                            <a
                                href="/docs"
                                className="flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition"
                            >
                                <ExternalLink className="w-5 h-5" />
                                <span className="hidden md:inline">API Docs</span>
                            </a>
                        </div>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="container mx-auto px-4 py-16">
                <div className="text-center mb-12 animate-fade-in">
                    <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
                        Discover What's <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Trending</span>
                    </h2>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                        AI-powered real-time summarization of social media trends and news from across the web
                    </p>
                </div>

                {/* Search Section */}
                <div className="max-w-3xl mx-auto mb-12 animate-slide-up">
                    <SearchBar
                        query={query}
                        setQuery={setQuery}
                        onSearch={handleSearch}
                        loading={loading}
                    />
                </div>

                {/* Error Message */}
                {error && (
                    <div className="max-w-3xl mx-auto mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 animate-fade-in">
                        {error}
                    </div>
                )}

                {/* Summary Results */}
                {summary && (
                    <div className="max-w-5xl mx-auto space-y-8 animate-slide-up">
                        <SummaryCard summary={summary} />

                        {summary.sentiment && (
                            <SentimentChart sentiment={summary.sentiment} />
                        )}
                    </div>
                )}

                {/* Trending Topics */}
                {!summary && trending.length > 0 && (
                    <div className="max-w-5xl mx-auto animate-fade-in">
                        <div className="flex items-center space-x-2 mb-6">
                            <TrendingUp className="w-6 h-6 text-indigo-600" />
                            <h3 className="text-2xl font-bold text-gray-900">Trending Now</h3>
                        </div>
                        <TrendingTopics topics={trending} onTopicClick={setQuery} />
                    </div>
                )}
            </section>

            {/* Footer */}
            <footer className="bg-white/80 backdrop-blur-md mt-20 py-8">
                <div className="container mx-auto px-4 text-center text-gray-600">
                    <p className="mb-2">
                        Built with ❤️ using React, FastAPI, and DistilBART
                    </p>
                    <p className="text-sm">
                        Powered by Twitter/X API and NewsAPI • Deployed on AWS & Vercel
                    </p>
                </div>
            </footer>
        </div>
    )
}

export default App
