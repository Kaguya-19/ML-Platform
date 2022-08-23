<template>
  <page-header-wrapper :title="false" content="Deploy Service">
    <a-spin :spinning="spinning">
      <a-card :body-style="{padding: '24px 32px'}" :bordered="false">
        <a-form @submit="handleSubmit" :form="form">
          <a-form-item
            label="Model ID"
            :labelCol="{lg: {span: 7}, sm: {span: 7}}"
            :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
            <a-input
              v-decorator="[
                'model_id',
                {rules: [{ required: true, message: 'Please enter model id.' }], initialValue: model_id}
              ]"
              name="name"
              disabled="true" />
          </a-form-item>
          <a-form-item
            label="Name"
            :labelCol="{lg: {span: 7}, sm: {span: 7}}"
            :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
            <a-input
              v-decorator="[
                'name',
                {rules: [{ required: true, message: 'Please enter name.' }]}
              ]"
              name="name"/>
          </a-form-item>
          <a-form-item
            label="Description"
            :labelCol="{lg: {span: 7}, sm: {span: 7}}"
            :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
            <a-textarea
              :auto-size="{ minRows: 3, maxRows: 10 }"
              v-decorator="[
                'description',
                {rules: [{ required: false }], initialValue: ''}
              ]" />
          </a-form-item>
          <a-form-item
            :wrapperCol="{ span: 24 }"
            style="text-align: center"
          >
            <a-button htmlType="submit" type="primary">Submit</a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </a-spin>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ModelAdd',
  data () {
    return {
      model_id: this.$route.query.id,
      form: this.$form.createForm(this),
      spinning: false
    }
  },
  methods: {
    handleSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          this.spinning = true
          var formData = new FormData()
          for (var v in values) {
            formData.append(v, values[v])
          }
          axios({
            url: '/ml/deploy',
            method: 'post',
            processData: false,
            data: formData
            }).then(res => {
                this.spinning = false
                this.$message.success('Deploy successfully.')
                this.$router.push('/deploy/deploy-list')
              }).catch(err => {
              this.spinning = false
              console.log(err)
              try {
                this.$message.error(err.response.data.errmsg)
              } catch (err) {
                this.$message.error('Deploy failed.')
                }
            })
        }
      })
    }
  }
}
</script>
