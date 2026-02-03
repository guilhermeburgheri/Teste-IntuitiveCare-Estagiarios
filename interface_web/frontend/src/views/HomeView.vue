<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/services/api";

const operadoras = ref([]);
const page = ref(1);
const limit = ref(10);
const total = ref(0);
const q = ref("");

async function carregar() {
  const res = await api.get("/api/operadoras", {
    params: {
      page: page.value,
      limit: limit.value,
      q: q.value || undefined
    }
  });

  operadoras.value = res.data.data;
  total.value = res.data.total;
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

onMounted(carregar);
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

    <table border="1" cellpadding="6">
      <thead>
        <tr>
          <th>Registro ANS</th>
          <th>Razão Social</th>
          <th>UF</th>
          <th>Modalidade</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="op in operadoras" :key="op.REGISTRO_OPERADORA">
          <td>{{ op.REGISTRO_OPERADORA }}</td>
          <td>{{ op.Razao_Social }}</td>
          <td>{{ op.UF }}</td>
          <td>{{ op.Modalidade }}</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 10px;">
      <button @click="anterior" :disabled="page === 1">
        Anterior
      </button>

      <span> Página {{ page }} </span>

      <button
        @click="proxima"
        :disabled="page * limit >= total"
      >
        Próxima
      </button>
    </div>
  </div>
</template>
