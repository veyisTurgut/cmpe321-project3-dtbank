  <template>
  <br /><br />
  <div class="flex-container">
    <div class="flex-child magenta">
      <b><mark> Add New User</mark></b
      ><br /><br />
      <form class="postForm" @submit.prevent="postNewUser">
        <p>username</p>
        <input type="text" v-model="user_body.username" />
        <p>realname</p>
        <input type="text" v-model="user_body.realname" />
        <p>institution</p>
        <input type="text" v-model="user_body.institution" />
        <p>password</p>
        <input type="password" v-model="user_body.password" />
        <br />
        <br />
        <button type="submit"><mark> Add</mark></button>
      </form>
    </div>

    <div class="flex-child green">
      <b><mark> Update Affinity </mark></b><br /><br />
      <form class="postForm" @submit.prevent="updateAffinity">
        <p>reaction_id</p>
        <input type="text" v-model="affinity_body.reaction_id" />
        <p>new affinity</p>
        <input type="text" v-model="affinity_body.affinity" />
        <br />
        <br />
        <button type="submit"><mark> Update </mark></button>
      </form>
    </div>
    <div class="flex-child green">
      <b><mark> Delete Drug </mark></b><br /><br />
      <form class="postForm" @submit.prevent="deleteDrug">
        <p>drugbank_id</p>
        <input type="text" v-model="drug_body.drugbank_id" />
        <br />
        <br />
        <button type="submit"><mark> Delete </mark></button>
      </form>
    </div>
    <div class="flex-child green">
      <b><mark> Delete Uniprot </mark></b><br /><br />
      <form class="postForm" @submit.prevent="deleteProt">
        <p>uniprot_id</p>
        <input type="text" v-model="prot_body.uniprot_id" />
        <br />
        <br />
        <button type="submit"><mark> Delete </mark></button>
      </form>
    </div>
    <div class="flex-child green">
      <b><mark> Update Contributors </mark></b>
      <br /><br />
      <form class="postForm" @submit.prevent="updateContributor">
        <!-- TODO -->
        <p>reaction_id</p>
        <input type="text" v-model="contributor_body.reaction_id" />
        <p>usernames</p>
        <textarea type="text" v-model="contributor_body.username" />
        <p>realnames</p>
        <textarea type="text" v-model="contributor_body.realname" />
        <p>passwords</p>
        <input type="password" v-model="contributor_body.password" />
        <br />
        <br />
        <button type="submit"><mark> Update </mark></button>
        <br /><br />
        <p>Please add comma separated values.</p>
        <p>Example: username1,username2,username3</p>
        <p>Example: realname1,realname2,realname3</p>
        <p>Example: password1,password2,password3</p>
      </form>
    </div>
    <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br />
  </div>

  <h1 v-if="success">Success</h1>
  <h1 v-if="fail">{{ this.error }}</h1>
</template>

<script>
import axios from "axios"

export default {
  data() {
    return {
      success: false,
      fail: false,
      error: null,
      searchQuery: "",
      searchError: null,
      user_body: {
        username: "",
        realname: "",
        institution: "",
        password: "",
      },
      drug_body: {
        drugbank_id: "",
      },
      prot_body: {
        uniprot_id: "",
      },
      affinity_body: {
        reaction_id: "",
        affinity: "",
      },
      contributor_body: {
        reaction_id: "",
        username: "",
        realname: "",
        password: "",
      },
    }
  },
  methods: {
    async postNewUser() {
      this.success = false
      this.fail = false
      this.error = null
      const url = `http://127.0.0.1:8000/users`
      const response = await axios
        .post(url, this.user_body)
        .then(value => {
          if (value.status == 200) {
            this.success = true
            this.fail = false
          }
        })
        .catch(value => {
          this.success = false
          this.fail = true
          this.error = value.response.data.detail
        })
    },
    async updateAffinity() {
      this.success = false
      this.fail = false
      this.error = null
      const url =
        `http://127.0.0.1:8000/reactions/` +
        this.affinity_body.reaction_id +
        `/affinity?affinity=` +
        this.affinity_body.affinity
      const response = await axios
        .put(url)
        .then(value => {
          if (value.status == 200) {
            this.success = true
            this.fail = false
          }
        })
        .catch(value => {
          this.success = false
          this.fail = true
          this.error = value.response.data.detail
        })
    },
    async deleteDrug() {
      this.success = false
      this.fail = false
      this.error = null
      const url = "http://127.0.0.1:8000/drugs/" + this.drug_body.drugbank_id
      const response = await axios
        .delete(url)
        .then(value => {
          if (value.status == 200) {
            this.success = true
            this.fail = false
          }
        })
        .catch(value => {
          this.success = false
          this.fail = true
          this.error = value.response.data.detail
        })
    },
    async deleteProt() {
      this.success = false
      this.fail = false
      this.error = null
      const url = `http://127.0.0.1:8000/prots/` + this.prot_body.uniprot_id
      const response = await axios
        .delete(url)
        .then(value => {
          if (value.status == 200) {
            this.success = true
            this.fail = false
          }
        })
        .catch(value => {
          this.success = false
          this.fail = true
          this.error = value.response.data.detail
        })
    },
    async updateContributor() {
      var username_arr = this.contributor_body.username.split(",")
      var realname_arr = this.contributor_body.realname.split(",")
      var password_arr = this.contributor_body.password.split(",")
      if (
        this.contributor_body.username == "" ||
        this.contributor_body.realname == "" ||
        this.contributor_body.password == "" ||
        this.contributor_body.reaction_id == ""
      ) {
        this.success = false
        this.fail = true
        this.error = "Fields can't be empty!"
      } else if (
        username_arr.length == realname_arr.length &&
        realname_arr.length == password_arr.length
      ) {
        var user_arr = []
        for (var i = 0; i < username_arr.length; i++) {
          user_arr.push({
            username: username_arr[i],
            realname: realname_arr[i],
            password: password_arr[i],
          })
        }
        this.success = false
        this.fail = false
        this.error = null
        const url =
          `http://127.0.0.1:8000/articles/` + this.contributor_body.reaction_id
        const response = await axios
          .put(url, user_arr) //todo
          .then(value => {
            if (value.status == 200) {
              this.success = true
              this.fail = false
            }
          })
          .catch(value => {
            this.success = false
            this.fail = true
            this.error = value.response.data.detail
          })
      } else {
        this.success = false
        this.fail = true
        this.error = "Please enter equal number of parameters!"
      }
    },
  },
}
</script>

<style>
.postForm {
  display: block;
}
.inline-block-child {
  display: inline-block;
}
.flex-container {
  display: flex;
}

.flex-child {
  flex: 1;
}
</style>
