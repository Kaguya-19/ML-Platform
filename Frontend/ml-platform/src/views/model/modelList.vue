<template>
  <page-header-wrapper :title="false" :content="$t('model_list_guideline')">
    <a-card :bordered="false">
      <a-table v-if="showList" :columns="modelColumns" :data-source="modelData" :row-key="record => record.id">
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
import axios from 'axios'
import { defineComponent } from 'vue'
// import { STable, Ellipsis } from '@/components'
const modelColumns = [
  {
    title: 'Model number',
    dataIndex: 'id',
    key: 'id'
  },
  {
    title: 'Name',
    dataIndex: 'name'
  },
  // {
  //   title: 'Description',
  //   dataIndex: 'description'
  // },
  // {
  //   title: 'Status',
  //   dataIndex: 'status',
  //   key: 'status'
  // },
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
    dataIndex: 'operation'
  }
]
var modelData = [
  // {
  //   key: '1',
  //   number: 1,
  //   // status: 'undeployed',
  //   // description: 'This is a model.',
  //   // time: '2022-8-7 22:10'
  //   operation: 'detail'
  // }
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
      confirmLoading: false,
      showList: false
    }
  },
  beforeCreate () {
    modelData = []
    axios.get(
      '/ml/model'
      ).then(res => {
        console.log(res.data.models)
          for (let i = 0; i < res.data.models.length; i++) {
            modelData.push(res.data.models[i])
        }
        this.showList = true
        console.log(modelData)
        }).catch(err => {
        console.log(err)
        if ('errmsg' in err.response.data) {
          this.$message.error(err.response.data.errmsg)
        } else {
          this.$message.error('read failed.')
          }
      })
  },
  methods: { // TODO:删除&选择&查询&分页
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
