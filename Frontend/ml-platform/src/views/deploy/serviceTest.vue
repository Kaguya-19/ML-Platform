<template>
  <page-header-wrapper :title="serviceName">
    <!-- 选择菜单：部署概述/测试 -->
    <a-menu mode="horizontal">
      <a-menu-item @click="showPage('info')">Service infomation</a-menu-item>
      <a-menu-item @click="showPage('test')">Fast test</a-menu-item>
      <a-menu-item @click="showPage('task')">Task</a-menu-item>
      <a-menu-item @click="showPage('pro')">Preprocess</a-menu-item>
      <a-menu-item @click="showPage('list')">List</a-menu-item>
    </a-menu>
    <!-- 部署概述 -->
    <a-spin :spinning="spinning">
      <template v-if="page=='info'">
        <!-- 基本信息 -->
        <a-card :bordered="false" title="Indicators">
          <template #extra><a :href="&quot;/model/model-test?id=&quot;+model_id">Model</a></template>
          <a-row>
          <a-descriptions title="How to use">
            <a-descriptions-item>wait return:add/task at end of url,POST: file:yourfile<br/>fast test:POST: input<br/>PUT status:'paused'\'deployed'\'undeployed'<br/>get info:GET
            </a-descriptions-item>
          </a-descriptions>
          <a-button @click="deploy" v-if="serviceStatus!='deployed'">Deploy</a-button>
          <a-button @click="undeploy" v-if="serviceStatus!='undeployed'">Undeploy</a-button>
          <a-button @click="pause" v-if="serviceStatus!='paused'">Pause</a-button>
          </a-row>
          <br/>
          <a :href="&quot;http://&quot;+baseUrl+&quot;/ml/deploy/&quot;+deploy_id">{{ baseUrl }}/ml/deploy/{{ deploy_id }}</a>
          <a-table :columns="funcColumns" :data-source="funcData">
          </a-table>
          <a-descriptions title="Description" v-if="serviceDescription !== ''" :value="serviceDescription" style="white-space: pre-wrap;">
            <a-descriptions-item>{{ serviceDescription }}</a-descriptions-item>
          </a-descriptions>
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
                :auto-size="{ minRows: 3, maxRows: 10 }"
                v-model="jsonStr"
              />
              <!-- <a-button @click.prevent="reset">Clear</a-button> -->
              <a-button type="primary" @click="submitJSON" style="margin-left: 16px">Submit</a-button>
              <a-button type="primary" @click="jsonCurl" style="margin-left: 16px">Curlcode</a-button>
            </a-card>
            <a-card title="Input" :bordered="false" v-else>
              <template #extra><a @click.stop="toJSON">JSON</a></template>
              <a-form @submit="testFormSubmit" :form="form">
                <a-form-item v-for="(data, index) in inputData" :key="index" :label="data.name+' (Type:'+data.type+')'">
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
                      :auto-size="{ minRows: 1, maxRows: 10 }"
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
                  <a-button type="primary" @click="formCurl" style="margin-left: 16px">Curlcode</a-button>
                </a-form-item>
              </a-form>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="Output" :bordered="false" v-if="page=='test'">
              <a-textarea :auto-size="{ minRows: 3, maxRows: 10 }" style="border: none" :defaultValue="testRes" v-if="!spinning">
              </a-textarea>
            </a-card>
          </a-col>
        </a-row>
      </template>
      <template v-if="page=='task'">
        <a-row type="flex" :gutter="16">
          <a-col :span="12">
            <a-card title="Input" :bordered="false">
              <a-form @submit="taskFormSubmit" :form="form">
                <a-form-item
                  label="Description"
                  >
                  <a-textarea
                    :auto-size="{ minRows: 3, maxRows: 10 }"
                    v-decorator="[
                      'description',
                      {
                        rules: [{ required: false }],
                        initialValue: ''
                      }
                    ]" />
                </a-form-item>
                <a-form-item label="File">
                  <a-upload
                    :before-upload="testBeforeUpload"
                    :multiplt="false"
                    :max-count="1"
                    v-decorator="['file', { rules: [{required: true, message: 'Please give input'}]}]"
                  >
                    <a-button> <a-icon type="upload" /> Select File </a-button>
                  </a-upload>
                </a-form-item>
                <a-form-item :wrapper-col="{ span: 14, offset: 15 }">
                  <!-- <a-button @click.prevent="reset">Clear</a-button> -->
                  <a-button type="primary" htmlType="submit" style="margin-left: 16px">Submit</a-button>
                </a-form-item>
              </a-form>
            </a-card>
          </a-col>
          <a-col :span="12">
          </a-col>
        </a-row>
      </template>
      <template v-if="page=='list'">
          <s-table
            ref="table"
            size="default"
            :columns="columns"
            :data="loadData"
            :alert="{ show: true, clear: true }"
            :rowSelection="{ selectedRowKeys: this.selectedRowKeys }"
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
                  <a class="edit" @click="() => detail(record)">Detail</a>
                </span>
              </div>
            </template>
          </s-table>
      </template>
      <template v-if="page=='pro'">
        <a-row type="flex" :gutter="16">
          <a-col :span="12">
            <a-card title="Input" :bordered="false">
              <a-description>Use python.<br/>Please name input:preprocess_data.input,<br/>name result:preprocess_data.result</a-description>
              <a-form @submit="funcSubmit" :form="form">
                <a-form-item
                  label="Preprocess Function"
                  :labelCol="{ lg: { span: 7 }, sm: { span: 7 } }">
                  <a-textarea
                    :auto-size="{ minRows: 3, maxRows: 20 }"
                    v-decorator="[
                      'func_str',
                      {
                        rules: [{ required: false }],
                        initialValue: func_str
                      }
                    ]" />
                </a-form-item>
                <a-form-item :wrapper-col="{ span: 14, offset: 15 }">
                  <!-- <a-button @click.prevent="reset">Clear</a-button> -->
                  <a-button type="primary" htmlType="submit" style="margin-left: 16px">Submit</a-button>
                </a-form-item>
              </a-form>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="Example" :bordered="false" v-if="!spinning">
              <a-textarea :auto-size="{ minRows: 3, maxRows: 10 }" style="border: none" :defaultValue="func_ex">
              </a-textarea>
            </a-card>
          </a-col>
          <!-- <a-col :span="12">
          <a-card title="TestInput" :bordered="false" v-if="isJSON">
              <template #extra><a @click.stop="toJSON">Form</a></template>
              <a-textarea
                rows="6"
                v-model="jsonStr"
              />
              <a-button type="primary" @click="submitJSON" style="margin-left: 16px">Submit</a-button>
              <a-button type="primary" @click="jsonCurl" style="margin-left: 16px">Curlcode</a-button>
            </a-card>
            <a-card title="Input" :bordered="false" v-else>
              <template #extra><a @click.stop="toJSON">JSON</a></template>
              <a-form @submit="testFormSubmit" :form="form">
                <a-form-item v-for="(data, index) in inputData" :key="index" :label="data.name+' (Type:'+data.type+')'">
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
                </a-form-item>
                <a-form-item :wrapper-col="{ span: 14, offset: 15 }">
                  <a-button type="primary" htmlType="submit" style="margin-left: 16px">Submit</a-button>
                  <a-button type="primary" @click="formCurl" style="margin-left: 16px">Curlcode</a-button>
                </a-form-item>
              </a-form>
            </a-card>
          </a-col>
        </a-row>
        <br/><br/>
        <a-row type="flex" :gutter="16">
          <a-col :span="20">
            <a-card title="Output" :bordered="false">
              <textarea row="6" style="border: none" :value="testRes">
              </textarea>
            </a-card>
          </a-col> -->
        </a-row>
      </template>
    </a-spin>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
import { STable } from '@/components'
// 输入变量表格Column
const funcColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'Create Time',
    dataIndex: 'add_time',
    key: 'add_time'
  },
  {
    title: 'Average(ms)',
    key: 'average_use_time',
    dataIndex: 'average_use_time'
  },
  // {
  //   title: 'Median(ms)',
  //   key: 'medResTime',
  //   dataIndex: 'medResTime'
  // },
    {
    title: 'Min(ms)',
    key: 'minResTime',
    dataIndex: 'min_use_time'
  },
    {
    title: 'Max(ms)',
    key: 'maxResTime',
    dataIndex: 'max_use_time'
  },
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
  components: {
    STable
  },
  data () {
    return {
      deploy_id: this.$route.query.id,
      model_id: 0,
      serviceName: '',
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
      testRes: 'Here is result!',
      func_str: '',
      func_ex: 'import numpy as np\r\nimport cv2\r\n\r\ndef defualt_process(img):\r\n    img = cv2.imdecode(np.frombuffer(img.read(),np.uint8), cv2.IMREAD_COLOR)\r\n    img = cv2.resize(img, (28, 28))\r\n    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)\r\n    img = img / 255\r\n    img = np.ascontiguousarray(img)\r\n    img = img.astype(np.float)\r\n    img = img.reshape(1,28,28)\r\n    return np.array(img).astype(np.float32)\r\n\r\npreprocess_data.result = defualt_process(preprocess_data.input)',

      curlStr: '',
      spinning: false,
      baseUrl: '',

      columns: [
        {
          title: 'Test number',
          dataIndex: 'id',
          key: 'id'
        },
        {
          title: 'Description',
          dataIndex: 'description'
        },
        {
          title: 'Status',
          dataIndex: 'status',
          key: 'status'
        },
        {
          title: 'Added time',
          dataIndex: 'add_time'
        },
        {
          title: 'Recent modified time',
          dataIndex: 'recent_modified_time'
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
        return axios.get('/ml/test', {
          params: Object.assign(parameter, { 'service': this.deploy_id })
        }).then(res => {
            console.log(this.queryParam)
            console.log(parameter)
            console.log(res.data.result)
            return res.data.result
            }).catch(err => {
            console.log(err)
            try {
              this.$message.error(err.response.data.errmsg)
            } catch (err) {
              this.$message.error('read failed.')
              }
      })
      },

      selectedRowKeys: [],
      selectedRows: []
    }
  },
  beforeMount () {
    this.getInfo()
  },
  methods: {
    detail (row) {
      console.log(row.id)
      this.$router.push({ path: '/test/test-detail', query: { id: row.id } })
      // row = Object.assign({}, row)
    },
    getInfo () {
      this.spinning = true
      axios.get(`/ml/deploy/${this.deploy_id}`)
          .then(res => {
            this.spinning = false
            this.funcData = [res.data]
            this.model_id = res.data.mod
            console.log(this.funcData)
            if (this.funcData[0]['use_times'] === 0) {
              this.funcData[0]['min_use_time'] = 0
            }
            this.serviceDescription = res.data.description
            this.serviceStatus = res.data.status
            this.serviceName = res.data.name
            this.func_str = res.data.func_str
            this.baseUrl = res.data.baseUrl
            this.getModelInfo()
            }).catch(err => {
            this.spinning = false
            console.log(err)
            try {
              this.$message.error(err.response.data.errmsg)
            } catch (err) {
              this.$message.error('read failed.')
              }
          })
    },
    showPage (key) {
      this.page = key
      console.log('page:', this.page)
      this.getInfo()
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
            try {
              this.$message.error(err.response.data.errmsg)
            } catch (err) {
              this.$message.error('read failed.')
              }
          })
    },
    testBeforeUpload (file) {
      console.log(file)
      return false
    },
    toFormData (obj) {
    const form = new FormData()
    makeFormData(obj, form)
  /** 多层json数据转成formData */
    function makeFormData (obj, form_data) {
    const data = []

    if (obj instanceof File) {
      data.push({ key: '', value: obj })
    } else if (obj instanceof Array) { // 数组情况
      for (let j = 0, len = obj.length; j < len; j++) {
        const arr = makeFormData(obj[j])

        for (let k = 0, l = arr.length; k < l; k++) {
          const key = form_data ? j + arr[k].key : '[' + j + ']' + arr[k].key

          data.push({ key: key, value: arr[k].value })
        }
      }
    } else if (typeof obj === 'object') { // object
      for (const j in obj) {
        const arr = makeFormData(obj[j])

        for (let k = 0, l = arr.length; k < l; k++) {
          const key = form_data ? j + arr[k].key : '.' + j + '' + arr[k].key

          data.push({ key: key, value: arr[k].value })
        }
      }
    } else {
      data.push({ key: '', value: obj })
    }

      if (form_data) {
      // 封装
        for (let i = 0, len = data.length; i < len; i++) {
          form_data.append(data[i].key, data[i].value)
        }
      } else {
        return data
      }
    }

      return form
    },
    testFormSubmit (e) {
      e.preventDefault()
      console.log(this.form)
      this.form.validateFields((err, values) => {
        if (!err) {
          this.spinning = true
          Object.keys(values).forEach(key => {
            if (this.isFile[key]) {
              values[key] = values[key].file
            }
            var val = values[key]
            console.log(val)
            if (typeof (val) === 'string' && val.startsWith('[') && val.endsWith(']')) {
              values[key] = val.split(/\s|,|\[|\]/).filter(item => item !== '')
            }
          })
          var formData = this.toFormData(values)
          console.log(values)
          axios({
            url: `/ml/deploy/${this.deploy_id}`,
            method: 'post',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                this.spinning = false
                this.$message.success('upload successfully.')
                this.testRes = JSON.stringify(res.data)
              }).catch(err => {
              console.log(err)
              this.spinning = false
              try {
                this.$message.error(err.response.data.errmsg)
              } catch (err) {
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
        return
      }
      console.log(jsonJson)
      this.spinning = true
      const formData = this.toFormData(jsonJson)
      axios({
            url: `/ml/deploy/${this.deploy_id}`,
            method: 'post',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                this.spinning = false
                this.$message.success('upload successfully.')
                this.testRes = JSON.stringify(res.data)
              }).catch(err => {
              this.spinning = false
              console.log(err)
              try {
                this.$message.error(err.response.data.errmsg)
              } catch (err) {
                this.$message.error('upload failed.')
                }
            })
    },
    pause () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Pause?`,
        okType: 'danger',
        onOk () {
          const formData = new FormData()
          formData.append('status', 'paused')
          thi.spinning = true
          axios({
            url: `/ml/deploy/${thi.deploy_id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                thi.spinning = false
                thi.$message.success('pause successfully.')
                thi.$router.go(0)
              }).catch(err => {
              console.log(err)
              thi.spinning = false
              if ('errmsg' in err.response.data) {
                thi.$message.error(err.response.data.errmsg)
              } else {
                thi.$message.error('pause failed.')
                }
            })
        }
      })
    },
    deploy () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Deploy?`,
        okType: 'danger',
        onOk () {
          thi.spinning = true
          const formData = new FormData()
          formData.append('status', 'deployed')
          axios({
            url: `/ml/deploy/${thi.deploy_id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                thi.spinning = false
                thi.$message.success('Depoly successfully.')
                thi.$router.go(0)
              }).catch(err => {
              thi.spinning = false
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('Depoly failed.')
                }
            })
        }
      })
    },
    undeploy () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Undeploy?`,
        okType: 'danger',
        onOk () {
          thi.spinning = true
          const formData = new FormData()
          formData.append('status', 'undeployed')
          axios({
            url: `/ml/deploy/${thi.deploy_id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                thi.spinning = false
                thi.$message.success('Undeploy successfully.')
                thi.$router.go(0)
              }).catch(err => {
              console.log(err)
              thi.spinning = false
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('Undeploy failed.')
                }
            })
        }
      })
    },
    jsonCurl () {
      this.curlStr = `curl --location --request POST 'http://${this.baseUrl}/ml/deploy/${this.deploy_id}'`
      try {
      var jsonJson = JSON.parse(this.jsonStr)
      } catch (err) {
        console.log(err)
        this.$message.error('json error.')
        return
      }
      console.log(jsonJson)
      for (var v in jsonJson) {
        this.curlStr += ` \\\n--form '${v}="${jsonJson[v]}"'`
      }
      const thi = this
      this.$confirm({
        title: 'CURL',
        content: this.curlStr,
        cancelText: 'Copy to clipborad',
        onOk () {},
        onCancel () {
          thi.$copyText(thi.curlStr)
        }
      })
    },
    toBase64 (file) {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      return new Promise(
      resolve => (reader.onloadend = () => resolve(reader.result))
      )
    },
    async formCurl () {
    async function t (values, v, thi) {
          try {
            const res = await thi.toBase64(values[v].file)
            thi.curlStr += ` \\\n--form '${v}="${res}"'`
            } catch (err) {
            console.log(err)
            thi.curlStr += ` \\\n--form '${v}="${values[v]}"'`
          }
          }
    async function vva (values, thi) {
          thi.curlStr = `curl --location --request POST 'http://${thi.baseUrl}/ml/deploy/${thi.deploy_id}'`
          for (var v in values) {
            await t(values, v, thi)
          }
          await thi.$confirm({
            title: 'CURL',
            content: thi.curlStr,
            cancelText: 'Copy to clipborad',
            onOk () {},
            onCancel () {
              thi.$copyText(thi.curlStr)
            }
          })
        }
      this.form.validateFields((err, values) => {
        if (!err) {
          vva(values, this)
        }
        })
    },
    taskFormSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          this.spinning = true
          const formData = new FormData()
          formData.append('file', values['file'].file)
          for (var v in values) {
           if (v !== 'file') {
            formData.append(v, values[v])
            }
          formData.append('service_id', this.deploy_id)
          }
          console.log(values)
          axios({
            url: `/ml/test`,
            method: 'post',
            processData: false,
            data: formData
            }).then(res => {
                this.spinning = false
                this.$message.success('upload successfully.')
                const thi = this
                this.$info({
                  title: 'Task ID',
                  content: 'Task ID:' + res.data.task_id.toString(),
                  onOk () {
                    thi.$router.push({ path: '/test/test-detail', query: { id: res.data.task_id } })
                  },
                  onCancel () {}
                })
              }).catch(err => {
              this.spinning = false
              console.log(err)
              try {
                this.$message.error(err.response.data.errmsg)
              } catch (err) {
                this.$message.error('Failed.')
                }
            })
        }
      })
    },
    funcSubmit (e) {
      e.preventDefault()
      console.log(this.form)
      this.form.validateFields((err, values) => {
        if (!err) {
          this.spinning = true
          var formData = new FormData()
          console.log(values)
          for (var v in values) {
            formData.append(v, values[v])
          }
          console.log(values)
          axios({
            url: `/ml/deploy/${this.deploy_id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                this.spinning = false
                this.$message.success('upload successfully.')
              }).catch(err => {
              this.spinning = false
              console.log(err)
              try {
                this.$message.error(err.response.data.errmsg)
              } catch (err) {
                this.$message.error('Failed.')
                }
            })
        }
      })
    }
  }
}
</script>

<style scoped>
</style>
