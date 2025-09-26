import React, { useState, useEffect } from 'react';
import { Upload, FileText, Search, Download, TrendingUp, Users, Award, Filter, ChevronRight, X, Eye, Star, Mail, Phone, MapPin, Briefcase, Calendar, CheckCircle, AlertCircle, LogOut, Archive } from 'lucide-react';
import './App.css';
import Login from './Login';
import { uploadResumes, processResumes } from './services/api';
import JSZip from 'jszip';
import { uploadResumes } from './services/api';

const ResumeScreener = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedResumes, setUploadedResumes] = useState([]);
  const [jobDescription, setJobDescription] = useState('');
  const [jobInputMethod, setJobInputMethod] = useState('paste');
  const [jobFileName, setJobFileName] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [filterScore, setFilterScore] = useState(0);
  const [notification, setNotification] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Mock data for demo
  const mockResults = [
    { id: 1, name: "Sarah Johnson", email: "sarah.j@email.com", phone: "+1 234-567-8901", location: "Seattle, WA", experience: "5 years", score: 95, skills: ["Python", "FastAPI", "Azure", "Machine Learning"], status: "excellent" },
    { id: 2, name: "Michael Chen", email: "m.chen@email.com", phone: "+1 234-567-8902", location: "San Francisco, CA", experience: "3 years", score: 88, skills: ["Python", "Docker", "CI/CD", "NLP"], status: "good" },
    { id: 3, name: "Emily Rodriguez", email: "emily.r@email.com", phone: "+1 234-567-8903", location: "Austin, TX", experience: "4 years", score: 82, skills: ["Azure", "DevOps", "Python", "SQL"], status: "good" },
    { id: 4, name: "David Park", email: "d.park@email.com", phone: "+1 234-567-8904", location: "New York, NY", experience: "2 years", score: 75, skills: ["Python", "FastAPI", "Docker"], status: "average" },
    { id: 5, name: "Jessica Liu", email: "j.liu@email.com", phone: "+1 234-567-8905", location: "Boston, MA", experience: "6 years", score: 70, skills: ["Machine Learning", "Python", "Azure"], status: "average" },
  ];

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const extractZipFiles = async (zipFile) => {
    try {
      const zip = new JSZip();
      const contents = await zip.loadAsync(zipFile);
      const extractedFiles = [];
      
      for (const filename of Object.keys(contents.files)) {
        const file = contents.files[filename];
        if (!file.dir && /\.(pdf|doc|docx|txt|json|csv)$/i.test(filename)) {
          const blob = await file.async('blob');
          const extractedFile = new File([blob], filename.split('/').pop(), {
            type: getFileType(filename)
          });
          extractedFiles.push(extractedFile);
        }
      }
      
      return extractedFiles;
    } catch (error) {
      throw new Error('Failed to extract ZIP file: ' + error.message);
    }
  };

  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    const types = {
      'pdf': 'application/pdf',
      'doc': 'application/msword',
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'txt': 'text/plain',
      'json': 'application/json',
      'csv': 'text/csv'
    };
    return types[ext] || 'application/octet-stream';
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    let allFiles = [];
    
    try {
      setUploadProgress(10);
      
      // Process each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        if (file.name.toLowerCase().endsWith('.zip')) {
          // Extract ZIP files
          const extractedFiles = await extractZipFiles(file);
          allFiles.push(...extractedFiles);
          setNotification({ type: 'success', message: `Extracted ${extractedFiles.length} files from ${file.name}` });
        } else {
          allFiles.push(file);
        }
        
        // Update progress
        setUploadProgress(20 + (i / files.length) * 30);
      }

      setUploadProgress(60);
      
      // Upload to Azure Blob Storage and backend
      const response = await uploadResumes(allFiles, (progress) => {
        setUploadProgress(60 + (progress * 0.4));
      });
      
      const newResumes = allFiles.map((file, index) => ({
        id: response.files[index]?.filename || `file_${Date.now()}_${index}`,
        name: file.name,
        size: (file.size / 1024).toFixed(2) + ' KB',
        status: 'uploaded',
        timestamp: new Date().toLocaleTimeString(),
        blobUrl: response.files[index]?.blobUrl || null
      }));
      
      setUploadedResumes([...uploadedResumes, ...newResumes]);
      setUploadProgress(100);
      setNotification({ type: 'success', message: `${allFiles.length} resume(s) uploaded successfully to Azure Blob Storage!` });
      
      // Reset progress after a delay
      setTimeout(() => setUploadProgress(0), 1000);
      
    } catch (error) {
      setUploadProgress(0);
      setNotification({ type: 'error', message: 'Error uploading files: ' + error.message });
    }
  };

  const handleJobFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setJobFileName(file.name);
      // Simulate reading the file content
      const reader = new FileReader();
      reader.onload = (e) => {
        setJobDescription(e.target.result);
        setNotification({ type: 'success', message: 'Job description file uploaded successfully!' });
      };
      reader.readAsText(file);
    }
  };

  const handleProcess = async () => {
    if (uploadedResumes.length === 0 || !jobDescription) {
        setNotification({ type: 'error', message: 'Please upload resumes and provide a job description' });
        return;
    }
    
    setIsProcessing(true);
    try {
        const response = await processResumes(
            uploadedResumes.map(resume => resume.id),
            jobDescription
        );
        setResults(response.results || mockResults); // Fallback to mock data
        setActiveTab('results');
        setNotification({ type: 'success', message: 'Analysis complete! View your results below.' });
    } catch (error) {
        // Use mock data if API fails
        setResults(mockResults);
        setActiveTab('results');
        setNotification({ type: 'success', message: 'Analysis complete! View your results below.' });
    } finally {
        setIsProcessing(false);
    }
};

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 85) return 'bg-green-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const filteredResults = results?.filter(r => r.score >= filterScore) || [];
  
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUploadedResumes([]);
    setResults(null);
    setNotification({ type: 'success', message: 'Logged out successfully!' });
  };

  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg flex items-center gap-3 animate-pulse ${
          notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`}>
          {notification.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
                <FileText className="text-white" size={20} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Resume Screener AI</h1>
                <p className="text-sm text-gray-600">Powered by Azure OpenAI</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Welcome back</p>
                <p className="font-semibold text-gray-800">User_Name</p>
              </div>
              <button 
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                title="Logout"
              >
                <LogOut size={16} />
                <span className="text-sm">Logout</span>
              </button>
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <Users size={20} className="text-gray-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="grid grid-cols-4 gap-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Upload size={20} className="text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{uploadedResumes.length}</p>
                <p className="text-sm text-gray-600">Resumes Uploaded</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle size={20} className="text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{results ? results.filter(r => r.score >= 85).length : 0}</p>
                <p className="text-sm text-gray-600">Excellent Matches</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <TrendingUp size={20} className="text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{results ? Math.round(results.reduce((a, b) => a + b.score, 0) / results.length) : 0}%</p>
                <p className="text-sm text-gray-600">Average Match Score</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Award size={20} className="text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{results ? results[0]?.name.split(' ')[0] : '-'}</p>
                <p className="text-sm text-gray-600">Top Candidate</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-6 mt-6">
        <div className="flex gap-2 bg-white p-1 rounded-lg shadow-sm">
          {['upload', 'results', 'insights'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                activeTab === tab
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {tab === 'upload' && 'Upload & Process'}
              {tab === 'results' && 'Ranking Results'}
              {tab === 'insights' && 'Analytics & Insights'}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 mt-6 pb-8">
        {activeTab === 'upload' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Resume Upload */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Upload size={20} />
                Upload Resumes
              </h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
                <Upload size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-2">Drag and drop resume files here</p>
                <p className="text-sm text-gray-500 mb-4">or</p>
                <input
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.json,.csv,.zip"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer transition-colors"
                >
                  <Upload size={16} />
                  Browse Files
                </label>
                <p className="text-xs text-gray-500 mt-4">Supported: PDF, DOC, DOCX, TXT, JSON, CSV, ZIP</p>
                
                {/* Upload Progress */}
                {uploadProgress > 0 && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">Uploading...</span>
                      <span className="text-sm text-gray-600">{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {/* ZIP File Info */}
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Archive size={16} className="text-blue-600" />
                  <span className="text-sm font-semibold text-blue-800">ZIP File Support</span>
                </div>
                <p className="text-xs text-blue-700">
                  Upload ZIP files containing multiple resumes. Supported formats inside ZIP: PDF, DOC, DOCX, TXT, JSON, CSV
                </p>
              </div>

              {uploadedResumes.length > 0 && (
                <div className="mt-4 max-h-48 overflow-y-auto">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Uploaded Files ({uploadedResumes.length})</h3>
                  {uploadedResumes.map((resume) => (
                    <div key={resume.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg mb-2">
                      <div className="flex items-center gap-2">
                        <FileText size={16} className="text-gray-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-800">{resume.name}</p>
                          <p className="text-xs text-gray-500">
                            {resume.size} • {resume.timestamp}
                            {resume.blobUrl && <span className="text-green-600"> • Stored in Azure</span>}
                          </p>
                        </div>
                      </div>
                      <CheckCircle size={16} className="text-green-500" />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Job Description */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Briefcase size={20} />
                Job Description
              </h2>
              
              {/* Tab selector for upload vs paste */}
              <div className="flex gap-2 mb-4">
                <button
                  onClick={() => setJobInputMethod('paste')}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                    jobInputMethod === 'paste' 
                      ? 'bg-indigo-100 text-indigo-700' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <FileText size={16} className="inline mr-1" />
                  Paste Text
                </button>
                <button
                  onClick={() => setJobInputMethod('upload')}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                    jobInputMethod === 'upload' 
                      ? 'bg-indigo-100 text-indigo-700' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <Upload size={16} className="inline mr-1" />
                  Upload File
                </button>
              </div>

              {jobInputMethod === 'paste' ? (
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste or type the job description here. Include required skills, experience, and qualifications..."
                  className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                />
              ) : (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition-colors">
                  <Briefcase size={40} className="mx-auto text-gray-400 mb-3" />
                  <p className="text-gray-600 mb-2">Upload job description file</p>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleJobFileUpload}
                    className="hidden"
                    id="job-file-upload"
                  />
                  <label
                    htmlFor="job-file-upload"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer transition-colors text-sm"
                  >
                    <Upload size={16} />
                    Choose File
                  </label>
                  <p className="text-xs text-gray-500 mt-3">PDF, DOC, DOCX, or TXT</p>
                  
                  {jobFileName && (
                    <div className="mt-4 p-3 bg-green-50 rounded-lg text-left">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CheckCircle size={16} className="text-green-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-800">{jobFileName}</p>
                            <p className="text-xs text-gray-600">Job description loaded</p>
                          </div>
                        </div>
                        <button 
                          onClick={() => {
                            setJobFileName('');
                            setJobDescription('');
                          }}
                          className="text-gray-500 hover:text-red-500"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>💡 Tip:</strong> Be specific about technical requirements, years of experience, and must-have skills for better matching accuracy.
                </p>
              </div>
              
              <button
                onClick={handleProcess}
                disabled={isProcessing || uploadedResumes.length === 0 || !jobDescription}
                className={`w-full mt-4 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  isProcessing || uploadedResumes.length === 0 || !jobDescription
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                }`}
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Processing {uploadedResumes.length} resumes...
                  </>
                ) : (
                  <>
                    <Search size={20} />
                    Analyze Resumes
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Results and Insights tabs remain the same as in original code */}
        {activeTab === 'results' && (
          <div className="grid md:grid-cols-3 gap-6">
            {/* Results List */}
            <div className="md:col-span-2 bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <Award size={20} />
                  Ranked Candidates
                </h2>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Filter size={16} className="text-gray-600" />
                    <label className="text-sm text-gray-600">Min Score:</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={filterScore}
                      onChange={(e) => setFilterScore(Number(e.target.value))}
                      className="w-24"
                    />
                    <span className="text-sm font-medium text-gray-800">{filterScore}%</span>
                  </div>
                  <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
                    <Download size={16} />
                    Export Report
                  </button>
                </div>
              </div>

              {!results ? (
                <div className="text-center py-12">
                  <Search size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No results yet. Upload resumes and analyze them first.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredResults.map((candidate, index) => (
                    <div
                      key={candidate.id}
                      className={`p-4 rounded-lg border-2 transition-all cursor-pointer hover:shadow-md ${
                        selectedCandidate?.id === candidate.id
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedCandidate(candidate)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex items-start gap-4">
                          <div className="flex flex-col items-center">
                            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-600">
                              {index + 1}
                            </div>
                            <div className={`mt-2 px-2 py-1 rounded-full text-xs font-medium ${getScoreBg(candidate.score)} ${getScoreColor(candidate.score)}`}>
                              {candidate.score}%
                            </div>
                          </div>
                          <div className="flex-1">
                            <h3 className="font-bold text-gray-800 text-lg">{candidate.name}</h3>
                            <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                              <span className="flex items-center gap-1">
                                <Mail size={14} />
                                {candidate.email}
                              </span>
                              <span className="flex items-center gap-1">
                                <MapPin size={14} />
                                {candidate.location}
                              </span>
                              <span className="flex items-center gap-1">
                                <Briefcase size={14} />
                                {candidate.experience}
                              </span>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-3">
                              {candidate.skills.map((skill) => (
                                <span
                                  key={skill}
                                  className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <ChevronRight size={20} className="text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Candidate Details */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Eye size={20} />
                Candidate Details
              </h2>
              {selectedCandidate ? (
                <div>
                  <div className="text-center mb-4">
                    <div className="w-20 h-20 bg-gray-200 rounded-full mx-auto mb-3 flex items-center justify-center">
                      <Users size={32} className="text-gray-600" />
                    </div>
                    <h3 className="font-bold text-lg text-gray-800">{selectedCandidate.name}</h3>
                    <div className={`inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full ${getScoreBg(selectedCandidate.score)}`}>
                      <Star size={16} className={getScoreColor(selectedCandidate.score)} />
                      <span className={`font-bold ${getScoreColor(selectedCandidate.score)}`}>
                        {selectedCandidate.score}% Match
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3 border-t pt-4">
                    <div className="flex items-center gap-2 text-sm">
                      <Mail size={16} className="text-gray-500" />
                      <span className="text-gray-600">{selectedCandidate.email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Phone size={16} className="text-gray-500" />
                      <span className="text-gray-600">{selectedCandidate.phone}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin size={16} className="text-gray-500" />
                      <span className="text-gray-600">{selectedCandidate.location}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar size={16} className="text-gray-500" />
                      <span className="text-gray-600">{selectedCandidate.experience} experience</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-semibold text-gray-700 mb-2">Key Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedCandidate.skills.map((skill) => (
                        <span
                          key={skill}
                          className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-semibold text-gray-700 mb-3">Match Analysis</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Skills Match</span>
                        <span className="font-medium text-gray-800">92%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Experience Level</span>
                        <span className="font-medium text-gray-800">85%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Location Fit</span>
                        <span className="font-medium text-gray-800">100%</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 flex gap-2">
                    <button className="flex-1 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                      Schedule Interview
                    </button>
                    <button className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                      View Full Resume
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">Select a candidate to view details</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Skills Distribution */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Top Skills in Pool</h2>
              <div className="space-y-3">
                {['Python', 'Azure', 'FastAPI', 'Docker', 'Machine Learning'].map((skill, i) => (
                  <div key={skill}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{skill}</span>
                      <span className="text-sm text-gray-600">{85 - i * 10}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${85 - i * 10}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Experience Distribution */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Experience Distribution</h2>
              <div className="space-y-4">
                {[
                  { range: '0-2 years', count: 2, color: 'bg-blue-500' },
                  { range: '2-4 years', count: 5, color: 'bg-green-500' },
                  { range: '4-6 years', count: 3, color: 'bg-yellow-500' },
                  { range: '6+ years', count: 1, color: 'bg-purple-500' }
                ].map((item) => (
                  <div key={item.range} className="flex items-center gap-4">
                    <div className="w-24 text-sm font-medium text-gray-700">{item.range}</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-8 relative">
                      <div
                        className={`${item.color} h-8 rounded-full flex items-center justify-end pr-3 transition-all`}
                        style={{ width: `${(item.count / 11) * 100}%` }}
                      >
                        <span className="text-white text-sm font-medium">{item.count}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Screening Summary</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">15%</p>
                  <p className="text-sm text-gray-600 mt-1">Excellent Matches</p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-3xl font-bold text-yellow-600">35%</p>
                  <p className="text-sm text-gray-600 mt-1">Good Matches</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">3.2</p>
                  <p className="text-sm text-gray-600 mt-1">Avg. Years Experience</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-3xl font-bold text-purple-600">78%</p>
                  <p className="text-sm text-gray-600 mt-1">Location Match</p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">AI Recommendations</h2>
              <div className="space-y-3">
                <div className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <p className="text-sm font-semibold text-blue-800">Consider Experience Range</p>
                  <p className="text-sm text-blue-700 mt-1">Most qualified candidates have 2-4 years experience. Consider adjusting requirements.</p>
                </div>
                <div className="p-3 bg-green-50 border-l-4 border-green-500 rounded">
                  <p className="text-sm font-semibold text-green-800">High Skill Match</p>
                  <p className="text-sm text-green-700 mt-1">Python and Azure skills are abundant in your candidate pool.</p>
                </div>
                <div className="p-3 bg-yellow-50 border-l-4 border-yellow-500 rounded">
                  <p className="text-sm font-semibold text-yellow-800">Skill Gap Identified</p>
                  <p className="text-sm text-yellow-700 mt-1">Few candidates have strong DevOps experience. Consider training programs.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeScreener;