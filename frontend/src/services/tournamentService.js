import api from './api';

export const tournamentService = {
  getTournaments: async () => {
    const response = await api.get('tournaments/');
    return response.data;
  }
};
