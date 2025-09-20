import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

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
        
        try {
            const response = await api.post('/resume/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error('Error uploading resume:', error);
            throw error;
        }
    },

    rankResumes: async (jobDescription: string, resumeIds: string[]) => {
        try {
            const response = await api.post('/resume/rank', {
                job_description: jobDescription,
                resume_ids: resumeIds,
            });
            return response.data;
        } catch (error) {
            console.error('Error ranking resumes:', error);
            throw error;
        }
    },
};