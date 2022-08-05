<template>
  <page-header-wrapper :title="false" :content="$t('model_list_guideline')">
    <a-card :bordered="false">
      <s-table
        ref="table"
        size="default"
        rowKey="key"
        :columns="columns"
        :data="loadData"
        :alert="true"
        showPagination="auto"
      >
        <!-- 模型编号 -->
        <span slot="serial" slot-scope="text, record, index">
          {{ index + 1 }}
        </span>
        <!-- 模型状态：deployed or not -->
        <span slot="status" slot-scope="text">
          <a-badge :status="text | statusTypeFilter" :text="text | statusFilter" />
        </span>
        <!-- 模型描述 -->
        <span slot="description" slot-scope="text">
          <ellipsis :length="20" tooltip>{{ text }}</ellipsis>
        </span>
        <!-- 删除/测试模型 -->
        <span slot="action" slot-scope="text, record">
          <template>
            <a @click="Delete(record)">Delete</a>
            <a-divider type="vertical" />
            <a @click="Test(record)">Test</a>
          </template>
        </span>
      </s-table>

      <step-by-step-modal ref="modal" @ok="handleOk"/>
    </a-card>
  </page-header-wrapper>
</template>

<script>
// import moment from 'moment'
import { STable, Ellipsis } from '@/components'
import { getRoleList, getServiceList } from '@/api/manage'

import StepByStepModal from './modules/StepByStepModal'
// import CreateForm from './modules/CreateForm'

const columns = [
  {
    title: 'Model number',
    scopedSlots: { customRender: 'serial' }
  },
  {
    title: 'Description',
    dataIndex: 'description',
    scopedSlots: { customRender: 'description' }
  },
  {
    title: 'Status',
    dataIndex: 'status',
    scopedSlots: { customRender: 'status' }
  },
  {
    title: 'Added time',
    dataIndex: 'updatedAt'
  },
  {
    title: 'Operation',
    dataIndex: 'action',
    width: '150px',
    scopedSlots: { customRender: 'action' }
  }
]

export default {
  name: 'ModelList',
  components: {
    STable,
    Ellipsis,
    StepByStepModal
  },
  data () {
    this.columns = columns
    return {
      // create model
      visible: false,
      confirmLoading: false,
      mdl: null,
      loadData: parameter => {
        const requestParameters = Object.assign({}, parameter, this.queryParam)
        console.log('loadData request parameters:', requestParameters)
        return getServiceList(requestParameters)
          .then(res => {
            return res.result
          })
      }
    }
  },
  created () {
    getRoleList({ t: new Date() })
  },
  computed: {
    rowSelection () {
      return {
        selectedRowKeys: this.selectedRowKeys,
        onChange: this.onSelectChange
      }
    }
  },
  methods: {
    handleAdd () {
      this.mdl = null
      this.visible = true
    },
    handleEdit (record) {
      this.visible = true
      this.mdl = { ...record }
    },
    handleOk () {
      const form = this.$refs.createModal.form
      this.confirmLoading = true
      form.validateFields((errors, values) => {
        if (!errors) {
          console.log('values', values)
          if (values.id > 0) {
            // 修改 e.g.
            new Promise((resolve, reject) => {
              setTimeout(() => {
                resolve()
              }, 1000)
            }).then(res => {
              this.visible = false
              this.confirmLoading = false
              // 重置表单数据
              form.resetFields()
              // 刷新表格
              this.$refs.table.refresh()

              this.$message.info('修改成功')
            })
          } else {
            // 新增
            new Promise((resolve, reject) => {
              setTimeout(() => {
                resolve()
              }, 1000)
            }).then(res => {
              this.visible = false
              this.confirmLoading = false
              // 重置表单数据
              form.resetFields()
              // 刷新表格
              this.$refs.table.refresh()

              this.$message.info('新增成功')
            })
          }
        } else {
          this.confirmLoading = false
        }
      })
    },
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
    },
    toggleAdvanced () {
      this.advanced = !this.advanced
    },
    resetSearchForm () {
      // this.queryParam = {
      //   date: moment(new Date())
      // }
    }
  }
}
</script>

<style scoped>
  span s-table{
    text-align: center;
  }
</style>
