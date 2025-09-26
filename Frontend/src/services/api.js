// services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Utility function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }
  return await response.json();
};

// Upload resumes to Azure Blob Storage via backend
export const uploadResumes = async (files, onProgress = null) => {
  try {
    const formData = new FormData();
    
    // Add each file to form data
    files.forEach((file, index) => {
      formData.append('resumes', file);
    });

    // Add metadata
    formData.append('uploadedAt', new Date().toISOString());
    formData.append('totalFiles', files.length.toString());

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            onProgress(percentComplete);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          try {
            const errorResponse = JSON.parse(xhr.responseText);
            reject(new Error(errorResponse.message || 'Upload failed'));
          } catch {
            reject(new Error(`Upload failed with status: ${xhr.status}`));
          }
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      xhr.addEventListener('timeout', () => {
        reject(new Error('Upload timeout'));
      });

      xhr.open('POST', `${API_BASE_URL}/upload-resumes`);
      xhr.timeout = 300000; // 5 minutes timeout
      xhr.send(formData);
    });
  } catch (error) {
    throw new Error(`Upload preparation failed: ${error.message}`);
  }
};

// Process resumes using Azure OpenAI
export const processResumes = async (resumeIds, jobDescription) => {
  try {
    const response = await fetch(`${API_BASE_URL}/process-resumes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resumeIds,
        jobDescription,
        analysisType: 'comprehensive', // basic, comprehensive, detailed
        includeSkillsMatch: true,
        includeExperienceAnalysis: true,
        includeCultureFit: false
      }),
    });

    return await handleResponse(response);
  } catch (error) {
    throw new Error(`Resume processing failed: ${error.message}`);
  }
};

// Get resume details from Azure Blob Storage
export const getResumeDetails = async (resumeId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/resume/${resumeId}`, {
      method: 'GET',
    });

    return await handleResponse(response);
  } catch (error) {
    throw new Error(`Failed to get resume details: ${error.message}`);
  }
};

// Download resume from Azure Blob Storage
export const downloadResume = async (resumeId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/download-resume/${resumeId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Download failed: ${response.status}`);
    }

    // Return blob for download
    const blob = await response.blob();
    return blob;
  } catch (error) {
    throw new Error(`Resume download failed: ${error.message}`);
  }
};

// Delete resume from Azure Blob Storage
export const deleteResume = async (resumeId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/delete-resume/${resumeId}`, {
      method: 'DELETE',
    });

    return await handleResponse(response);
  } catch (error) {
    throw new Error(`Resume deletion failed: ${error.message}`);
  }
};

// Get upload statistics
export const getUploadStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/upload-stats`, {
      method: 'GET',
    });

    return await handleResponse(response);
  } catch (error) {
    throw new Error(`Failed to get upload statistics: ${error.message}`);
  }
};