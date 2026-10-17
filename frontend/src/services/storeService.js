import { request } from './api';

export const storeService = {
  getPackages: async () => {
    return await request('/store/packages', {
      method: 'GET'
    });
  },

  createCheckout: async (packageId, idempotencyKey = null) => {
    return await request('/store/checkout', {
      method: 'POST',
      body: JSON.stringify({ packageId, idempotencyKey })
    });
  },

  confirmPayment: async (payload) => {
    return await request('/store/confirm-payment', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  getPurchases: async () => {
    return await request('/store/purchases', {
      method: 'GET'
    });
  },

  refundPurchase: async (purchaseId, reason = '') => {
    return await request(`/store/purchases/${purchaseId}/refund`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
  },

  getMissions: async () => {
    return await request('/store/missions', {
      method: 'GET'
    });
  },

  getMissionDetail: async (id) => {
    return await request(`/store/missions/${id}`, {
      method: 'GET'
    });
  },

  claimReward: async (id) => {
    return await request(`/store/missions/${id}/claim`, {
      method: 'POST'
    });
  },

  getRewardsSummary: async () => {
    return await request('/store/rewards', {
      method: 'GET'
    });
  }
};
