import api from './api';

export const authService = {
  login: async (username, password) => {
    const response = await api.post('auth/login/', { username, password });
    if (response.data.access) {
      localStorage.setItem('token', response.data.access);
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  }
};
