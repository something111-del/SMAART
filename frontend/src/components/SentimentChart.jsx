import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

export default function SentimentChart({ sentiment }) {
    const data = [
        { name: 'Positive', value: sentiment.positive * 100, color: '#10b981' },
        { name: 'Neutral', value: sentiment.neutral * 100, color: '#f59e0b' },
        { name: 'Negative', value: sentiment.negative * 100, color: '#ef4444' },
    ]

    return (
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Sentiment Analysis</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Chart */}
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Stats */}
                <div className="flex flex-col justify-center space-y-4">
                    {data.map((item) => (
                        <div key={item.name} className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div
                                    className="w-4 h-4 rounded-full"
                                    style={{ backgroundColor: item.color }}
                                />
                                <span className="font-medium text-gray-700">{item.name}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="w-32 bg-gray-200 rounded-full h-2">
                                    <div
                                        className="h-2 rounded-full transition-all duration-500"
                                        style={{
                                            width: `${item.value}%`,
                                            backgroundColor: item.color,
                                        }}
                                    />
                                </div>
                                <span className="text-sm font-semibold text-gray-600 w-12 text-right">
                                    {item.value.toFixed(1)}%
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
