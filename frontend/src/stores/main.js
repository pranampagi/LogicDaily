import { defineStore } from 'pinia'
import { dailyService } from '../services/api'

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
      if (!state.dailyQuestion) return null
      return state.submissionHistory[state.dailyQuestion.id] || null
    },
    
    hasSubmittedToday: (state) => {
      if (!state.dailyQuestion) return false
      return !!state.submissionHistory[state.dailyQuestion.id]
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
    
    logout() {
      this.setUser(null)
    },

    // Daily Challenge actions
    async fetchDailyQuestion(forceRefresh = false) {
      if (this.dailyQuestion && !forceRefresh) return
      
      this.dailyLoading = true
      this.dailyError = null
      
      try {
        const question = await dailyService.getDailyQuestion()
        this.dailyQuestion = question
      } catch (error) {
        console.error('Failed fetching daily question in store:', error)
        this.dailyError = 'Failed to load today\'s challenge. Please try again later.'
      } finally {
        this.dailyLoading = false
      }
    },

    // Record submission state locally
    recordSubmission(questionId, selectedAnswer, isCorrect) {
      this.submissionHistory = {
        ...this.submissionHistory,
        [questionId]: {
          selectedAnswer,
          isCorrect,
          submittedAt: new Date().toISOString()
        }
      }
      localStorage.setItem('submissionHistory', JSON.stringify(this.submissionHistory))
    }
  }
})
