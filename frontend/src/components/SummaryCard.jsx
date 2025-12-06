import { Clock, Hash, TrendingUp, ExternalLink } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function SummaryCard({ summary }) {
    const getSentimentColor = (sentiment) => {
        if (sentiment.positive > 0.6) return 'text-green-600 bg-green-50'
        if (sentiment.negative > 0.4) return 'text-red-600 bg-red-50'
        return 'text-yellow-600 bg-yellow-50'
    }

    const getSentimentLabel = (sentiment) => {
        if (sentiment.positive > 0.6) return 'Positive'
        if (sentiment.negative > 0.4) return 'Negative'
        return 'Neutral'
    }

    return (
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
                <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        Summary: {summary.query}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center space-x-1">
                            <Clock className="w-4 h-4" />
                            <span>{formatDistanceToNow(new Date(summary.generated_at), { addSuffix: true })}</span>
                        </span>
                        <span>•</span>
                        <span>{summary.processing_time_ms}ms</span>
                        <span>•</span>
                        <span className="flex items-center space-x-1">
                            <TrendingUp className="w-4 h-4" />
                            <span>{summary.confidence * 100}% confidence</span>
                        </span>
                    </div>
                </div>

                <div className={`px-4 py-2 rounded-full font-semibold ${getSentimentColor(summary.sentiment)}`}>
                    {getSentimentLabel(summary.sentiment)}
                </div>
            </div>

            {/* Summary Text */}
            <div className="mb-6">
                <p className="text-lg text-gray-700 leading-relaxed">
                    {summary.summary}
                </p>
            </div>

            {/* Entities */}
            {summary.entities && summary.entities.length > 0 && (
                <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-600 mb-3 flex items-center space-x-2">
                        <Hash className="w-4 h-4" />
                        <span>Key Topics</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        {summary.entities.map((entity, index) => (
                            <span
                                key={index}
                                className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium"
                            >
                                {entity}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Sources */}
            {summary.sources && (
                <div className="pt-6 border-t border-gray-100">
                    <h4 className="text-sm font-semibold text-gray-600 mb-3">Data Sources</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(summary.sources).map(([source, count]) => (
                            <div key={source} className="bg-gray-50 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-indigo-600">{count}</div>
                                <div className="text-sm text-gray-600 capitalize">{source}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
