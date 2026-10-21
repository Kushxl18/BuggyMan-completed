import { request } from './api';

export const challengeService = {
  getChallenges: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.difficulty && params.difficulty !== 'All') query.append('difficulty', params.difficulty);
    if (params.technology && params.technology !== 'All') query.append('technology', params.technology);
    if (params.category && params.category !== 'All') query.append('category', params.category);
    if (params.arena && params.arena !== 'All') query.append('arena', params.arena);
    if (params.search) query.append('search', params.search);
    if (params.personalized !== undefined) query.append('personalized', params.personalized);
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
  },

  getCareerInsights: async (roleId = null) => {
    const query = roleId ? `?role=${encodeURIComponent(roleId)}` : '';
    return await request(`/career-insights${query}`, {
      method: 'GET'
    });
  },

  getBugBytesSummary: async () => {
    return await request('/bugbytes', {
      method: 'GET'
    });
  },

  getBugBytesHistory: async () => {
    return await request('/bugbytes/history', {
      method: 'GET'
    });
  },

  getUnlockedHints: async (challengeId) => {
    return await request(`/challenges/${challengeId}/hints`, {
      method: 'GET'
    });
  },

  requestAIHint: async (challengeId, level, payload = {}) => {
    return await request(`/challenges/${challengeId}/hints`, {
      method: 'POST',
      body: JSON.stringify({ level, ...payload })
    });
  },

  // PvP Battle APIs
  createBattle: async (params = {}) => {
    return await request('/pvp/create', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  },

  joinBattle: async (roomCode) => {
    return await request('/pvp/join', {
      method: 'POST',
      body: JSON.stringify({ roomCode })
    });
  },

  quickMatch: async (params = {}) => {
    return await request('/pvp/quick-match', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  },

  getBattleStatus: async (battleId) => {
    return await request(`/pvp/${battleId}/status`, {
      method: 'GET'
    });
  },

  startBattle: async (battleId) => {
    return await request(`/pvp/${battleId}/start`, {
      method: 'POST'
    });
  },

  updateBattleProgress: async (battleId, progress) => {
    return await request(`/pvp/${battleId}/progress`, {
      method: 'POST',
      body: JSON.stringify(progress)
    });
  },

  submitBattleSolution: async (battleId, code, files = []) => {
    return await request(`/pvp/${battleId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ code, files })
    });
  },

  cancelBattle: async (battleId) => {
    return await request(`/pvp/${battleId}/cancel`, {
      method: 'POST'
    });
  },

  matchBot: async (battleId) => {
    return await request(`/pvp/${battleId}/match-bot`, {
      method: 'POST'
    });
  },

  getPvPHistory: async () => {
    return await request('/pvp/history', {
      method: 'GET'
    });
  },

  // Engagement & Reactions
  getEngagement: async (challengeId) => {
    return await request(`/challenges/${challengeId}/engagement`, {
      method: 'GET'
    });
  },

  toggleReaction: async (challengeId, reaction) => {
    return await request(`/challenges/${challengeId}/reaction`, {
      method: 'POST',
      body: JSON.stringify({ reaction })
    });
  },

  toggleStar: async (challengeId) => {
    return await request(`/challenges/${challengeId}/star`, {
      method: 'POST'
    });
  },

  getSolution: async (challengeId) => {
    return await request(`/challenges/${challengeId}/solution`, {
      method: 'GET'
    });
  },

  getSubmissions: async (challengeId) => {
    return await request(`/challenges/${challengeId}/submissions`, {
      method: 'GET'
    });
  }
};

