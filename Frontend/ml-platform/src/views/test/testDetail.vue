<template>
  <page-header-wrapper title="Test Detail" :content="$t('model_test_guideline')">
    <!-- 选择菜单：模型概述/测试 -->
    <!-- 模型概述 -->
    <template>
      <!-- 基本信息 -->
      <a-card :bordered="false">
        <template #extra><a :href="&quot;/deploy/deploy-test?id=&quot;+service_id">Service</a></template>
        <a :href="&quot;/model/model-test?id=&quot;+model_id">Model</a>
        <a style="margin-left: 30px" :href="&quot;http://&quot;+testUrl">Test File</a>
        <br/><br/>
        // <a-button @click="deploy" v-if="testStatus=='paused'">Run</a-button>
        <a-button @click="undeploy" v-if="testStatus=='run'">Stop</a-button>
        <!-- <a-button @click="pause" v-if="testStatus=='run'">Pause</a-button> -->

        <a-row type="flex">
          <a-col flex="auto">
            <a-statistic title="id" :value="test_id" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Status" :value="testStatus" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Added time" :value="addTime" />
          </a-col>
          <a-col flex="auto">
            <a-statistic title="Recent Modified Time" :value="recent_modified_time" />
          </a-col>
        </a-row>
        <a-row type="flex" v-if="testStatus!='run'&&testStatus!='paused'">
          <a-col flex="auto">
            <a-statistic title="Endtime" :value="end_time" />
          </a-col>
          <a-col flex="auto">
            <a-descriptions title="Result"></a-descriptions>
            <a-textarea title="Result" :auto-size="{ minRows: 3, maxRows: 20 }" style="border: none" :defaultValue="testRes">
            </a-textarea>
          </a-col>
        </a-row>
        <a-row type="flex" style="margin-top: 20px">
          <a-descriptions title="Description" v-if="testDescription!==''" :value="testDescription" style="white-space: pre-wrap;">
            <a-descriptions-item>{{ testDescription }}</a-descriptions-item>
          </a-descriptions>
        </a-row>

      </a-card>
      <!-- 输入/目标变量 -->
    </template>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
import { STable } from '@/components'
export default {
  name: 'ModelTest',
  components: {
    STable
  },
  data () {
    return {
      // form: this.$form.createForm(this),
      test_id: this.$route.query.id,
      testStatus: '',
      addTime: '2022-8-7 23:07',
      testDescription: '',
      model_id: 0,
      service_id: 0,
      recent_modified_time: '',
      end_time: '',
      testRes: '',
      testUrl: ''
    }
  },

  beforeMount () {
    this.getInfo()
  },
  methods: {
    // handler
    getInfo () {
      axios.get(`/ml/test/${this.test_id}`)
          .then(res => {
            this.testStatus = res.data.status
            this.addTime = res.data.add_time
            this.testDescription = res.data.description
            this.model_id = res.data.mod
            this.service_id = res.data.service
            this.recent_modified_time = res.data.recent_modified_time
            this.end_time = res.data.end_time
            this.testUrl = res.data.tested_file
            if ((this.testStatus === 'finished') || (this.testStatus === 'interrupted')) {
              this.testRes = JSON.stringify(res.data.result)
            }
            }).catch(err => {
            console.log(err)
            try {
              this.$message.error(err.response.data.errmsg)
            } catch (err) {
              this.$message.error('read failed.')
              }
          })
    },
    stop () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Stop?`,
        okType: 'danger',
        onOk () {
          const formData = new FormData()
          formData.append('status', 'interrupted')
          axios({
            url: `/ml/test/${thi.test_id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                thi.$message.success('Stop successfully.')
                thi.$router.go(0)
              }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('undeploy failed.')
                }
            })
        }
      })
    },
    deploy () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Run?`,
        okType: 'danger',
        onOk () {
          const formData = new FormData()
          formData.append('status', 'run')
          axios({
            url: `/ml/test/${thi.test_id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                thi.$message.success('Run successfully.')
                thi.$router.go(0)
              }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('deploy failed.')
                }
            })
        }
      })
    }
    // pause () {
    //   const thi = this
    //   this.$confirm({
    //     title: 'Warning',
    //     content: `Pause?`,
    //     okType: 'danger',
    //     onOk () {
    //       const formData = new FormData()
    //       formData.append('status', 'paused')
    //       axios({
    //         url: `/ml/test/${thi.test_id}`,
    //         method: 'put',
    //         processData: false,
    //         headers: {
    //            'Content-Type': 'application/x-www-form-urlencoded'
    //         },
    //         data: formData
    //         }).then(res => {
    //             thi.$message.success('Pause successfully.')
    //             thi.$router.go(0)
    //           }).catch(err => {
    //           console.log(err)
    //           try {
    //             thi.$message.error(err.response.data.errmsg)
    //           } catch (err) {
    //             thi.$message.error('pause failed.')
    //             }
    //         })
    //     }
    //   })
    // }
  }
}
</script>

<style scoped>
</style>
