<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="candidates.length === 0" class="card">
      <p class="no-candidates">{{ t('restocking.noCandidates') }}</p>
    </div>
    <div v-else>
      <!-- Success Banner -->
      <div v-if="successMessage" class="success-banner">{{ successMessage }}</div>
      <div v-if="submitError" class="error">{{ submitError }}</div>

      <!-- Budget Control -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
        </div>
        <div class="budget-controls">
          <div class="budget-display">
            <span class="budget-amount">{{ currencySymbol }}{{ budget.toLocaleString() }}</span>
          </div>
          <div class="slider-row">
            <input
              type="range"
              class="budget-slider"
              :min="0"
              :max="maxBudget"
              :step="sliderStep || 1"
              :disabled="maxBudget === 0"
              v-model.number="budget"
              @input="syncBudgetInput"
            />
            <input
              type="number"
              class="budget-number"
              :min="0"
              :max="maxBudget"
              v-model.number="budgetInput"
              @input="onBudgetNumberInput"
            />
          </div>
          <p class="budget-hint">{{ t('restocking.budgetHint') }}</p>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.recommendedCount', { recommended: recommendedCount, total: totalCount }) }}</div>
          <div class="stat-value">{{ recommendedCount }} / {{ totalCount }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ recommendedTotal.toLocaleString() }}</div>
        </div>
        <div class="stat-card" :class="remainingBudget >= 0 ? 'success' : 'warning'">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ Math.abs(remainingBudget).toLocaleString() }}</div>
        </div>
      </div>

      <!-- Recommendations Table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }}</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.demand') }}</th>
                <th>{{ t('restocking.table.recommendedQty') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineCost') }}</th>
                <th>{{ t('restocking.table.leadTime') }}</th>
                <th>{{ t('restocking.table.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="c in annotatedCandidates"
                :key="c.item_sku"
                :class="{ 'over-budget-row': !c.recommended }"
              >
                <td><strong>{{ translateProductName(c.item_name) }}</strong></td>
                <td class="sku-cell">{{ c.item_sku }}</td>
                <td>
                  <span :class="['badge', c.trend]">{{ t('trends.' + c.trend) }}</span>
                </td>
                <td>{{ c.current_demand }} &rarr; {{ c.forecasted_demand }}</td>
                <td>{{ c.recommended_qty }}</td>
                <td>{{ currencySymbol }}{{ c.unit_cost.toLocaleString() }}</td>
                <td>{{ currencySymbol }}{{ c.line_cost.toLocaleString() }}</td>
                <td>{{ c.lead_time_days }} {{ t('restocking.days') }}</td>
                <td>
                  <span v-if="c.recommended" class="badge success">{{ t('restocking.recommended') }}</span>
                  <span v-else class="badge warning">{{ t('restocking.overBudget') }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Place Order Button -->
      <div class="order-action">
        <button
          class="btn-primary"
          :disabled="submitting || recommendedItems.length === 0"
          @click="placeOrder"
        >
          {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const currencySymbol = computed(() => currentCurrency.value === 'JPY' ? '¥' : '$')

    const loading = ref(true)
    const error = ref(null)
    const candidates = ref([])
    const submitting = ref(false)
    const successMessage = ref('')
    const submitError = ref('')

    // Budget reactive state
    const budget = ref(0)
    // Synced number input (mirrors budget, allows editing)
    const budgetInput = ref(0)

    const maxBudget = computed(() => {
      const sum = candidates.value.reduce((acc, c) => acc + c.line_cost, 0)
      return Math.round(sum * 100) / 100
    })

    const sliderStep = computed(() => {
      if (maxBudget.value === 0) return 1
      return maxBudget.value / 100
    })

    // Annotated candidates: greedy walk to mark each as recommended or over-budget
    const annotatedCandidates = computed(() => {
      let cumulative = 0
      return candidates.value.map(c => {
        const candidate_total = Math.round((cumulative + c.line_cost) * 100) / 100
        const budget_rounded = Math.round(budget.value * 100) / 100
        if (candidate_total <= budget_rounded) {
          cumulative = candidate_total
          return { ...c, recommended: true }
        } else {
          return { ...c, recommended: false }
        }
      })
    })

    const recommendedItems = computed(() => annotatedCandidates.value.filter(c => c.recommended))

    const recommendedTotal = computed(() => {
      const sum = recommendedItems.value.reduce((acc, c) => acc + c.line_cost, 0)
      return Math.round(sum * 100) / 100
    })

    const remainingBudget = computed(() => {
      return Math.round((budget.value - recommendedTotal.value) * 100) / 100
    })

    const recommendedCount = computed(() => recommendedItems.value.length)
    const totalCount = computed(() => candidates.value.length)

    const onBudgetNumberInput = () => {
      let val = budgetInput.value
      if (isNaN(val) || val < 0) val = 0
      if (val > maxBudget.value) val = maxBudget.value
      budget.value = val
      budgetInput.value = val
    }

    // Keep budgetInput in sync when slider moves
    const syncBudgetInput = () => {
      budgetInput.value = budget.value
    }

    const loadCandidates = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await api.getRestockCandidates()
        candidates.value = data

        // Set default budget to 50% of max after data loads
        const max = Math.round(data.reduce((acc, c) => acc + c.line_cost, 0) * 100) / 100
        const defaultBudget = Math.round(max * 0.5 * 100) / 100
        budget.value = defaultBudget
        budgetInput.value = defaultBudget
      } catch (err) {
        error.value = 'Failed to load restock candidates: ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (submitting.value || recommendedItems.value.length === 0) return
      submitting.value = true
      successMessage.value = ''
      submitError.value = ''

      try {
        const payload = {
          budget: budget.value,
          items: recommendedItems.value.map(c => ({
            sku: c.item_sku,
            name: c.item_name,
            quantity: c.recommended_qty,
            unit_cost: c.unit_cost,
            lead_time_days: c.lead_time_days
          }))
        }
        const result = await api.submitRestockOrder(payload)
        successMessage.value = t('restocking.orderPlaced', { orderNumber: result.order_number })
      } catch (err) {
        submitError.value = 'Failed to place order: ' + err.message
        console.error(err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadCandidates)

    return {
      t,
      currencySymbol,
      translateProductName,
      loading,
      error,
      candidates,
      budget,
      budgetInput,
      maxBudget,
      sliderStep,
      annotatedCandidates,
      recommendedItems,
      recommendedTotal,
      remainingBudget,
      recommendedCount,
      totalCount,
      submitting,
      successMessage,
      submitError,
      onBudgetNumberInput,
      syncBudgetInput,
      placeOrder
    }
  }
}
</script>

<style scoped>
.no-candidates {
  color: #64748b;
  padding: 2rem 0;
  text-align: center;
  font-size: 0.938rem;
}

.budget-card .card-header {
  margin-bottom: 1rem;
}

.budget-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.budget-display {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.budget-amount {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.slider-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.budget-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  cursor: pointer;
}

.budget-slider:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: background 0.15s ease, box-shadow 0.15s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  background: #1d4ed8;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.4);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.budget-slider::-webkit-slider-runnable-track {
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
}

.budget-slider::-moz-range-track {
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
}

.budget-number {
  width: 130px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.938rem;
  color: #0f172a;
  outline: none;
  transition: border-color 0.15s ease;
}

.budget-number:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.budget-hint {
  font-size: 0.813rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.over-budget-row {
  opacity: 0.45;
}

.sku-cell {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.813rem;
  color: #64748b;
}

.order-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
  margin-bottom: 1.5rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 2rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
  letter-spacing: 0.01em;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success-banner {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.938rem;
  font-weight: 500;
}
</style>
