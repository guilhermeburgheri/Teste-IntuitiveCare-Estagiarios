<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/services/api";

const route = useRoute();
const cnpj = route.params.cnpj;

const operadora = ref(null);
const despesas = ref([]);

const loading = ref(false);
const errorMsg = ref("");

async function carregarDetalhes() {
  loading.value = true;
  errorMsg.value = "";

  try {
    const resOp = await api.get(`/api/operadoras/${cnpj}`);
    operadora.value = resOp.data;

    const resDesp = await api.get(`/api/operadoras/${cnpj}/despesas`);
    despesas.value = resDesp.data.data || [];
  } catch (e) {
    errorMsg.value = "Erro ao carregar detalhes da operadora.";
  } finally {
    loading.value = false;
  }
}

onMounted(carregarDetalhes);
</script>

<template>
  <div>
    <h1>Detalhes da Operadora</h1>

    <div v-if="loading">Carregando...</div>
    <div v-if="errorMsg" style="color: red;">{{ errorMsg }}</div>

    <div v-if="operadora && !loading">
      <p><b>Razão Social:</b> {{ operadora.Razao_Social }}</p>
      <p><b>CNPJ:</b> {{ operadora.CNPJ }}</p>
      <p><b>Registro ANS:</b> {{ operadora.REGISTRO_OPERADORA }}</p>
      <p><b>UF:</b> {{ operadora.UF }}</p>
      <p><b>Modalidade:</b> {{ operadora.Modalidade }}</p>

      <hr />

      <h2>Histórico de Despesas</h2>

      <table border="1" cellpadding="6">
        <thead>
          <tr>
            <th>Ano</th>
            <th>Trimestre</th>
            <th>ValorDespesas</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(d, idx) in despesas" :key="idx">
            <td>{{ d.Ano }}</td>
            <td>{{ d.Trimestre }}</td>
            <td>{{ d.ValorDespesas }}</td>
          </tr>

          <tr v-if="despesas.length === 0">
            <td colspan="3">Sem despesas encontradas.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
