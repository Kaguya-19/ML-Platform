<template>
  <page-header-wrapper title="Sample Model" :content="$t('model_test_guideline')">
    <!-- 选择菜单：模型概述/测试 -->
    <!-- 模型概述 -->
    <template>
      <!-- 基本信息 -->
      <a-card :bordered="false">
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
        </a-row>
        <!-- <a-row type="flex" style="margin-top: 20px">
          <a-descriptions title="Description" v-if="modelDescription!==''" :value="modelDescription">
            <a-descriptions-item>{{ modelDescription }}</a-descriptions-item>
          </a-descriptions>
        </a-row> -->
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
      testStatus: false,
      modelAlgorithm: 'MiningModel(classification)',
      modelEngine: 'PyPMML',
      modelType: 'PMML',
      addTime: '2022-8-7 23:07',
      modelDescription: ''
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
            this.testStatus = res.data.algorithm
            this.modelTime = res.data.addTime
            if (res.data.description !== 'undefined') {
              this.modelDescription = res.data.description
            }
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
}
</script>

<style scoped>
</style>
