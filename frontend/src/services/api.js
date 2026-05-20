import axios from 'axios'

// Dynamically use environment API base URL, fallback to local FastAPI development port
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Service layer encapsulating CRUD operations for questions administration
export const questionService = {
  getQuestions() {
    return apiClient.get('/api/questions').then(response => response.data)
  },
  getQuestion(id) {
    return apiClient.get(`/api/questions/${id}`).then(response => response.data)
  },
  createQuestion(questionData) {
    return apiClient.post('/api/questions', questionData).then(response => response.data)
  },
  updateQuestion(id, questionData) {
    return apiClient.put(`/api/questions/${id}`, questionData).then(response => response.data)
  },
  deleteQuestion(id) {
    return apiClient.delete(`/api/questions/${id}`).then(response => response.data)
  }
}

// Service layer for the daily challenge endpoints
export const dailyService = {
  getDailyQuestion() {
    return apiClient.get('/api/daily').then(response => {
      return {
        ...response.data,
        fromCache: response.headers['x-cache'] === 'HIT'
      }
    })
  }
}

// Service layer for user registration and authentication
export const userService = {
  register(userData) {
    return apiClient.post('/api/users/register', userData).then(response => response.data)
  },
  login(credentials) {
    return apiClient.post('/api/users/login', credentials).then(response => response.data)
  }
}

// Service layer for challenge submissions
export const submissionService = {
  submit(questionId, submittedAnswer, userId) {
    return apiClient.post('/api/submissions', 
      { question_id: questionId, submitted_answer: submittedAnswer },
      { headers: { 'X-User-ID': userId } }
    ).then(response => response.data)
  },
  getSubmissionStatus(questionId, userId) {
    return apiClient.get(`/api/submissions/status/${questionId}`, {
      headers: { 'X-User-ID': userId }
    }).then(response => response.data)
  }
}

export default apiClient
