<template>
  <page-header-wrapper :title="false" :content="$t('form.basic-form.basic.description')">
    <a-card :body-style="{padding: '24px 32px'}" :bordered="false">

      <!-- 模型名称 -->
      <a-form @submit="handleSubmit" :form="form">
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
        <!-- 模型类型 -->
        <a-form-item
          label="Model type"
          :labelCol="{lg: {span: 7}, sm: {span: 7}}"
          :wrapperCol="{lg: {span: 10}, sm: {span: 17}}"
        >
          <a-select
            placeholder="Please choose your model type"
            v-decorator="['paymentUser', { rules: [{required: true, message: '付款账户必须填写'}] }]">
            <a-select-option value="1">PMML</a-select-option>
            <a-select-option value="2">ONNX</a-select-option>
          </a-select>
        </a-form-item>
        <!-- 模型文件上传 -->
        <a-form-item
          label="Model file"
          :labelCol="{lg: {span: 7}, sm: {span: 7}}"
          :wrapperCol="{lg: {span: 10}, sm: {span: 17}}"
        >
          <a-upload name="file" :beforeUpload="beforeUpload" :showUploadList="false">
            <a-button icon="upload">Select from local</a-button>
          </a-upload>
          <a-input
            disabled="true"
            :style="{width: 'calc(100% - 162.39px)'}"
            v-decorator="['payType', {rules: [{required: true, message: 'Please upload your model file'}]}]"
          />
        </a-form-item>
        <a-form-item
          :wrapperCol="{ span: 24 }"
          style="text-align: center"
        >
          <a-button htmlType="submit" type="primary">{{ $t('form.basic-form.form.submit') }}</a-button>
          <a-button style="margin-left: 8px">{{ $t('form.basic-form.form.save') }}</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </page-header-wrapper>
</template>

<script>
export default {
  name: 'ModelAdd',
  data () {
    return {
      form: this.$form.createForm(this)
    }
  },
  methods: {
    // handler
    handleSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          console.log('Received values of form: ', values)
        }
      })
    }
  }
}
</script>
