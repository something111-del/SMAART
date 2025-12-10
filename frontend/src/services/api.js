import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds
})

/**
 * Summarize a topic
 * @param {string} query - Topic or keyword to summarize
 * @param {number} hours - Time window in hours
 * @param {Array<string>} sources - Optional source filters
 * @param {number} maxLength - Maximum summary length
 * @returns {Promise<Object>} Summary response
 */
export const summarizeTopic = async (query, hours = 24, sources = null, maxLength = 150) => {
    try {
        const response = await api.post('/api/v1/summarize', {
            query,
            hours,
            sources,
            max_length: maxLength,
        })
        return response.data
    } catch (error) {
        console.error('Error summarizing topic:', error)
        throw new Error(
            error.response?.data?.detail || 'Failed to generate summary. Please try again.'
        )
    }
}

/**
 * Get trending topics
 * @param {number} limit - Number of topics to fetch
 * @param {number} hours - Time window in hours
 * @returns {Promise<Array>} List of trending topics
 */
export const getTrendingTopics = async (limit = 10, hours = 24) => {
    try {
        const response = await api.get('/api/v1/trending', {
            params: { limit, hours },
        })
        return response.data
    } catch (error) {
        console.error('Error fetching trending topics:', error)
        throw new Error(
            error.response?.data?.detail || 'Failed to fetch trending topics.'
        )
    }
}

/**
 * Health check
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
    try {
        const response = await api.get('/api/v1/health')
        return response.data
    } catch (error) {
        console.error('Health check failed:', error)
        throw new Error('API is not responding')
    }
}

export default api
