<script>
import { dailyService } from '../services/api'

export default {
  name: 'HomeView',
  data() {
    return {
      loading: true,
      error: null,
      question: null,
      selectedAnswer: null,
      hasSubmitted: false,
      isCorrect: false
    }
  },
  async created() {
    try {
      this.question = await dailyService.getDailyQuestion()
    } catch (err) {
      console.error('Failed to fetch daily question:', err)
      this.error = "Failed to load today's challenge. Please ensure the API is running."
    } finally {
      this.loading = false
    }
  },
  methods: {
    selectAnswer(option) {
      if (!this.hasSubmitted) {
        this.selectedAnswer = option
      }
    },
    submitAnswer() {
      if (!this.selectedAnswer) return;
      
      this.hasSubmitted = true;
      this.isCorrect = (this.selectedAnswer === this.question.correct_answer);
      
      // Note: In Commit 18, we will actually POST this to the backend
      // API to securely evaluate and record the submission.
    }
  }
}
</script>

<template>
  <div class="container mt-5 challenge-container mx-auto pb-5">
    
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
      <p class="mb-0 fs-5">{{ error }}</p>
    </div>

    <!-- Challenge UI -->
    <div v-else-if="question" class="card shadow-lg border-0 rounded-4 overflow-hidden">
      <!-- Card Header -->
      <div class="card-header bg-primary text-white py-3 px-4 border-0">
        <div class="d-flex justify-content-between align-items-center">
          <span class="badge bg-white text-primary rounded-pill px-3 py-2 text-uppercase fw-bold letter-spacing-1">
            {{ question.category }}
          </span>
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
            :disabled="hasSubmitted"
          >
            <div class="d-flex align-items-center">
              <span class="badge rounded-circle me-3 option-letter" 
                    :class="selectedAnswer === option || hasSubmitted ? 'bg-white text-dark' : 'bg-primary text-white'">
                {{ String.fromCharCode(65 + index) }}
              </span>
              <span class="flex-grow-1 fw-medium">{{ option }}</span>
              
              <!-- Result Icons -->
              <i v-if="hasSubmitted && option === question.correct_answer" class="bi bi-check-circle-fill fs-3 mb-0 text-white animate-pop"></i>
              <i v-if="hasSubmitted && selectedAnswer === option && option !== question.correct_answer" class="bi bi-x-circle-fill fs-3 mb-0 text-white animate-pop"></i>
            </div>
          </button>
        </div>
        
        <!-- Submit Action -->
        <div class="mt-5 text-center" v-if="!hasSubmitted">
          <button 
            class="btn btn-primary btn-lg px-5 py-3 rounded-pill shadow fw-bold text-uppercase letter-spacing-1 submit-btn" 
            :disabled="!selectedAnswer"
            @click="submitAnswer"
          >
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
</template>

<style scoped>
.challenge-container {
  max-width: 850px;
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
