<template>
  <page-header-wrapper :title="false" content="List of models.">
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
            <a-col :md="8" :sm="24">
              <a-form-item>
                <a-input placeholder="" v-model="filter_name"/>
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24">
              <a-form-item label="Type">
                <a-select placeholder="" default-value="" v-model="filter_type">
                  <a-select-option value="">All</a-select-option>
                  <a-select-option value="onnx">onnx</a-select-option>
                  <a-select-option value="pmml">pmml</a-select-option>
                  <a-select-option value="keras">keras</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <!-- <template v-if="advanced">
            <a-col :md="8" :sm="24">
              <a-form-item label="更新日期">
                <a-date-picker style="width: 100%" placeholder="请输入更新日期"/>
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24">
              <a-form-item label="使用状态">
                <a-select placeholder="请选择" default-value="0">
                  <a-select-option value="0">全部</a-select-option>
                  <a-select-option value="1">关闭</a-select-option>
                  <a-select-option value="2">运行中</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </template> -->
            <a-col :md="!advanced && 8 || 24" :sm="24">
              <span class="table-page-search-submitButtons" :style="advanced && { float: 'right', overflow: 'hidden' } || {} ">
                <a-button type="primary" @click="filter">Query</a-button>
                <a-button style="margin-left: 8px" @click="resetForm">Reset</a-button>
                <!-- <a @click="toggleAdvanced" style="margin-left: 8px">
                  {{ advanced ? 'Up' : 'Down' }}
                  <a-icon :type="advanced ? 'up' : 'down'"/>
                </a> -->
              </span>
            </a-col>
          </a-row>
        </a-form>
      </div>

      <div class="table-operator">
        <a-button type="primary" icon="plus" @click="add">Add</a-button>
        <a-dropdown v-if="selectedRowKeys.length > 0">
          <a-button style="margin-left: 8px" @click="dels">
            Delete
          </a-button>
        </a-dropdown>
      </div>

      <s-table
        ref="table"
        size="default"
        :columns="columns"
        :data="loadData"
        :alert="{ show: true, clear: true }"
        :rowSelection="{ selectedRowKeys: this.selectedRowKeys, onChange: this.onSelectChange }"
        :rowKey="record => record.id"
      >
        <template v-for="(col) in columns" :slot="col.dataIndex" slot-scope="text">
          <template>{{ text }}</template>
        </template>

        <template slot="action" slot-scope="text, record">
          <div class="editable-row-operations">
            <span>
              <a class="edit" @click="() => detail(record)">Detail</a>
              <a-divider type="vertical" />
              <a class="delete" @click="() => del(record)">Del</a>
            </span>
          </div>
        </template>
      </s-table>

    </a-card>
  </page-header-wrapper>
</template>

<script>
import axios from 'axios'
import { STable } from '@/components'

export default {
  name: 'TableList',
  components: {
    STable
  },
  data () {
    return {
      filter_name: '',
      filter_type: '',

      // 高级搜索 展开/关闭
      advanced: false,
      // 查询参数
      queryParam: {},
      // 表头
      columns: [
        {
          title: 'Model number',
          dataIndex: 'id',
          key: 'id'
        },
        {
          title: 'Name',
          dataIndex: 'name',
          key: 'name'
        },
        {
          title: 'Description',
          dataIndex: 'description'
        },
        {
          title: 'Added time',
          dataIndex: 'add_time'
        },
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
        this.queryParam = {}
        if (this.filter_name !== '') {
          this.queryParam['name'] = this.filter_name
        }
        if (this.filter_type !== '') {
          this.queryParam['model_type'] = this.filter_type
        }
        return axios.get('/ml/model', {
          params: Object.assign(parameter, this.queryParam)
        }).then(res => {
            return res.data.result
            }).catch(err => {
            console.log(err)
            if ('errmsg' in err.response.data) {
              this.$message.error(err.response.data.errmsg)
            } else {
              this.$message.error('read failed.')
              }
      })
      },

      selectedRowKeys: [],
      selectedRows: []
    }
  },
  methods: {
    add () {
      this.$router.push('/model/model-add')
    },
    handleChange (value, key, column, record) {
      console.log(value, key, column)
      record[column.dataIndex] = value
    },
    detail (row) {
      console.log(row.id)
      this.$router.push({ path: '/model/model-test', query: { id: row.id } })
    },
    del (row) {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Delete ${row.name}?`,
        okType: 'danger',
        onOk () {
          axios({
            url: `/ml/model/${row.id}`,
            method: 'delete',
            processData: false
            }).then(res => {
                thi.$message.success('Delete successfully.')
                thi.resetForm()
                thi.$refs.table.refresh(true)
              }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('Delete failed.')
                }
            })
        }
      })
    },
    dels () {
      const thi = this
      this.$confirm({
        title: 'Warming',
        content: `Delete these?`,
        okType: 'danger',
        async onOk () {
          console.log(thi.selectedRows)
          for (var i = 0; i < thi.selectedRows.length; i++) {
          await axios({
            url: `/ml/model/${thi.selectedRows[i].id}`,
            method: 'delete',
            processData: false
            }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('delete failed.')
                }
            })
          }
          thi.resetForm()
          thi.selectedRows = []
          thi.$refs.table.refresh(true)
        }
      })
    },

    onSelectChange (selectedRowKeys, selectedRows) {
      this.selectedRowKeys = selectedRowKeys
      this.selectedRows = selectedRows
    },
    toggleAdvanced () {
      this.advanced = !this.advanced
    },
    resetForm () {
      this.filter_name = ''
      this.filter_type = ''
    },
    filter () {
      this.$refs.table.refresh(true)
    }
  }
}
</script>

<style lang="less" scoped>
  .search {
    margin-bottom: 54px;
  }

  .fold {
    width: calc(100% - 216px);
    display: inline-block
  }

  .operator {
    margin-bottom: 18px;
  }

  @media screen and (max-width: 900px) {
    .fold {
      width: 100%;
    }
  }
</style>
