<script>
import { useMainStore } from '../stores/main'

export default {
  name: 'HomeView',
  data() {
    return {
      authTab: 'login',
      authError: null,
      authLoading: false,
      authForm: {
        username: '',
        email: '',
        password: ''
      },
      localSelectedAnswer: null,
      submitLoading: false,
      submitError: null
    }
  },
  computed: {
    mainStore() {
      return useMainStore()
    },
    isAuthenticated() {
      return this.mainStore.isAuthenticated
    },
    question() {
      return this.mainStore.dailyQuestion
    },
    loading() {
      return this.mainStore.dailyLoading
    },
    error() {
      return this.mainStore.dailyError
    },
    hasSubmitted() {
      return this.mainStore.hasSubmittedToday
    },
    isCorrect() {
      if (this.mainStore.currentSubmission) {
        return this.mainStore.currentSubmission.isCorrect
      }
      return false
    },
    selectedAnswer() {
      if (this.mainStore.currentSubmission) {
        return this.mainStore.currentSubmission.selectedAnswer
      }
      return this.localSelectedAnswer
    }
  },
  async created() {
    // Fetch the daily question from backend via the store
    await this.mainStore.fetchDailyQuestion()
  },
  watch: {
    isAuthenticated() {
      this.localSelectedAnswer = null
    }
  },
  methods: {
    async handleAuthSubmit() {
      this.authError = null
      this.authLoading = true
      try {
        if (this.authTab === 'login') {
          await this.mainStore.loginUser(this.authForm.email, this.authForm.password)
        } else {
          await this.mainStore.registerUser(this.authForm.username, this.authForm.email, this.authForm.password)
        }
        // Clear form
        this.authForm.username = ''
        this.authForm.email = ''
        this.authForm.password = ''
      } catch (err) {
        this.authError = err.response?.data?.detail || 'An error occurred during authentication.'
      } finally {
        this.authLoading = false
      }
    },
    selectAnswer(option) {
      if (!this.hasSubmitted) {
        this.localSelectedAnswer = option
        this.submitError = null
      }
    },
    async submitAnswer() {
      if (!this.selectedAnswer || !this.question) return
      
      this.submitLoading = true
      this.submitError = null
      try {
        await this.mainStore.submitChallenge(this.question.id, this.selectedAnswer)
      } catch (err) {
        this.submitError = err.response?.data?.detail || 'Failed to submit answer. Please try again.'
      } finally {
        this.submitLoading = false
      }
    }
  }
}
</script>

<template>
  <div class="container mt-5 challenge-container mx-auto pb-5">
    
    <!-- Authentication flow (when not logged in) -->
    <div v-if="!isAuthenticated" class="card shadow-lg border-0 rounded-4 overflow-hidden auth-card mx-auto">
      <div class="card-header bg-primary text-white py-3 border-0">
        <ul class="nav nav-pills card-header-pills justify-content-center">
          <li class="nav-item">
            <button class="nav-link text-white px-4 fw-bold" :class="{ active: authTab === 'login' }" @click="authTab = 'login'">Login</button>
          </li>
          <li class="nav-item">
            <button class="nav-link text-white px-4 fw-bold" :class="{ active: authTab === 'register' }" @click="authTab = 'register'">Register</button>
          </li>
        </ul>
      </div>
      
      <div class="card-body p-4 p-md-5">
        <h3 class="fw-bold text-center mb-4">{{ authTab === 'login' ? 'Welcome Back!' : 'Create Your Account' }}</h3>
        
        <div v-if="authError" class="alert alert-danger border-0 rounded-3 mb-4 d-flex align-items-center">
          <i class="bi bi-exclamation-circle-fill me-2"></i>
          <div>{{ authError }}</div>
        </div>

        <form @submit.prevent="handleAuthSubmit">
          <div v-if="authTab === 'register'" class="mb-4">
            <label class="form-label fw-semibold text-secondary">Username</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-person text-muted"></i></span>
              <input v-model="authForm.username" type="text" class="form-control bg-light border-start-0 ps-0" placeholder="username" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold text-secondary">Email Address</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-envelope text-muted"></i></span>
              <input v-model="authForm.email" type="email" class="form-control bg-light border-start-0 ps-0" placeholder="email@domain.com" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold text-secondary">Password</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"><i class="bi bi-lock text-muted"></i></span>
              <input v-model="authForm.password" type="password" class="form-control bg-light border-start-0 ps-0" placeholder="••••••••" required minlength="6">
            </div>
          </div>

          <div class="d-grid mt-5">
            <button type="submit" class="btn btn-primary btn-lg py-3 rounded-pill fw-bold text-uppercase letter-spacing-1 shadow-sm" :disabled="authLoading">
              <span v-if="authLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ authTab === 'login' ? 'Sign In' : 'Create Account' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Active challenge flow (when logged in) -->
    <div v-else>
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <h5 class="mt-4 text-muted fw-semibold animate-pulse">Loading today's challenge...</h5>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger shadow-sm border-0 rounded-4 p-4 text-center">
        <i class="bi bi-exclamation-triangle-fill fs-1 text-danger mb-3 d-block"></i>
        <h4 class="alert-heading fw-bold">Oops!</h4>
        <p class="mb-3 fs-5">{{ error }}</p>
        <button class="btn btn-outline-danger rounded-pill px-4 fw-bold shadow-sm" @click="mainStore.fetchDailyQuestion(true)">
          <i class="bi bi-arrow-clockwise me-1"></i> Retry
        </button>
      </div>

      <!-- Challenge UI -->
      <div v-else-if="question" class="card shadow-lg border-0 rounded-4 overflow-hidden">
        <!-- Card Header -->
        <div class="card-header bg-primary text-white py-3 px-4 border-0">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-2">
              <span class="badge bg-white text-primary rounded-pill px-3 py-2 text-uppercase fw-bold letter-spacing-1">
                {{ question.category }}
              </span>
              <span v-if="question.fromCache" class="badge bg-info text-white rounded-pill px-2 py-1 fw-bold fs-7" title="Served directly from cache">
                <i class="bi bi-lightning-charge-fill"></i> Cached
              </span>
              <span v-else class="badge bg-warning text-dark rounded-pill px-2 py-1 fw-bold fs-7" title="Fetched from database">
                <i class="bi bi-database-fill"></i> DB Load
              </span>
            </div>
            <span class="opacity-75 fw-semibold">
              <i class="bi bi-calendar2-check me-2"></i>Daily Challenge
            </span>
          </div>
        </div>
        
        <!-- Card Body -->
        <div class="card-body p-4 p-md-5 bg-white">
          <h2 class="card-title fw-bolder mb-4 text-dark display-6">{{ question.title }}</h2>
          <p class="card-text fs-4 mb-5 text-secondary lh-base">{{ question.content }}</p>
          
          <!-- Options List -->
          <div class="d-grid gap-3">
            <button 
              v-for="(option, index) in question.options" 
              :key="index"
              class="btn btn-outline-primary text-start p-3 rounded-4 fs-5 transition-all option-btn"
              :class="{ 
                'active-selection': selectedAnswer === option && !hasSubmitted,
                'btn-success text-white border-success': hasSubmitted && option === question.correct_answer,
                'btn-danger text-white border-danger': hasSubmitted && selectedAnswer === option && option !== question.correct_answer,
                'opacity-50 grayscale': hasSubmitted && option !== question.correct_answer && option !== selectedAnswer
              }"
              @click="selectAnswer(option)"
              :disabled="hasSubmitted || submitLoading"
            >
              <div class="d-flex align-items-center">
                <span class="badge rounded-circle me-3 option-letter" 
                      :class="selectedAnswer === option || (hasSubmitted && (option === question.correct_answer || selectedAnswer === option)) ? 'bg-white text-dark' : 'bg-primary text-white'">
                  {{ String.fromCharCode(65 + index) }}
                </span>
                <span class="flex-grow-1 fw-medium">{{ option }}</span>
                
                <!-- Result Icons -->
                <i v-if="hasSubmitted && option === question.correct_answer" class="bi bi-check-circle-fill fs-3 mb-0 text-white animate-pop"></i>
                <i v-if="hasSubmitted && selectedAnswer === option && option !== question.correct_answer" class="bi bi-x-circle-fill fs-3 mb-0 text-white animate-pop"></i>
              </div>
            </button>
          </div>
          
          <!-- Submission Error Alert -->
          <div v-if="submitError" class="alert alert-danger border-0 rounded-4 mt-4 d-flex align-items-center justify-content-center shadow-sm">
            <i class="bi bi-exclamation-circle-fill me-2 fs-5"></i>
            <div class="fw-medium">{{ submitError }}</div>
          </div>
          
          <!-- Submit Action -->
          <div class="mt-4 text-center" v-if="!hasSubmitted">
            <button 
              class="btn btn-primary btn-lg px-5 py-3 rounded-pill shadow fw-bold text-uppercase letter-spacing-1 submit-btn" 
              :disabled="!selectedAnswer || submitLoading"
              @click="submitAnswer"
            >
              <span v-if="submitLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Submit Answer <i class="bi bi-send-fill ms-2"></i>
            </button>
          </div>
          
          <!-- Feedback Banner -->
          <div class="mt-5 p-4 rounded-4 text-center animate-fade-in" 
               :class="isCorrect ? 'bg-success bg-opacity-10 text-success border border-success border-opacity-25' : 'bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25'" 
               v-if="hasSubmitted">
            <h3 class="mb-0 fw-bold">
              <i :class="isCorrect ? 'bi bi-emoji-sunglasses-fill' : 'bi bi-emoji-frown-fill'" class="me-2 fs-2 align-middle"></i>
              {{ isCorrect ? 'Brilliant! That is absolutely correct.' : 'Not quite right. Keep practicing!' }}
            </h3>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.challenge-container {
  max-width: 850px;
}
.auth-card {
  max-width: 550px;
}
.letter-spacing-1 {
  letter-spacing: 1px;
}
.transition-all {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.option-btn {
  border-width: 2px;
}
.option-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
  background-color: #f8f9fa;
  color: var(--bs-primary) !important;
}
.option-letter {
  width: 36px; 
  height: 36px; 
  display: flex; 
  align-items: center; 
  justify-content: center;
  font-size: 1.1rem;
  transition: all 0.2s ease;
}
.active-selection {
  background-color: var(--bs-primary) !important;
  color: white !important;
  box-shadow: 0 8px 15px rgba(13, 110, 253, 0.3);
}
.active-selection .option-letter {
  background-color: white !important;
  color: var(--bs-primary) !important;
}
.option-btn.active-selection:hover {
  background-color: var(--bs-primary) !important;
  color: white !important;
}
/* Override Bootstrap disabled states to maintain readable contrast */
.option-btn.btn-success:disabled {
  background-color: #198754 !important;
  border-color: #198754 !important;
  color: white !important;
  opacity: 1 !important;
}
.option-btn.btn-danger:disabled {
  background-color: #dc3545 !important;
  border-color: #dc3545 !important;
  color: white !important;
  opacity: 1 !important;
}
.option-btn.grayscale:disabled {
  opacity: 0.4 !important;
  border-color: #dee2e6 !important;
  color: #6c757d !important;
  background-color: transparent !important;
}
.grayscale {
  filter: grayscale(100%);
}
.submit-btn {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(13, 110, 253, 0.4) !important;
}

/* Custom Animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pop {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}
.animate-pop {
  animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeIn 0.5s ease forwards;
}
</style>
