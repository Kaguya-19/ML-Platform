<template>
  <page-header-wrapper title="Sample Model" :content="$t('model_test_guideline')">
    <!-- 选择菜单：模型概述/测试 -->
    <a-menu mode="horizontal">
      <a-menu-item @click="showPage('info')">Model infomation</a-menu-item>
      <a-menu-item @click="showPage('change')">Change model</a-menu-item>
      <a-menu-item @click="showPage('test')">Model test</a-menu-item>
      <a-menu-item @click="showPage('tasks')">Model services</a-menu-item>
    </a-menu>
    <!-- 模型概述 -->
    <template v-if="page == 'info'">
      <!-- 基本信息 -->

      <a-card :bordered="false">
        <a-row type="flex">
          <a-col flex="auto">
            <a-statistic title="Name" :value="modelName" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Type" :value="modelType" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Algorithm" :value="modelAlgorithm" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Engine" :value="modelEngine" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Added time" :value="modelTime" />
          </a-col>
        </a-row>
        <a-row type="flex" style="margin-top: 20px">
          <a-descriptions title="Description" v-if="modelDescription !== ''" :value="modelDescription">
            <a-descriptions-item>{{ modelDescription }}</a-descriptions-item>
          </a-descriptions>
        </a-row>
      </a-card>

      <!-- 输入/目标变量 -->
      <a-row type="flex" :gutter="16" style="margin-top: 20px">
        <a-col :span="12">
          <a-card title="Input variable" :bordered="false">
            <a-table :columns="inputColumns" :data-source="inputData" :rowKey="record => record.name">
            </a-table>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="output variable" :bordered="false">
            <a-table :columns="outputColumns" :data-source="outputData" :rowKey="record => record.name">
            </a-table>
          </a-card>
        </a-col>
      </a-row>
    </template>
    <!-- change -->
    <template v-if="page == 'change'">
      <a-form @submit="handleSubmit" :form="form">
        <a-form-item
          :label="$t('form.basic-form.title.label')"
          :labelCol="{ lg: { span: 7 }, sm: { span: 7 } }"
          :wrapperCol="{ lg: { span: 10 }, sm: { span: 17 } }">
          <a-input
            v-decorator="[
              'name',
              {
                rules: [{ required: true, message: $t('form.basic-form.title.required') }],
                initialValue: modelName
              }
            ]"
            name="name" />
        </a-form-item>
        <a-form-item
          :label="$t('form.basic-form.goal.label')"
          :labelCol="{ lg: { span: 7 }, sm: { span: 7 } }"
          :wrapperCol="{ lg: { span: 10 }, sm: { span: 17 } }">
          <a-textarea
            rows="4"
            v-decorator="[
              'description',
              {
                rules: [{ required: false }],
                initialValue: modelDescription
              }
            ]" />
        </a-form-item>
        <!-- 模型类型 -->
        <a-form-item
          label="Model type"
          :labelCol="{ lg: { span: 7 }, sm: { span: 7 } }"
          :wrapperCol="{ lg: { span: 10 }, sm: { span: 17 } }">
          <a-select
            v-decorator="['model_type', { rules: [{ required: true, message: 'Please choose your model type' }], initialValue: modelType }]">
            <a-select-option value="pmml">PMML</a-select-option>
            <a-select-option value="onnx">ONNX</a-select-option>
          </a-select>
        </a-form-item>
        <!-- 模型文件上传 -->
        <a-form-item
          label="Model file"
          :labelCol="{ lg: { span: 7 }, sm: { span: 7 } }"
          :wrapperCol="{ lg: { span: 10 }, sm: { span: 17 } }">
          <a-upload
            name="file"
            :file-list="fileList"
            :before-upload="beforeUpload"
            :multiplt="false"
            :max-count="1"
            v-decorator="['file']"
            :show-upload-list="{ showRemoveIcon: false }">
            <a-button>
              <a-icon type="upload" /> Select File
            </a-button>
          </a-upload>
        </a-form-item>
        <a-form-item :wrapperCol="{ span: 24 }" style="text-align: center">
          <a-button htmlType="submit" type="primary">{{ $t('form.basic-form.form.submit') }}</a-button>
          <!-- <a-button style="margin-left: 8px">{{ $t('form.basic-form.form.save') }}</a-button> -->
        </a-form-item>
      </a-form>
    </template>
    <!-- 模型测试 -->
    <template v-if="page == 'test'">
      <a-row type="flex" :gutter="16">
        <a-col :span="12">
          <a-card title="Input" :bordered="false" v-if="isJSON">
            <template #extra><a @click.stop="toJSON">Form</a></template>
            <a-textarea rows="6" v-model="jsonStr" />
            <!-- <a-button @click.prevent="reset">Clear</a-button> -->
            <a-button type="primary" @click.stop="submitJSON" style="margin-left: 16px">Submit</a-button>
          </a-card>
          <a-card title="Input" :bordered="false" v-else>
            <template #extra><a @click.stop="toJSON">JSON</a></template>
            <a-form @submit="testFormSubmit" :form="form">
              <a-form-item
                v-for="(data, index) in inputData"
                :key="index"
                :label="data.name + ' (Type:' + data.type + ')'">
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
    <!-- tasks -->
    <template v-if="page=='tasks'">
      <!-- todo -->
      <a-button @click.stop="deploy">Deploy</a-button>
      <a-row type="flex" :gutter="16">
        <s-table
          ref="table"
          size="default"
          :columns="columns"
          :data="loadData"
          :alert="{ show: true, clear: true }"
          :rowSelection="{ selectedRowKeys: this.selectedRowKeys, onChange: this.onSelectChange }"
          :rowKey="record => record.id"
        >
          <template v-for="(col, index) in columns" v-if="col.scopedSlots" :slot="col.dataIndex" slot-scope="text">
            <div :key="index">
              <template>{{ text }}</template>
            </div>
          </template>
          <template slot="action" slot-scope="text, record">
            <div class="editable-row-operations">
              <span>
                <a class="edit" @click="() => detail(record)">详情</a>
              </span>
            </div>
          </template>
        </s-table>

      </a-row>
    </template>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
import { STable } from '@/components'
var inputData = []
// 输入变量表格Column
const inputColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type'
  },
  {
    title: 'Shape',
    key: 'shape',
    dataIndex: 'shape'
  },
  {
    title: 'Sample',
    key: 'sample',
    dataIndex: 'sample'
  }
]
var outputData = []
// 目标变量表格Column
const outputColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type'
  },
  {
    title: 'Shape',
    key: 'shape',
    dataIndex: 'shape'
  }
]
export default {
  name: 'ModelTest',
  components: {
    STable
  },
  data () {
    return {
      // form: this.$form.createForm(this),
      model_id: this.$route.query.id,
      modelName: 'a',
      modelAlgorithm: 'MiningModel(classification)',
      modelEngine: 'PyPMML',
      modelType: 'PMML',
      modelTime: '2022-8-7 23:07',
      modelDescription: '',
      page: 'info',
      inputData,
      inputColumns,
      outputData,
      outputColumns,

      fileList: [],
      fileChanged: false,
      form: this.$form.createForm(this),
      testForm: this.$form.createForm(this),
      testRes: 'Here is result!',

      isFile: {},
      isJSON: false,
      jsonStr: 'aa',
      testFileList: [],

      columns: [
        {
          title: 'Service number',
          dataIndex: 'id',
          key: 'id'
        },
        {
          title: 'Name',
          dataIndex: 'name',
          key: 'name'
        },
        // {
        //   title: 'Description',
        //   dataIndex: 'description'
        // },
        {
          title: 'Status',
          dataIndex: 'status',
          key: 'status'
        },
        // {
        //   title: 'Added time',
        //   dataIndex: 'time'
        // },
        {
          title: 'Type',
          dataIndex: 'model_type'
        },
        {
          title: 'Operation',
          table: 'Operation',
          dataIndex: 'action',
          scopedSlots: { customRender: 'action' }
        }
      ],
      // 加载数据方法 必须为 Promise 对象
      loadData: parameter => {
        return axios.get('/ml/deploy', {
          params: Object.assign(parameter, { 'mod': this.model_id })
        }).then(res => {
            console.log(res.data)
            return res.data.result
            }).catch(err => {
            console.log(err)
            if ('errmsg' in err.response.data) {
              this.$message.error(err.response.data.errmsg)
            } else {
              this.$message.error('read failed.')
              }
      })
      }
    }
  },

  beforeMount () {
    this.getInfo()
  },
  methods: {
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
    getInfo () {
      axios.get(`/ml/model/${this.model_id}`)
        .then(res => {
          this.modelName = res.data.name
          this.modelAlgorithm = res.data.algorithm
          this.modelEngine = res.data.engine
          this.modelType = res.data.model_type
          this.modelTime = res.data.addTime
          if (res.data.description !== 'undefined') {
            this.modelDescription = res.data.description
          }
          this.inputData = res.data.input
          var jsonJson = {}
          this.isFile = []
          this.testFileList = []
          this.testFileDic = {}
          for (let i = 0; i < this.inputData.length; i++) {
            jsonJson[this.inputData[i].name] = ''
            this.isFile[this.inputData[i].name] = false
            if ('shape' in this.inputData[i]) {
              this.inputData[i].shape = '[' + String(this.inputData[i].shape) + ']'
            }
          }
          this.jsonStr = JSON.stringify(jsonJson)
          this.outputData = res.data.output
          for (let i = 0; i < this.outputData.length; i++) {
            if ('shape' in this.outputData[i]) {
              this.outputData[i].shape = '[' + String(this.outputData[i].shape) + ']'
            }
          }
          this.fileList = [{
            uid: '-1',
            name: res.data.file.split('/').slice(-1)[0],
            status: 'done',
            url: res.data.file
          }]
        }).catch(err => {
          console.log(err)
          if ('errmsg' in err.response.data) {
            this.$message.error(err.response.data.errmsg)
          } else {
            this.$message.error('read failed.')
          }
        })
    },
    beforeUpload (file) {
      this.fileList = [file]
      this.fileChanged = true
      return false
    },
    testBeforeUpload (file) {
      this.testFileList.push(file)
      this.fileChanged = true
      return false
    },
    handleSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          var formData = new FormData()
          console.log(values)
          if (this.fileChanged) {
            formData.append('file', values['file'].file)
          }
          for (var v in values) {
            if (v !== 'file') {
              formData.append(v, values[v])
            }
          }
          console.log(values)
          // console.log('Received values of form: ', values)
          // formData.forEach((key, val) => {
          //   console.log('key %s: value %s', key, val)
          // })
          axios({
            url: `/ml/model/${this.model_id}`,
            method: 'put',
            processData: false,
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
          }).then(res => {
            this.$message.success('upload successfully.')
            this.$router.go(0)
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
            url: `/ml/test/quick/${this.model_id}`, // TODO
            method: 'post',
            processData: false,
            data: formData
          }).then(res => {
            this.$message.success('upload successfully.')
            console.log(res.data)
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
      const formData = new FormData()
      Object.keys(jsonJson).forEach((key) => {
      formData.append(key, jsonJson[key])
      })
      axios({
        url: `/ml/test/quick/${this.model_id}`, // TODO
        method: 'post',
        processData: false,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        data: jsonJson
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
    },
    showPage (key) {
      this.page = key
      this.getInfo()
      console.log('page:', this.page)
    },
    deploy () {
      this.$router.push({ path: '/deploy/deploy-add', query: { id: this.model_id } })
    },
    detail (row) {
      console.log(row.id)
      this.$router.push({ path: '/deploy/deploy-test', query: { id: row.id } })
      // row = Object.assign({}, row)
    }
  }
}
</script>

<style scoped>
</style>
