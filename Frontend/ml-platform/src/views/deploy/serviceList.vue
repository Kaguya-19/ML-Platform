<template>
  <page-header-wrapper :title="false" :content="$t('model_list_guideline')">
    <a-card :bordered="false">
      <a-table :columns="modelColumns" :data-source="modelData">
        <!-- <template #headerCell="{ column }">
          <template v-if="column.key === 'status'">
            <span>
              <smile-outlined />
              Statuss
            </span>
          </template>
        </template> -->
        <template #bodyCell="{ column, record }">
          <!-- <div>{{column}}</div> -->
          <template v-if="column.key === 'operation'">
            <span>
              <a @click="Delete(record)">Delete</a>
              <a-divider type="vertical" />
              <a @click="Test(record)">Test</a>
            </span>
          </template>
        </template>
      </a-table>
    </a-card>
  </page-header-wrapper>
</template>

<script lang='ts'>
import { defineComponent } from 'vue'
// import { STable, Ellipsis } from '@/components'
const modelColumns = [
  {
    title: 'Service name',
    dataIndex: 'name'
  },
  {
    title: 'Type',
    dataIndex: 'type'
  },
  {
    title: 'Start time',
    dataIndex: 'time'
  },
  {
    title: 'Status',
    dataIndex: 'status'
  },
  {
    title: 'Operation',
    dataIndex: 'operation',
    key: 'operation'
  }
]
const modelData = [
  {
    key: '1',
    name: 'Sample service',
    status: 'undeployed',
    type: 'This is a model type',
    time: '2022-8-7 22:10'
    // operation: 'test'
  }
]

export default defineComponent({
  name: 'ModelList',
  setup () {
    return {
      modelData,
      modelColumns
    }
  },
  data () {
    return {
      visible: false,
      confirmLoading: false
    }
  },
  methods: {
    // 删除模型
    Delete () {
      console.log('sha')
    },
    // 测试模型
    Test () {
      this.$router.push({ path: '/form/test-model' })
      // console.log('ready for test')
      // window.open(routeUrl.href, '_self')
    },
    onSelectChange (selectedRowKeys, selectedRows) {
      this.selectedRowKeys = selectedRowKeys
      this.selectedRows = selectedRows
    }
  }
})
</script>

<style scoped>
  span s-table{
    text-align: center;
  }
</style>
