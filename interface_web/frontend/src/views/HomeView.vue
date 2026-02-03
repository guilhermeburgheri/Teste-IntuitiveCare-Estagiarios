<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { api } from "@/services/api";
import Chart from "chart.js/auto";
import { useRouter } from "vue-router";

const router = useRouter();

const operadoras = ref([]);
const page = ref(1);
const limit = ref(10);
const total = ref(0);
const q = ref("");

const loading = ref(false);
const errorMsg = ref("");

const ufStats = ref([]);
const chartCanvas = ref(null);
let chartInstance = null;

async function carregar() {
  loading.value = true;
  errorMsg.value = "";

  try {
    const res = await api.get("/api/operadoras", {
      params: {
        page: page.value,
        limit: limit.value,
        q: q.value || undefined
      }
    });

    operadoras.value = res.data.data;
    total.value = res.data.total;
  } catch (e) {
    errorMsg.value = "Erro ao carregar operadoras.";
  } finally {
    loading.value = false;
  }
}

async function carregarEstatisticas() {
  try {
    const res = await api.get("/api/estatisticas");
    ufStats.value = res.data.despesas_por_uf || [];
    await nextTick();
    desenharChart();
  } catch (e) {
    // silencioso pra não “quebrar” a home
  }
}

function desenharChart() {
  if (!chartCanvas.value) return;

  const labels = ufStats.value.map((x) => x.uf);
  const values = ufStats.value.map((x) => x.total);

  if (chartInstance) {
    chartInstance.destroy();
  }

  const ctx = chartCanvas.value.getContext("2d");

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Total de Despesas por UF",
          data: values
        }
      ]
    },
    options: {
      scales: {
        y: {
          ticks: {
            callback: (value) => (value / 1_000_000_000).toFixed(0) + " bi"
          }
        }
      }
    }
  });
}


function proxima() {
  page.value++;
  carregar();
}

function anterior() {
  if (page.value > 1) {
    page.value--;
    carregar();
  }
}

function irDetalhe(cnpj) {
  router.push(`/operadoras/${cnpj}`);
}

onMounted(async () => {
  await carregar();
  await carregarEstatisticas();
});

// se quiser redesenhar quando stats mudarem
watch(ufStats, () => desenharChart());
</script>

<template>
  <div>
    <h1>Operadoras Ativas</h1>

    <div style="margin-bottom: 10px;">
      <input
        v-model="q"
        placeholder="Buscar por nome, CNPJ ou Registro ANS"
        @keyup.enter="carregar"
      />
      <button @click="carregar">Buscar</button>
    </div>

    <div v-if="loading">Carregando...</div>
    <div v-if="errorMsg" style="color: red;">{{ errorMsg }}</div>

    <table v-if="!loading" border="1" cellpadding="6">
      <thead>
        <tr>
          <th>Registro ANS</th>
          <th>Razão Social</th>
          <th>UF</th>
          <th>Modalidade</th>
          <th>Ações</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="op in operadoras" :key="op.REGISTRO_OPERADORA">
          <td>{{ op.REGISTRO_OPERADORA }}</td>
          <td>{{ op.Razao_Social }}</td>
          <td>{{ op.UF }}</td>
          <td>{{ op.Modalidade }}</td>
          <td>
            <button @click="irDetalhe(op.CNPJ)">Detalhes</button>
          </td>
        </tr>

        <tr v-if="operadoras.length === 0">
          <td colspan="5">Nenhum resultado.</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 10px;">
      <button @click="anterior" :disabled="page === 1">Anterior</button>
      <span> Página {{ page }} </span>
      <button @click="proxima" :disabled="page * limit >= total">Próxima</button>
    </div>

    <hr style="margin: 20px 0;" />

    <h2>Distribuição de Despesas por UF</h2>

    <canvas ref="chartCanvas" style="max-height: 500px;"></canvas>
  </div>
</template>
