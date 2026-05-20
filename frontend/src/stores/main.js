import { defineStore } from 'pinia'
import { dailyService, userService, submissionService } from '../services/api'

export const useMainStore = defineStore('main', {
  state: () => ({
    // Load initial user state from localStorage if available
    user: JSON.parse(localStorage.getItem('user')) || null,
    
    // Daily question state
    dailyQuestion: null,
    dailyLoading: false,
    dailyError: null,
    
    // Local persistence of today's submission status
    // Keyed by daily question ID to reset automatically when a new daily challenge goes active
    submissionHistory: JSON.parse(localStorage.getItem('submissionHistory')) || {}
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    
    currentSubmission: (state) => {
      if (!state.dailyQuestion || !state.user) return null
      const userKey = `user_${state.user.id}`
      const userHistory = state.submissionHistory[userKey] || {}
      return userHistory[state.dailyQuestion.id] || null
    },
    
    hasSubmittedToday: (state) => {
      if (!state.dailyQuestion || !state.user) return false
      const userKey = `user_${state.user.id}`
      const userHistory = state.submissionHistory[userKey] || {}
      return !!userHistory[state.dailyQuestion.id]
    }
  },

  actions: {
    // Authentication actions
    setUser(userData) {
      this.user = userData
      if (userData) {
        localStorage.setItem('user', JSON.stringify(userData))
      } else {
        localStorage.removeItem('user')
      }
    },
    
    async registerUser(username, email, password) {
      try {
        const userData = await userService.register({ username, email, password })
        this.setUser(userData)
        if (this.dailyQuestion) {
          await this.syncSubmissionStatus(this.dailyQuestion.id)
        }
        return userData
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      }
    },
    
    async loginUser(email, password) {
      try {
        const userData = await userService.login({ email, password })
        this.setUser(userData)
        if (this.dailyQuestion) {
          await this.syncSubmissionStatus(this.dailyQuestion.id)
        }
        return userData
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },
    
    logout() {
      this.setUser(null)
    },

    // Daily Challenge actions
    async fetchDailyQuestion(forceRefresh = false) {
      if (this.dailyQuestion && !forceRefresh) {
        if (this.user && !this.hasSubmittedToday) {
          await this.syncSubmissionStatus(this.dailyQuestion.id)
        }
        return
      }
      
      this.dailyLoading = true
      this.dailyError = null
      
      try {
        const question = await dailyService.getDailyQuestion()
        this.dailyQuestion = question
        if (this.user) {
          await this.syncSubmissionStatus(question.id)
        }
      } catch (error) {
        console.error('Failed fetching daily question in store:', error)
        this.dailyError = 'Failed to load today\'s challenge. Please try again later.'
      } finally {
        this.dailyLoading = false
      }
    },
    
    async syncSubmissionStatus(questionId) {
      if (!this.user) return
      try {
        const status = await submissionService.getSubmissionStatus(questionId, this.user.id)
        if (status.has_submitted) {
          this.recordSubmission(questionId, status.selected_answer, status.is_correct)
        }
      } catch (error) {
        console.error('Failed to sync submission status from backend:', error)
      }
    },
    
    async submitChallenge(questionId, submittedAnswer) {
      if (!this.user) throw new Error('User must be logged in to submit an answer.')
      
      try {
        const response = await submissionService.submit(questionId, submittedAnswer, this.user.id)
        this.recordSubmission(questionId, submittedAnswer, response.is_correct)
        return response
      } catch (error) {
        console.error('Submission failed:', error)
        throw error
      }
    },

    // Record submission state locally
    recordSubmission(questionId, selectedAnswer, isCorrect) {
      if (!this.user) return
      const userKey = `user_${this.user.id}`
      const userHistory = this.submissionHistory[userKey] || {}
      
      this.submissionHistory = {
        ...this.submissionHistory,
        [userKey]: {
          ...userHistory,
          [questionId]: {
            selectedAnswer,
            isCorrect,
            submittedAt: new Date().toISOString()
          }
        }
      }
      localStorage.setItem('submissionHistory', JSON.stringify(this.submissionHistory))
    }
  }
})
