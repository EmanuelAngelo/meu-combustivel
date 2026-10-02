<script setup lang="ts">
import { useAppContext } from "../../composables/appContext";
const {
  isDemo,
  online,
  vehicles,
  stations,
  saving,
  dateInput,
  form,
  selectedVehicle,
  selectedStation,
  calculation,
  overCapacity,
  needsCheck,
  money,
  num,
  error,
  stationChanged,
  fuelChanged,
  saveFill,
  resetForm,
  newStation,
} = useAppContext();
import {
  MapPin,
  Plus,
  Check,
  Bike,
  CheckCircle2,
  AlertTriangle,
  Globe,
} from "lucide-vue-next";
import PrecosForms from "../forms/PrecosForms.vue";
import ResumoAbastecimentoExibicao from "../exibicao/ResumoAbastecimentoExibicao.vue";
</script>
<template>
  <form @submit.prevent="saveFill" class="fill-layout">
    <div class="form-column">
      <section class="card form-card">
        <div class="section-heading">
          <span class="step-number">01</span>
          <h2>Onde e com qual veículo?</h2>
        </div>
        <div class="field-grid">
          <label class="field"
            ><span>Veículo</span>
            <div class="input-icon">
              <Bike :size="19" /><select
                v-model="form.vehicle"
                @change="form.ack = false"
              >
                <option v-for="v in vehicles" :value="v.id">
                  {{ v.brand }} {{ v.model }} · {{ v.year }}
                </option>
              </select>
            </div></label
          ><label class="field"
            ><span>Data do abastecimento</span
            ><input type="date" v-model="form.date" :max="dateInput()" required
          /></label>
        </div>
        <div class="field station-field">
          <span
            ><label for="refueling-station">Posto de combustível</label>
            <button type="button" class="text-button" @click="newStation">
              <Plus :size="14" />Cadastrar posto
            </button></span
          >
          <div class="input-icon">
            <MapPin :size="19" /><select
              id="refueling-station"
              v-model="form.station"
              @change="stationChanged"
            >
              <option v-if="!stations.length" :value="0" disabled>
                Cadastre seu primeiro posto
              </option>
              <option v-for="s in stations" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
          <small v-if="selectedStation"
            >{{ selectedStation.address }} · {{ selectedStation.city }},
            {{ selectedStation.state }}</small
          >
        </div>
      </section>
      <section class="card form-card">
        <div class="section-heading">
          <span class="step-number">02</span>
          <h2>O que aparece na bomba?</h2>
        </div>
        <div class="field-grid fuel-fields">
          <label class="field"
            ><span>Combustível</span
            ><select v-model="form.fuel" @change="fuelChanged">
              <option>Gasolina comum</option>
              <option>Gasolina aditivada</option>
              <option>Etanol</option>
              <option>Diesel S10</option>
              <option>Diesel S500</option>
            </select></label
          ><label class="field"
            ><span>Pagamento</span
            ><select
              v-model="form.payment"
              @change="
                form.price = '';
                form.ack = false;
              "
            >
              <option>Pix</option>
              <option>Dinheiro</option>
              <option>Débito</option>
              <option>Crédito</option>
              <option>Aplicativo / desconto</option>
            </select></label
          >
        </div>
        <PrecosForms
          v-model:common-payment="form.common_payment"
          v-model:common-price="form.common_price"
          v-model:credit-price="form.credit_price"
        />
        <div class="pump-values">
          <label class="field"
            ><span>Preço por litro</span>
            <div class="amount-input">
              <span>R$</span
              ><input
                aria-label="Preço por litro"
                inputmode="decimal"
                v-model="form.price"
                placeholder="0,00"
                required
                @input="form.ack = false"
              />
            </div>
            <small>Preço anunciado no posto</small></label
          ><label class="field"
            ><span>Total pago</span>
            <div class="amount-input">
              <span>R$</span
              ><input
                aria-label="Total pago"
                inputmode="decimal"
                v-model="form.total"
                placeholder="0,00"
                required
                @input="form.ack = false"
              />
            </div>
            <small>Valor cobrado na bomba</small></label
          ><label class="field"
            ><span>Quantidade de litros</span>
            <div class="amount-input">
              <input
                aria-label="Quantidade de litros"
                inputmode="decimal"
                v-model="form.liters"
                placeholder="0,000"
                required
                @input="form.ack = false"
              /><span>L</span>
            </div>
            <small>Volume indicado na bomba</small></label
          >
        </div>
        <div
          v-if="calculation"
          :class="['calculation-status', needsCheck ? 'warning' : 'success']"
          aria-live="polite"
        >
          <component
            :is="needsCheck ? AlertTriangle : CheckCircle2"
            :size="21"
          />
          <div>
            <strong>{{
              overCapacity
                ? "Quantidade acima da capacidade cadastrada"
                : calculation.consistent
                  ? "Tudo certo com os valores"
                  : "Vamos conferir esses valores?"
            }}</strong>
            <p>
              {{
                overCapacity
                  ? `O tanque cadastrado tem ${num(selectedVehicle.capacity)} L. Revise a capacidade ou os litros.`
                  : calculation.consistent
                    ? "O total corresponde ao preço por litro × quantidade abastecida."
                    : `Há uma diferença de ${money(Math.abs(calculation.difference))}. Confira os números e eventuais descontos.`
              }}
            </p>
          </div>
        </div>
        <label v-if="needsCheck" class="check-row review-check"
          ><input type="checkbox" v-model="form.ack" />Conferi os dados e quero
          manter os valores informados.</label
        >
      </section>
      <section class="card form-card">
        <div class="section-heading">
          <span class="step-number">03</span>
          <h2>Detalhes do abastecimento</h2>
          <span class="optional">Opcional</span>
        </div>
        <div class="field-grid">
          <label class="field"
            ><span>Quilometragem atual</span>
            <div class="amount-input regular">
              <input
                v-model="form.km"
                inputmode="numeric"
                placeholder="Ex.: 4400"
              /><span>km</span>
            </div></label
          >
          <div class="tank-toggle">
            <div>
              <strong>Completou o tanque?</strong
              ><small>Ajuda a acompanhar o consumo.</small>
            </div>
            <button
              type="button"
              role="switch"
              :aria-checked="form.full"
              aria-label="Completou o tanque?"
              :class="['switch', { on: form.full }]"
              @click="form.full = !form.full"
            >
              <span></span>
            </button>
          </div>
        </div>
        <label class="field notes-field"
          ><span>Observação</span
          ><textarea
            v-model="form.note"
            placeholder="Algo que você queira lembrar deste abastecimento…"
            rows="2"
            maxlength="1000"
          ></textarea>
        </label>
      </section>
      <div class="share-row">
        <label class="check-row"
          ><input type="checkbox" v-model="form.share" /><span
            ><strong>Contribuir com o preço deste posto</strong
            ><small
              >Compartilhe somente combustível, preço, data e condição de
              pagamento.</small
            ></span
          ></label
        ><Globe :size="21" />
      </div>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <div class="form-actions">
        <button type="button" class="text-button muted" @click="resetForm">
          Limpar campos</button
        ><button
          type="submit"
          class="primary-button"
          :disabled="saving || (!isDemo && !online)"
        >
          <Check :size="19" />{{
            saving ? "Salvando…" : "Salvar abastecimento"
          }}
        </button>
      </div>
    </div>
    <ResumoAbastecimentoExibicao />
  </form>
</template>
