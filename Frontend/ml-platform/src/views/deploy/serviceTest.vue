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
    </template>
  </page-header-wrapper>
</template>

<script>
const funcData = []
// 输入变量表格Column
const funcColumns = [
  {
    title: 'Function',
    dataIndex: 'funcName',
    key: 'funcName'
  },
  {
    title: 'Invoke',
    dataIndex: 'invokeTime',
    key: 'invokeTime'
  },
  {
    title: 'Average(ms)',
    key: 'avgResTime',
    dataIndex: 'avgResTime'
  },
  {
    title: 'Median(ms)',
    key: 'medResTime',
    dataIndex: 'medResTime'
  },
    {
    title: 'Min(ms)',
    key: 'minResTime',
    dataIndex: 'minResTime'
  },
    {
    title: 'Max(ms)',
    key: 'maxResTime',
    dataIndex: 'maxResTime'
  },
    {
    title: 'First visit',
    key: 'firVisTime',
    dataIndex: 'firVisTime'
  },
    {
    title: 'Latest visit',
    key: 'latVisTime',
    dataIndex: 'latVisTime'
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
      serviceAlgorithm: 'MiningModel(classification)',
      serviceEngine: 'PyPMML',
      serviceType: 'PMML',
      serviceTime: '2022-8-7 23:07',
      page: 'info',
      funcData,
      funcColumns,
      copyData,
      copyColumns
    }
  },

  methods: {
    showPage (key) {
      this.page = key
      console.log('page:', this.page)
    }
  }
}
</script>

<style scoped>
</style>
