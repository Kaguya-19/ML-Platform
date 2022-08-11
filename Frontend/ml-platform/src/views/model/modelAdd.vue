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
            v-decorator="['model_type', { rules: [{required: true, message: 'Please choose your model type'}] }]">
            <a-select-option value="pmml">PMML</a-select-option>
            <a-select-option value="onnx">ONNX</a-select-option>
          </a-select>
        </a-form-item>
        <!-- 模型文件上传 -->
        <a-form-item
          label="Model file"
          :labelCol="{lg: {span: 7}, sm: {span: 7}}"
          :wrapperCol="{lg: {span: 10}, sm: {span: 17}}"
        >
          <a-upload
            name="file"
            :file-list="fileList"
            :before-upload="beforeUpload"
            :multiplt="false"
            :remove="handleRemove"
            v-decorator="['file', {rules: [{required: true, message: 'Please upload your model file'}]}]"
          >
            <a-button> <a-icon type="upload" /> Select File </a-button>
          </a-upload>
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
      fileList: [],
      form: this.$form.createForm(this)
    }
  },
  methods: {
    handleRemove (file) {
      this.fileList = []
    },
    beforeUpload (file) {
      this.fileList = [file]
      return false
    },
    handleSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          var formData = new FormData()
          console.log(this.form)
          formData.append('file', this.fileList[0])
          for (var v in values) {
           if (v !== 'file') {
            formData.append(v, values[v])
            }
          }
          // console.log('Received values of form: ', values)
          // formData.forEach((key, val) => {
          //   console.log('key %s: value %s', key, val)
          // })
          axios({
            url: '/ml/model',
            method: 'post',
            processData: false,
            headers: {
               'Content-Type': 'multipart/form-data'
            },
            data: formData
            }).then(res => {
                this.$message.success('upload successfully.')
                this.$router.push('/model/model-list')
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
