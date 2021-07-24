<template>
  <Layout>
    <h2 class="mb-8 text-4xl font-bold text-center capitalize">
      Path: <span class="text-green-700">{{ header(section) }}</span>
    </h2>
    <ResponseFilter v-model="section" :fetch="fetchResponse" />
    <ResponseList v-if="!loading && !error" :posts="posts" />
    <!-- Start of loading animation -->
    <div class="mt-40" v-if="loading">
      <p class="text-6xl font-bold text-center text-gray-500 animate-pulse">
        Loading...
      </p>
    </div>
    <!-- End of loading animation -->

    <!-- Start of error alert -->
    <div class="mt-12 bg-red-50" v-if="error">
      <h3 class="px-4 py-1 text-4xl font-bold text-white bg-red-800">
        {{ error.title }}
      </h3>
      <p class="p-4 text-lg font-bold text-red-900">{{ error.message }}</p>
    </div>
    <!-- End of error alert -->
  </Layout>
</template>

<script>
import axios from "axios"
import Layout from "../components/Layout.vue"
import ResponseFilter from "../components/DBResponseFilterget.vue"
import ResponseList from "../components/ResponseList.vue"

export default {
  components: {
    Layout,
    ResponseFilter,
    ResponseList,
  },
  data() {
    return {
      section: [],
      posts: [],
      loading: false,
      error: null,
    }
  },
  methods: {
    extractImage(post) {
      const defaultImg = {
        url: "http://placehold.it/210x140?text=N/A",
        caption: post.title,
      }
      return defaultImg
    },
    header(value) {
      if (!value) return ""
      value = value.toString()
      return value
    },
    async fetchResponse() {
      const possible_paths = [
        "/siders" /* + */,
        "/drugs" /* + */,
        "/users" /* + */,
        "/prots" /* + */,
        "/reactions/articles" /* + */,
        "/drugtargets"/* */

      ]

      const headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      }

      try {
        this.error = null
        this.loading = true

        if (possible_paths.some(v => this.section.includes(v))) {
          const response = axios
            .get("http://127.0.0.1:8000" + this.section + "/", { headers })
            .then(value => {
              if (this.section == "/siders") {
                /*possible options:
                  # 6"/siders" + 
                */
                this.posts = value.data.items.map(post => ({
                  umls_cui: post.umls_cui,
                  side_effect_name: post.side_effect_name,
                }))
              } else if (this.section == "/drugs") {
                /*possible options:
                  # 6 "/drugs" + 
                */
                this.posts = value.data.items.map(post => ({
                  drugbank_id: post.drugbank_id,
                  drug_name: post.drug_name,
                  smiles: post.smiles,
                  description: post.description,
                }))
              } else if (this.section.startsWith("/users")) {
                /*possible options:
                  # 6 "/users" + 
                */
                if (this.section == "/users") {
                  this.posts = value.data.items.map(post => ({
                    username: post.username,
                    realname: post.realname,
                    institution: post.institution,
                  }))
                }
              } else if (this.section == "/prots") {
                /*possible options:
                  # 6 "/prots" +
                */
                this.posts = value.data.items.map(post => ({
                  uniprot_id: post.uniprot_id,
                  target_name: post.target_name,
                  sequence: post.sequence,
                }))
              } else if (this.section == "/reactions/articles") {
                /*possible options:
                  # 6 "/reactions"
                */
               this.posts = value.data.items.map(post => ({
                  doi: post.doi,
                  contributors: post.contributors,
                }))
              } else if (this.section == "/drugtargets"){
                this.posts = value.data.items.map(post => ({
                  drugbank_id: post.drugbank_id,
                  uniprot_id: post.uniprot_id,
                }))
              }
            })
            .catch(reason => {
              this.posts = [
                {
                  status: reason.response.status,
                  statusText: reason.response.statusText,
                  detail: reason.response.data.detail,
                },
              ]
            })
        }
      } catch (err) {
        if (err.response) {
          // client received an error response (5xx, 4xx)
          this.error = {
            title: "Server Response",
            message: err.message,
          }
        } else if (err.request) {
          // client never received a response, or request never left
          this.error = {
            title: "Unable to Reach Server",
            message: err.message,
          }
        } else {
          // There's probably an error in your code
          this.error = {
            title: "Application Error",
            message: err.message,
          }
        }
      }
      this.loading = false
    },
  },
  mounted() {
    this.fetchResponse()
  },
}
</script>
