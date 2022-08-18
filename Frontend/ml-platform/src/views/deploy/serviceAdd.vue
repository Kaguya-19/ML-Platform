<template>
  <page-header-wrapper :title="false" :content="$t('form.basic-form.basic.description')">
    <a-card :body-style="{padding: '24px 32px'}" :bordered="false">
      <!-- 模型名称 -->
      <a-form @submit="handleSubmit" :form="form">
        <a-form-item
          label="Mode _id"
          :labelCol="{lg: {span: 7}, sm: {span: 7}}"
          :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
          <a-input
            v-decorator="[
              'model_id',
              {rules: [{ required: true, message: $t('form.basic-form.title.required') }], initialValue: model_id}
            ]"
            name="name"
            disabled="true" />
        </a-form-item>
        <a-form-item
          :label="$t('form.basic-form.title.label')"
          :labelCol="{lg: {span: 7}, sm: {span: 7}}"
          :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
          <a-input
            v-decorator="[
              'name',
              {rules: [{ required: true, message: $t('form.basic-form.title.required') }]}
            ]"
            name="name"
            :placeholder="$t('form.basic-form.title.placeholder')" />
        </a-form-item>
        <a-form-item
          :label="$t('form.basic-form.goal.label')"
          :labelCol="{lg: {span: 7}, sm: {span: 7}}"
          :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
          <a-textarea
            rows="4"
            :placeholder="$t('form.basic-form.goal.placeholder')"
            v-decorator="[
              'description',
              {rules: [{ required: false }]}
            ]" />
        </a-form-item>
        <a-form-item
          :wrapperCol="{ span: 24 }"
          style="text-align: center"
        >
          <a-button htmlType="submit" type="primary">{{ $t('form.basic-form.form.submit') }}</a-button>
          <!-- <a-button style="margin-left: 8px">{{ $t('form.basic-form.form.save') }}</a-button> -->
        </a-form-item>
      </a-form>
    </a-card>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ModelAdd',
  data () {
    return {
      model_id: this.$route.query.id,
      form: this.$form.createForm(this)
    }
  },
  methods: {
    handleSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          var formData = new FormData()
          for (var v in values) {
            formData.append(v, values[v])
          }
          axios({
            url: '/ml/deploy',
            method: 'post',
            processData: false,
            headers: {
               'Content-Type': 'multipart/form-data'
            },
            data: formData
            }).then(res => {
                this.$message.success('deploy successfully.')
                this.$router.push('/deploy/deploy-list')
              }).catch(err => {
              console.log(err)
              if ('errmsg' in err.response.data) {
                this.$message.error(err.response.data.errmsg)
              } else {
                this.$message.error('upload failed.')
                }
            })
        }
      })
    }
  }
}
</script>
