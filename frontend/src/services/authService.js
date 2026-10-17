import { request } from './api';

const setToken = (token, rememberMe = true) => {
  if (rememberMe) {
    localStorage.setItem('token', token);
    sessionStorage.removeItem('token');
  } else {
    sessionStorage.setItem('token', token);
    localStorage.removeItem('token');
  }
};

const clearToken = () => {
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');
};

export const authService = {
  login: async (email, password, rememberMe = true) => {
    const response = await request('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (response.token) {
      setToken(response.token, rememberMe);
    }
    return response;
  },

  register: async (payload, rememberMe = true) => {
    const response = await request('/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (response.token) {
      setToken(response.token, rememberMe);
    }
    return response;
  },

  getCurrentUser: async () => {
    return await request('/profile', {
      method: 'GET'
    });
  },

  checkAvailability: async (username, email) => {
    return await request('/check-availability', {
      method: 'POST',
      body: JSON.stringify({ username, email })
    });
  },

  updateProfile: async (profileData) => {
    return await request('/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  },

  forgotPasswordRequest: async (email) => {
    return await request('/forgot-password/request', {
      method: 'POST',
      body: JSON.stringify({ email })
    });
  },

  forgotPasswordReset: async (email, otp, password) => {
    return await request('/forgot-password/reset', {
      method: 'POST',
      body: JSON.stringify({ email, otp, password })
    });
  },

  logout: async () => {
    try {
      await request('/logout', { method: 'POST' });
    } catch (error) {
      // ignore logout endpoint failures; clear client session regardless
    }
    clearToken();
  },

  oauthLogin: async (payload, rememberMe = true) => {
    const response = await request('/auth/oauth', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (response.token) {
      setToken(response.token, rememberMe);
    }
    return response;
  },

  getOAuthConfig: async () => {
    return await request('/auth/oauth/config', {
      method: 'GET'
    });
  },

  handleOAuthCallback: async (payload, rememberMe = true) => {
    const response = await request('/auth/oauth/callback', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (response.token) {
      setToken(response.token, rememberMe);
    }
    return response;
  },

  disconnectOAuth: async () => {
    return await request('/auth/oauth/disconnect', {
      method: 'POST'
    });
  }
};
