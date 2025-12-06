import { TrendingUp, MessageCircle } from 'lucide-react'

export default function TrendingTopics({ topics, onTopicClick }) {
    const getSentimentEmoji = (sentiment) => {
        if (sentiment > 0.6) return '😊'
        if (sentiment < 0.4) return '😟'
        return '😐'
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topics.map((topic, index) => (
                <button
                    key={index}
                    onClick={() => onTopicClick(topic.topic)}
                    className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 text-left border border-gray-100 hover:border-indigo-300 group"
                >
                    <div className="flex items-start justify-between mb-3">
                        <h4 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition">
                            {topic.topic}
                        </h4>
                        <span className="text-2xl">{getSentimentEmoji(topic.sentiment)}</span>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span className="flex items-center space-x-1">
                            <MessageCircle className="w-4 h-4" />
                            <span>{topic.count} mentions</span>
                        </span>
                        <span className="flex items-center space-x-1">
                            <TrendingUp className="w-4 h-4" />
                            <span>{(topic.sentiment * 100).toFixed(0)}%</span>
                        </span>
                    </div>

                    {topic.sources && topic.sources.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-1">
                            {topic.sources.map((source, idx) => (
                                <span
                                    key={idx}
                                    className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs capitalize"
                                >
                                    {source}
                                </span>
                            ))}
                        </div>
                    )}
                </button>
            ))}
        </div>
    )
}
