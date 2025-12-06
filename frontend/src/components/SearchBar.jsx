import { Search, Loader2 } from 'lucide-react'

export default function SearchBar({ query, setQuery, onSearch, loading }) {
    const handleSubmit = (e) => {
        e.preventDefault()
        onSearch()
    }

    return (
        <form onSubmit={handleSubmit} className="relative">
            <div className="relative">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="What's trending? (e.g., AI developments, climate change, tech news)"
                    className="w-full px-6 py-5 pr-32 text-lg rounded-2xl border-2 border-gray-200 focus:border-indigo-500 focus:outline-none shadow-lg transition-all duration-300 hover:shadow-xl"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Analyzing...</span>
                        </>
                    ) : (
                        <>
                            <Search className="w-5 h-5" />
                            <span>Search</span>
                        </>
                    )}
                </button>
            </div>

            {/* Quick suggestions */}
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
                {['AI & Technology', 'Climate Change', 'Global Politics', 'Health & Science'].map((suggestion) => (
                    <button
                        key={suggestion}
                        type="button"
                        onClick={() => setQuery(suggestion)}
                        className="px-4 py-2 bg-white rounded-full text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 transition border border-gray-200 shadow-sm hover:shadow"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </form>
    )
}
