<template>
    <div class="p-6 max-w-2xl mx-auto">
      <form @submit.prevent="submitForm" class="space-y-4">
        <textarea
          v-model="userDescription"
          placeholder="Tell us about yourself, your skills, and what you're looking for..."
          class="w-full p-2 border rounded"
        ></textarea>
  
        <input
          type="file"
          @change="handleFileChange"
          accept=".csv,.pdf,.doc,.docx"
          class="w-full p-2 border rounded"
        />
  
        <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded">
          Submit
        </button>
      </form>
  
      <div v-if="recommendations.length" class="mt-6">
        <h2 class="text-xl font-bold mb-2">Recommended Vacancies</h2>
        <ul class="space-y-2">
          <li v-for="(job, index) in recommendations" :key="index" class="p-4 border rounded">
            <a :href="job.url" target="_blank" class="text-blue-500 hover:underline">
              {{ job.title }}
            </a> 
            <p class="text-sm text-gray-600">{{ job.snippet }}</p>
            <p class="mt-2 text-sm text-green-700 italic" v-if="job.reason">
            Why this job is good for u: {{ job.reason }}
            </p>
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  
  const userDescription = ref("");  // Flexible user input
  const file = ref(null);
  const recommendations = ref([]);  // Store job recommendations
  
  const handleFileChange = (event) => {
    file.value = event.target.files[0];
  };
  
  const submitForm = async () => {
    console.log("Submitting:", userDescription.value)                                       // Debug log
    const formData = new FormData();
    formData.append("user_text", userDescription.value || ""); // Send user description
  
    if (file.value) {
      formData.append("file", file.value);
    }
  
    try {
      const response = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        body: formData,
      });
  
      const data = await response.json();
      console.log("Data received:", data)                                            // Debug log
      recommendations.value = data.recommended_jobs || [];  // Display job results
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };
  </script>