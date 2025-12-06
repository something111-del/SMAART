import { useState, useEffect } from 'react'
import { X, Activity, Server, Database, Cpu, Terminal } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { healthCheck } from '../services/api'

// Mock Data Generator
const generateData = () => {
    const data = []
    for (let i = 0; i < 20; i++) {
        data.push({
            time: `${i}s`,
            cpu: 30 + Math.random() * 20,
            memory: 40 + Math.random() * 10,
            latency: 100 + Math.random() * 50
        })
    }
    return data
}

const mockLogs = [
    "[INFO] Initializing DistilBART pipeline...",
    "[INFO] Connected to Redis (Cache Miss)",
    "[INFO] Fetching trending topics from Twitter API...",
    "[INFO] NLP Processor: Entities extracted (Person: 3, Org: 2)",
    "[SUCCESS] Summarization complete (Processing time: 142ms)",
    "[INFO] Serving request /api/v1/summarize",
    "[WARN] High memory usage detected in Worker-1",
    "[INFO] Auto-scaling trigger: CPU > 60%",
    "[INFO] Database connection pool: 5/10 active",
]

export default function MonitoringModal({ onClose }) {
    const [status, setStatus] = useState('loading')
    const [data, setData] = useState(generateData())
    const [logs, setLogs] = useState(mockLogs)
    const [activeTab, setActiveTab] = useState('metrics')

    useEffect(() => {
        checkHealth()
        const interval = setInterval(() => {
            // Update charts with live mock data
            setData(prev => {
                const newData = [...prev.slice(1), {
                    time: 'now',
                    cpu: 30 + Math.random() * 30,
                    memory: 45 + Math.random() * 10,
                    latency: 90 + Math.random() * 100
                }]
                return newData
            })
            // Add random log
            if (Math.random() > 0.7) {
                const newLog = `[INFO] Request processed ID:${Math.floor(Math.random() * 10000)} - ${Math.floor(Math.random() * 200)}ms`
                setLogs(prev => [...prev.slice(1), newLog])
            }
        }, 1000)

        return () => clearInterval(interval)
    }, [])

    const checkHealth = async () => {
        try {
            await healthCheck()
            setStatus('healthy')
        } catch (e) {
            setStatus('degraded')
        }
    }

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="w-full max-w-5xl bg-slate-900 rounded-xl shadow-2xl overflow-hidden border border-slate-700 text-slate-100 flex flex-col h-[80vh]">

                {/* Header */}
                <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-950">
                    <div className="flex items-center space-x-3">
                        <Activity className="text-emerald-400 w-6 h-6" />
                        <h2 className="text-lg font-bold">System Monitor</h2>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${status === 'healthy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'} border border-current`}>
                            {status === 'healthy' ? 'OPERATIONAL' : 'DEGRADED'}
                        </span>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-lg transition text-slate-400 hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-slate-700 bg-slate-900/50">
                    <button
                        onClick={() => setActiveTab('metrics')}
                        className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'metrics' ? 'text-blue-400 border-b-2 border-blue-400 bg-slate-800/50' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                        <div className="flex items-center space-x-2">
                            <Activity className="w-4 h-4" />
                            <span>Grafana Metrics</span>
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab('logs')}
                        className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'logs' ? 'text-amber-400 border-b-2 border-amber-400 bg-slate-800/50' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                        <div className="flex items-center space-x-2">
                            <Terminal className="w-4 h-4" />
                            <span>ELK / Loki Logs</span>
                        </div>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 bg-slate-900">
                    {activeTab === 'metrics' ? (
                        <div className="space-y-6">
                            {/* Key Metrics Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                <MetricCard icon={<Server />} label="API Instances" value="2 / 2" sub="Healthy" color="text-emerald-400" />
                                <MetricCard icon={<Cpu />} label="CPU Usage" value={Math.floor(data[data.length - 1].cpu) + "%"} sub="t3.micro" color="text-blue-400" />
                                <MetricCard icon={<Database />} label="Redis Cache" value="98%" sub="Hit Rate" color="text-purple-400" />
                                <MetricCard icon={<Activity />} label="Avg Latency" value={Math.floor(data[data.length - 1].latency) + "ms"} sub="P95" color="text-amber-400" />
                            </div>

                            {/* Charts */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                    <h3 className="text-sm font-semibold text-slate-400 mb-4">CPU & Memory Usage</h3>
                                    <div className="h-48">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={data}>
                                                <defs>
                                                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                                <XAxis dataKey="time" hide />
                                                <YAxis stroke="#475569" fontSize={12} />
                                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                                <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" />
                                                <Area type="monotone" dataKey="memory" stroke="#8b5cf6" fillOpacity={0} strokeDasharray="3 3" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                                    <h3 className="text-sm font-semibold text-slate-400 mb-4">API Latency (ms)</h3>
                                    <div className="h-48">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={data}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                                <XAxis dataKey="time" hide />
                                                <YAxis stroke="#475569" fontSize={12} />
                                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                                <Line type="monotone" dataKey="latency" stroke="#f59e0b" strokeWidth={2} dot={false} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-black/50 p-4 rounded-lg font-mono text-sm h-full overflow-hidden flex flex-col border border-slate-800">
                            <div className="flex-1 overflow-y-auto space-y-1 custom-scrollbar">
                                {logs.map((log, i) => (
                                    <div key={i} className="flex space-x-2">
                                        <span className="text-slate-500">{new Date().toLocaleTimeString()}</span>
                                        <span className={log.includes("ERROR") ? "text-red-400" : log.includes("WARN") ? "text-amber-400" : log.includes("SUCCESS") ? "text-emerald-400" : "text-slate-300"}>
                                            {log}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function MetricCard({ icon, label, value, sub, color }) {
    return (
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
            <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">{label}</span>
                <span className={color}>{icon}</span>
            </div>
            <div className="text-2xl font-bold">{value}</div>
            <div className="text-xs text-slate-500 mt-1">{sub}</div>
        </div>
    )
}
