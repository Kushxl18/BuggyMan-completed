import { request } from './api';

export const challengeService = {
  getChallenges: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.difficulty && params.difficulty !== 'All') query.append('difficulty', params.difficulty);
    if (params.technology && params.technology !== 'All') query.append('technology', params.technology);
    if (params.category && params.category !== 'All') query.append('category', params.category);
    if (params.arena && params.arena !== 'All') query.append('arena', params.arena);
    if (params.search) query.append('search', params.search);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return await request(`/challenges${queryString}`, {
      method: 'GET'
    });
  },

  getChallengeById: async (id) => {
    return await request(`/challenges/${id}`, {
      method: 'GET'
    });
  },

  runChallenge: async (id, code, files = []) => {
    return await request(`/challenges/${id}/run`, {
      method: 'POST',
      body: JSON.stringify({ code, files })
    });
  },

  submitChallenge: async (id, code, files = []) => {
    return await request(`/challenges/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ code, files })
    });
  },

  getHint: async (id, payload = {}) => {
    return await request(`/challenges/${id}/hint`, {
      method: 'POST',
      body: JSON.stringify({
        code: payload.code || '',
        files: payload.files || [],
        previousHints: payload.previousHints || [],
        testResults: payload.testResults || [],
        level: payload.level
      })
    });
  },

  getFeedback: async (id, payload = {}) => {
    return await request(`/challenges/${id}/feedback`, {
      method: 'POST',
      body: JSON.stringify({
        code: payload.code || '',
        files: payload.files || [],
        testResults: payload.testResults || [],
        stdout: payload.stdout || '',
        stderr: payload.stderr || '',
        error: payload.error || null
      })
    });
  },

  explainSolution: async (id, payload = {}) => {
    return await request(`/challenges/${id}/explain`, {
      method: 'POST',
      body: JSON.stringify({
        submittedCode: payload.submittedCode || payload.code || '',
        files: payload.files || []
      })
    });
  },

  injectBug: async (payload = {}) => {
    return await request('/challenges/inject-bug', {
      method: 'POST',
      body: JSON.stringify({
        code: payload.code || '',
        bugType: payload.bugType || 'logic',
        technology: payload.technology || 'React'
      })
    });
  },

  getAIInsights: async () => {
    return await request('/analytics/ai-insights', {
      method: 'GET'
    });
  },

  getRecommendations: async (limit = 5) => {
    return await request(`/challenges/recommendations?limit=${limit}`, {
      method: 'GET'
    });
  },

  getLearningPath: async () => {
    return await request('/challenges/learning-path', {
      method: 'GET'
    });
  },

  getUserSubmissions: async (challengeId = null) => {
    const query = challengeId ? `?challenge=${challengeId}` : '';
    return await request(`/submissions${query}`, {
      method: 'GET'
    });
  },

  getSubmissionById: async (id) => {
    return await request(`/submissions/${id}`, {
      method: 'GET'
    });
  },

  getChallengeSubmissions: async (challengeId) => {
    return await request(`/challenges/${challengeId}/submissions`, {
      method: 'GET'
    });
  },

  getAnalytics: async () => {
    return await request('/analytics', {
      method: 'GET'
    });
  },

  getLeaderboard: async () => {
    return await request('/leaderboard', {
      method: 'GET'
    });
  },

  getNotifications: async () => {
    return await request('/notifications', {
      method: 'GET'
    });
  },

  markNotificationAsRead: async (id) => {
    return await request(`/notifications/${id}/read`, {
      method: 'POST'
    });
  },

  getAdminStats: async () => {
    return await request('/admin/stats', {
      method: 'GET'
    });
  },

  createChallenge: async (challengeData) => {
    return await request('/admin/challenges', {
      method: 'POST',
      body: JSON.stringify(challengeData)
    });
  },

  generateChallenge: async (params = {}) => {
    return await request('/challenges/generate', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  },

  submitReport: async (challengeId, reportData = {}) => {
    return await request(`/challenges/${challengeId}/report`, {
      method: 'POST',
      body: JSON.stringify(reportData)
    });
  }
};

