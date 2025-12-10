export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Credentials', true)
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT')
    res.setHeader(
        'Access-Control-Allow-Headers',
        'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
    )

    if (req.method === 'OPTIONS') {
        res.status(200).end()
        return
    }

    const BACKEND_URL = 'http://3.145.166.181:30000'

    try {
        const path = req.url.replace('/api/proxy', '')
        const url = `${BACKEND_URL}${path}`

        const response = await fetch(url, {
            method: req.method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
        })

        const data = await response.json()
        res.status(response.status).json(data)
    } catch (error) {
        console.error('Proxy error:', error)
        res.status(500).json({ error: 'Proxy request failed', detail: error.message })
    }
}
