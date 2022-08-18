<template>
  <page-header-wrapper title="Sample Service" :content="$t('model_test_guideline')">
    <!-- 选择菜单：部署概述/测试 -->
    <a-menu mode="horizontal">
      <a-menu-item @click="showPage('info')">Service infomation</a-menu-item>
      <a-menu-item @click="showPage('test')">Service test</a-menu-item>
    </a-menu>
    <!-- 部署概述 -->
    <template v-if="page=='info'">
      <!-- 基本信息 -->
      <a-card :bordered="false" title="Indicators">

        <a-table :columns="funcColumns" :data-source="funcData">
        </a-table>
      </a-card>
      <!-- TODO -->
      <!-- <a-card :bordered="false" title="Copy" style="margin-top: 20px">
        <a-table :columns="copyColumns" :data-source="copyData">
        </a-table>
      </a-card> -->
    </template>
    <!-- 部署测试 -->
    <template v-if="page=='test'">
      <a-row type="flex" :gutter="16">
        <a-col :span="12">
          <a-card title="Input" :bordered="false" v-if="isJSON">
            <template #extra><a @click.stop="toJSON">Form</a></template>
            <a-textarea
              rows="6"
              v-model="jsonStr"
            />
            <!-- <a-button @click.prevent="reset">Clear</a-button> -->
            <a-button type="primary" @click.stop="submitJSON" style="margin-left: 16px">Submit</a-button>
          </a-card>
          <a-card title="Input" :bordered="false" v-else>
            <template #extra><a @click.stop="toJSON">JSON</a></template>
            <a-form @submit="testFormSubmit" :form="form">
              <a-form-item v-for="(data, index) in inputData" :key="index" :label="data.name+' (Type:'+data.type+')'">
                <!-- todo:upload -->
                <a-switch
                  :check="isFile[data.name]"
                  :v-model="isFile[data.name]"
                  checkedChildren="File"
                  unCheckedChildren="Text"
                  @change="chooseForT(data.name)"/>
                <a-form-item v-if="isFile[data.name]">
                  <a-upload
                    :before-upload="testBeforeUpload"
                    :multiplt="false"
                    :max-count="1"
                    :name="data.name"
                    v-decorator="[data.name, { rules: [{required: true, message: 'Please give input'}]}]"
                  >
                    <a-button> <a-icon type="upload" /> Select File </a-button>
                  </a-upload>
                </a-form-item>
                <a-form-item v-else>
                  <a-textarea
                    rows="2"
                    v-decorator="[data.name, { rules: [{required: true, message: 'Please give input'}]}]"
                  />
                </a-form-item>
                <!-- <a-textarea
                  rows="2"
                  v-decorator="[data.name, { rules: [{required: true, message: 'Please give input'}]}]"
                  v-else
                /> -->
              </a-form-item>
              <a-form-item :wrapper-col="{ span: 14, offset: 15 }">
                <!-- <a-button @click.prevent="reset">Clear</a-button> -->
                <a-button type="primary" htmlType="submit" style="margin-left: 16px">Submit</a-button>
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="Output" :bordered="false">
            <textarea style="border: none" :value="testRes">
            </textarea>
          </a-card>
        </a-col>
      </a-row>
    </template>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
// 输入变量表格Column
const funcColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'Create Time',
    dataIndex: 'create_time',
    key: 'create_time'
  },
  {
    title: 'Average(s)',
    key: 'average_use_time',
    dataIndex: 'average_use_time'
  },
  // {
  //   title: 'Median(ms)',
  //   key: 'medResTime',
  //   dataIndex: 'medResTime'
  // },
  //   {
  //   title: 'Min(ms)',
  //   key: 'minResTime',
  //   dataIndex: 'minResTime'
  // },
  //   {
  //   title: 'Max(ms)',
  //   key: 'maxResTime',
  //   dataIndex: 'maxResTime'
  // },
    {
    title: 'Invoke Times',
    key: 'use_times',
    dataIndex: 'use_times'
  },
    {
    title: 'Latest visit',
    key: 'recent_modified_time',
    dataIndex: 'recent_modified_time'
  }
]
const copyData = [
  {
    key: '1',
    copyName: 'd-pmml-xgb-iris-svc-5954487d5b-zbsjn',
    status: 'working',
    operation: '...'
  }
]
// 输入变量表格Column
const copyColumns = [
  {
    title: 'Copy',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'status',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: 'Operation',
    key: 'operation',
    dataIndex: 'operation'
  }
]
export default {
  name: 'ModelTest',
  data () {
    return {
      deploy_id: this.$route.query.id,
      model_id: 0,
      serviceStatus: '',
      serviceDescription: '',
      page: 'info',
      funcData: [],
      funcColumns,
      copyData,
      copyColumns,

      inputData: [],
      isJSON: false,
      jsonStr: 'aa',
      testFileList: [],
      isFile: {},
      form: this.$form.createForm(this),
      testRes: 'Here is result!'
    }
  },
  beforeMount () {
    this.getInfo()
  },
  methods: {
    getInfo () {
      axios.get(`/ml/deploy/${this.deploy_id}`)
          .then(res => {
            this.funcData.push(res.data)
            this.model_id = res.data.mod
            console.log(this.funcData)
            if (res.data.description !== 'undefined') {
              this.serviceDescription = res.data.description
            }
            this.getModelInfo()
            }).catch(err => {
            console.log(err)
            if ('errmsg' in err.response.data) {
              this.$message.error(err.response.data.errmsg)
            } else {
              this.$message.error('read failed.')
              }
          })
    },
    showPage (key) {
      this.page = key
      console.log('page:', this.page)
    },
    chooseForT (checked) {
      this.isFile[checked] = !this.isFile[checked]
      this.isJSON = !this.isJSON
      this.isJSON = !this.isJSON
      this.form.resetFields(checked)
    },
    toJSON () {
      for (var v in this.isFile) {
        this.isFile[v] = false
      }
      this.isJSON = !this.isJSON
      },
    // handler
    getModelInfo () {
      axios.get(`/ml/model/${this.model_id}`)
          .then(res => {
            // this.modelName = res.data.name
            // this.modelAlgorithm = res.data.algorithm
            // this.modelEngine = res.data.engine
            // this.modelType = res.data.model_type
            // this.modelTime = res.data.addTime
            // if (res.data.description !== 'undefined') {
            //   this.modelDescription = res.data.description
            // }
            this.inputData = res.data.input
            var jsonJson = {}
            // this.isFile = []
            this.testFileList = []
            // this.testFileDic = {}
            for (let i = 0; i < this.inputData.length; i++) {
              jsonJson[this.inputData[i].name] = ''
              this.isFile[this.inputData[i].name] = false
              if ('shape' in this.inputData[i]) {
              this.inputData[i].shape = '[' + String(this.inputData[i].shape) + ']'
            }
            }
            this.jsonStr = JSON.stringify(jsonJson)
            }).catch(err => {
            console.log(err)
            if ('errmsg' in err.response.data) {
              this.$message.error(err.response.data.errmsg)
            } else {
              this.$message.error('read failed.')
              }
          })
    },
    testBeforeUpload (file) {
      return false
    },
    testFormSubmit (e) {
      e.preventDefault()
      console.log(this.form)
      this.form.validateFields((err, values) => {
        if (!err) {
          var formData = new FormData()
          console.log(values)
          for (var v in values) {
           try {
            formData.append(v, values[v].file)
           } catch (err) {
            console.log(err)
            formData.append(v, values[v])
           }
          }
          console.log(values) // TODO: waiting anime
          axios({
            url: `/ml/deploy/${this.service_id}`,
            method: 'post',
            processData: false,
            params:{
              'type': 'fast'
            },
            data: formData
            }).then(res => {
                this.$message.success('upload successfully.')
                this.testRes = JSON.stringify(res.data)
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
    },
    submitJSON () {
      try {
      var jsonJson = JSON.parse(this.jsonStr)
      } catch (err) {
        console.log(err)
        this.$message.error('json error.')
      }
      console.log(jsonJson)
      axios({
            url: `/ml/deploy/${this.service_id}`,
            method: 'post',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: jsonJson,
            }).then(res => {
                this.$message.success('upload successfully.')
                this.testRes = JSON.stringify(res.data)
              }).catch(err => {
              console.log(err)
              if ('errmsg' in err.response.data) {
                this.$message.error(err.response.data.errmsg)
              } else {
                this.$message.error('upload failed.')
                }
            })
    }
  }
}
</script>

<style scoped>
</style>
