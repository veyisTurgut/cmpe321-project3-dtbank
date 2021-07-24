
<template>
  <!--  <form id="searchBar" @submit.prevent="search">
    <input type="text" v-model="searchQuery" />
    <button type="submit"><i class="fa fa-search"></i></button>
  </form>-->

  <div class="login">
    <b><mark> User Login </mark></b><br />
    <form v-if="!sent" class="postForm" @submit.prevent="postUserLogin">
      <p>username</p>
      <input type="text" v-model="user_body.username" />
      <p>institution</p>
      <input type="text" v-model="user_body.institution" />
      <p>password</p>
      <input type="password" v-model="user_body.password" />
      <br />
      <button type="submit"><mark> Login</mark></button>
    </form>
    <br /><br /><br /><br />
    <b><mark> DBManager Login </mark></b><br />
    <form v-if="!sent" class="postForm" @submit.prevent="postDBLogin">
      <p>username</p>
      <input type="text" v-model="db_body.username" />
      <p>password</p>
      <input type="password" v-model="db_body.password" />
      <br />
      <button type="submit"><mark> Login</mark></button>
    </form>
    <h1 v-if="success">Success</h1><br />
    <h1 v-if="success">Account activated for next 30 minutes.</h1>
    <h1 v-if="fail">{{ this.error }}</h1>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      sent: false,
      success: false,
      fail: false,
      error: null,
      searchQuery: "",
      searchError: null,
      user_body: {
        username: "",
        institution: "",
        password: "",
      },
      db_body: {
        username: "",
        password: "",
      },
    };
  },
  methods: {
    async postUserLogin() {
      this.sent = false;
      this.success = false;
      this.fail = false;
      this.error = null;
      const url = `http://127.0.0.1:8000/users/login`;
      const response = await axios
        .post(url, this.user_body)
        .then((value) => {
          if (value.status == 200) {
            this.success = true;
            this.fail = false;
          }
        })
        .catch((value) => {
          this.success = false;
          this.fail = true;
          this.error = value.response.data;
        });
      if(this.success){
        this.sent = true
      }

    },
    async postDBLogin() {
      this.sent = false;
      this.success = false;
      this.fail = false;
      this.error = null;
      const url = `http://127.0.0.1:8000/database_managers/login`;
      const response = await axios
        .post(url, this.db_body)
        .then((value) => {
          if (value.status == 200) {
            this.success = true;
            this.fail = false;
          }
        })
        .catch((value) => {
          this.success = false;
          this.fail = true;
          this.error = value.response.data;
        });
      if(this.success){
        this.sent = true
      }
    },
  },
};
</script>

<style>
.postForm {
  display: block;
}
</style>
