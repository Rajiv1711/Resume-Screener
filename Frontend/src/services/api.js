import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const resumeService = {
  uploadResume: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return await api.post('/api/resumes/upload', formData);
  },

  analyzeResumes: async (jobDescription: string, resumeIds: string[]) => {
    return await api.post('/api/resumes/analyze', {
      job_description: jobDescription,
      resume_ids: resumeIds,
    });
  },

  getRanking: async (analysisId: string) => {
    return await api.get(`/api/resumes/ranking/${analysisId}`);
  },
};

export default api;