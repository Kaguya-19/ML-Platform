<template>
  <page-header-wrapper :title="false" content="Enter model information.">
    <a-spin :spinning="spinning">
      <a-card :body-style="{padding: '24px 32px'}" :bordered="false">
        <!-- 模型名称 -->
        <a-form @submit="handleSubmit" :form="form">
          <a-form-item
            label="Name"
            :labelCol="{lg: {span: 7}, sm: {span: 7}}"
            :wrapperCol="{lg: {span: 10}, sm: {span: 17} }">
            <a-input
              v-decorator="[
                'name',
                {rules: [{ required: true, message: 'Please enter a name.' }]}
              ]"
              name="name"/>
          </a-form-item>
          <a-form-item
            label="Description"
            :labelCol="{lg: {span: 7}, sm: {span: 7}}">
            <a-textarea
              :auto-size="{ minRows: 3, maxRows: 10 }"
              v-decorator="[
                'description',
                {rules: [{ required: false }], initialValue: ''}
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
              <a-select-option value="keras">Keras</a-select-option>
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
              :max-count="1"
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
      fileList: [],
      form: this.$form.createForm(this),
      spinning: false
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
          this.spinning = true
          var formData = new FormData()
          formData.append('file', values['file'].file)
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
                this.spinning = false
                this.$message.success('Upload successfully.')
                this.$router.push('/model/model-list')
              }).catch(err => {
              console.log(err)
              this.spinning = false
              try {
                this.$message.error(err.response.data.errmsg)
              } catch (err) {
                this.$message.error('Upload failed.')
                }
            })
        }
      })
    }
  }
}
</script>
