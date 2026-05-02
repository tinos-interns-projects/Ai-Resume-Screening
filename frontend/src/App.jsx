import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000/api'

function App() {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [resumes, setResumes] = useState([])
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [clearing, setClearing] = useState(false)

  useEffect(() => {
    fetchJobs()
  }, [])

  useEffect(() => {
    if (selectedJob) {
      fetchResumes()
    }
  }, [selectedJob])

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/jobs/`)
      setJobs(response.data)
    } catch (err) {
      console.error('Error fetching jobs:', err)
      setError('Failed to load jobs. Is backend running?')
    }
  }

  const fetchResumes = async () => {
    try {
      const response = await axios.get(`${API_BASE}/resumes/?job=${selectedJob}`)
      const sorted = response.data.sort((a, b) => b.match_score - a.match_score)
      setResumes(sorted)
    } catch (err) {
      console.error('Error fetching resumes:', err)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    const fileInput = e.target.querySelector('input[type="file"]')
    const file = fileInput.files[0]

    if (!file || !selectedJob) {
      setError('Please select both a job and a resume file')
      return
    }

    setUploading(true)
    setMessage('')
    setError('')

    const formData = new FormData()
    formData.append('job_id', selectedJob)
    formData.append('resume', file)

    try {
      const response = await axios.post(
        `${API_BASE}/resumes/upload_and_screen/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setMessage(`✅ Score: ${response.data.match_score}% - ${response.data.message}`)
      fileInput.value = ''
      fetchResumes()
    } catch (err) {
      console.error('Upload error:', err)
      setError(err.response?.data?.error || 'Upload failed. Check console for details.')
    } finally {
      setUploading(false)
    }
  }

  const handleClearAll = async () => {
    if (!confirm('⚠️ Delete ALL candidates for this job? This cannot be undone!')) return;
    
    setClearing(true);
    try {
      const response = await axios.delete(`${API_BASE}/resumes/clear_all/`, {
        params: { job: selectedJob }
      });
      setResumes([]);
      alert(`✅ ${response.data.message}`);
    } catch (err) {
      alert('❌ Error: ' + (err.response?.data?.error || 'Failed to delete'));
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🤖 AI Resume Screener</h1>
        <p>Upload resumes & get instant AI match scores</p>
      </header>

      <main>
        <section className="card">
          <h2><b>1. Select Job Position</b></h2>
          <select 
            value={selectedJob} 
            onChange={e => setSelectedJob(e.target.value)}
            className="input-field"
          >
            <option value="">-- Choose a Job --</option>
            {jobs.map(job => (
              <option key={job.id} value={job.id}>{job.title}</option>
            ))}
          </select>
        </section>

        <section className="card">
          <h2><b>2. Upload Resume</b></h2>
          <form onSubmit={handleUpload} className="upload-form">
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
              required 
              disabled={!selectedJob}
            />
            <button 
              type="submit" 
              disabled={uploading || !selectedJob}
            >
              {uploading ? '⏳ Screening...' : '🚀 Upload & Screen'}
            </button>
          </form>
          
          {message && <p className="message success">{message}</p>}
          {error && <p className="message error">{error}</p>}
        </section>

        {resumes.length > 0 && (
          <section className="card results">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ margin: 0 }}><b>3. Ranked Candidates ({resumes.length})</b></h2>
              <button
                onClick={handleClearAll}
                disabled={clearing}
                style={{
                  background: '#e53e3e',
                  color: 'white',
                  border: 'none',
                  padding: '0.6rem 1.2rem',
                  borderRadius: '8px',
                  cursor: clearing ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  opacity: clearing ? 0.6 : 1,
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => !clearing && (e.target.style.background = '#c53030')}
                onMouseLeave={(e) => !clearing && (e.target.style.background = '#e53e3e')}
              >
                {clearing ? '⏳ Deleting...' : '🗑️ Clear All'}
              </button>
            </div>
            
            <div className="results-list">
              {resumes.map((resume, index) => (
                <div key={resume.id} className="result-item">
                  <span className="rank">#{index + 1}</span>
                  <div className="candidate-info">
                    <strong>{resume.candidate_name || 'Unknown'}</strong>
                    <div className="score-bar">
                      <div 
                        className="score-fill" 
                        style={{ width: `${resume.match_score}%` }}
                      />
                    </div>
                  </div>
                  <span className="score">{resume.match_score}%</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App