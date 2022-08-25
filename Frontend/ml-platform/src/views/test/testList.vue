<template>
  <page-header-wrapper :title="false">
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
            <a-col :md="8" :sm="24">
              <a-form-item>
                <a-input placeholder="" v-model="filter_name"/>
              </a-form-item>
            </a-col>
            <!-- <a-col :md="8" :sm="24">
              <a-form-item label="Type">
                <a-select placeholder="请选择" default-value="" v-model="filter_type">
                  <a-select-option value="">All</a-select-option>
                  <a-select-option value="onnx">onnx</a-select-option>
                  <a-select-option value="pmml">pmml</a-select-option>
                </a-select>
              </a-form-item>
            </a-col> -->
            <a-col :md="8" :sm="24">
              <a-form-item label="Status">
                <a-select placeholder="" default-value="" v-model="filter_status">
                  <a-select-option value="">All</a-select-option>
                  <a-select-option value="run">Running</a-select-option>
                  <!-- <a-select-option value="paused">Paused</a-select-option> -->
                  <a-select-option value="finished">Finished</a-select-option>
                  <a-select-option value="interrupted">Interrupted</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <!-- <template v-if="advanced">
            <a-col :md="8" :sm="24">
              <a-form-item label="调用次数">
                <a-input-number style="width: 100%"/>
              </a-form-item>
            </a-col>
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
        <a-dropdown v-if="selectedRowKeys.length > 0">
          <template #overlay>
            <a-menu>
              // <a-menu-item @click="deploys">
              //   Run
              // </a-menu-item>
              // <a-menu-item @click="pauses">
              //   Pause
              // </a-menu-item>
              <a-menu-item @click="stops">
                Stop
              </a-menu-item>
              <a-menu-item @click="dels">
                Delete
              </a-menu-item>
            </a-menu>
          </template>
          <a-button>
            Do
            <DownOutlined />
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
        <template v-for="(col, index) in columns" v-if="col.scopedSlots" :slot="col.dataIndex" slot-scope="text">
          <div :key="index">
            <template>{{ text }}</template>
          </div>
        </template>

        <template slot="action" slot-scope="text, record">
          <div class="editable-row-operations">
            <span>
              <a class="edit" @click="() => detail(record)">Detail</a>
              <!-- <a-divider type="vertical" v-if="record.status=='paused'"/>
              <a class="delete" @click="() => deploy(record)" v-if="record.status=='paused'">Run</a>
              <a-divider type="vertical" v-if="record.status=='run'"/>
              <a class="delete" @click="() => pause(record)" v-if="record.status=='run'">Pause</a> -->
              <a-divider type="vertical" v-if="record.status=='run'"/>
              <a class="delete" @click="() => stop(record)" v-if="record.status=='run'">Stop</a>
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
      filter_status: '',

      // 高级搜索 展开/关闭
      advanced: false,
      // 查询参数
      queryParam: {},
      // 表头
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
        this.queryParam = {}
        if (this.filter_name !== '') {
          this.queryParam['name'] = this.filter_name
        }
        // if (this.filter_type !== '') {
        //   this.queryParam['model_type'] = this.filter_type
        // }
        if (this.filter_status !== '') {
          this.queryParam['status'] = this.filter_status
        }
        return axios.get('/ml/test', {
          params: Object.assign(parameter, this.queryParam)
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
  methods: {
    handleChange (value, key, column, record) {
      console.log(value, key, column)
      record[column.dataIndex] = value
    },
    detail (row) {
      console.log(row.id)
      this.$router.push({ path: '/test/test-detail', query: { id: row.id } })
      // row = Object.assign({}, row)
    },
    del (row) {
      const thi = this
      this.$confirm({
        title: 'Warining',
        content: `Delete ${row.id}?`,
        okType: 'danger',
        onOk () {
          axios({
            url: `/ml/test/${row.id}`,
            method: 'delete',
            processData: false
            }).then(res => {
                thi.$message.success('Delete successfully.')
                thi.resetForm()
                thi.$refs.table.refresh(true)
              }).catch(err => {
              console.log(err)
              if ('errmsg' in err.response.data) {
                thi.$message.error(err.response.data.errmsg)
              } else {
                thi.$message.error('Delete failed.')
                }
            })
        }
      })
    },
    dels () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Delete these?`,
        okType: 'danger',
        async onOk () {
          console.log(thi.selectedRows)
          for (var i = 0; i < thi.selectedRows.length; i++) {
          await axios({
            url: `/ml/test/${thi.selectedRows[i].id}`,
            method: 'delete',
            processData: false
            }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('Delete failed.')
                }
            })
          }
          thi.resetForm()
          thi.selectedRows = []
          thi.$refs.table.refresh(true)
        }
      })
    },
    // pause (row) {
    //   const thi = this
    //   this.$confirm({
    //     title: 'Warning',
    //     content: `Pause ${row.name}?`,
    //     okType: 'danger',
    //     onOk () {
    //       const formData = new FormData()
    //       formData.append('status', 'paused')
    //       axios({
    //         url: `/ml/test/${row.id}`,
    //         method: 'put',
    //         processData: false,
    //         headers: {
    //            'Content-Type': 'application/x-www-form-urlencoded'
    //         },
    //         data: formData
    //         }).then(res => {
    //             thi.$message.success('pause successfully.')
    //             thi.resetForm()
    //             thi.$refs.table.refresh(true)
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
    // },
    // pauses () {
    //   const thi = this
    //   this.$confirm({
    //     title: 'Warning',
    //     content: `Pause these?`,
    //     okType: 'danger',
    //     async onOk () {
    //       const formData = new FormData()
    //       formData.append('status', 'paused')
    //       console.log(thi.selectedRows)
    //       for (var i = 0; i < thi.selectedRows.length; i++) {
    //       await axios({
    //         url: `/ml/test/${thi.selectedRows[i].id}`,
    //         method: 'put',
    //         processData: false,
    //         headers: {
    //            'Content-Type': 'application/x-www-form-urlencoded'
    //         },
    //         data: formData
    //         }).catch(err => {
    //           console.log(err)
    //           try {
    //             thi.$message.error(err.response.data.errmsg)
    //           } catch (err) {
    //             thi.$message.error('delete failed.')
    //             }
    //         })
    //       }
    //       thi.$router.go(0)
    //     }
    //   })
    // },
    // deploy (row) {
    //   const thi = this
    //   this.$confirm({
    //     title: 'Warning',
    //     content: `Run ${row.name}?`,
    //     okType: 'danger',
    //     onOk () {
    //       const formData = new FormData()
    //       formData.append('status', 'run')
    //       axios({
    //         url: `/ml/test/${row.id}`,
    //         method: 'put',
    //         processData: false,
    //         headers: {
    //            'Content-Type': 'application/x-www-form-urlencoded'
    //         },
    //         data: formData
    //         }).then(res => {
    //             thi.$message.success('Run successfully.')
    //             thi.resetForm()
    //             thi.$refs.table.refresh(true)
    //           }).catch(err => {
    //           console.log(err)
    //           try {
    //             thi.$message.error(err.response.data.errmsg)
    //           } catch (err) {
    //             thi.$message.error('Run failed.')
    //             }
    //         })
    //     }
    //   })
    // },
    // deploys () {
    //   const thi = this
    //   this.$confirm({
    //     title: 'Warning',
    //     content: `Deploy these?`,
    //     okType: 'danger',
    //     async onOk () {
    //       const formData = new FormData()
    //       formData.append('status', 'run')
    //       console.log(thi.selectedRows)
    //       for (var i = 0; i < thi.selectedRows.length; i++) {
    //       await axios({
    //         url: `/ml/test/${thi.selectedRows[i].id}`,
    //         method: 'put',
    //         processData: false,
    //         headers: {
    //            'Content-Type': 'application/x-www-form-urlencoded'
    //         },
    //         data: formData
    //         }).catch(err => {
    //           console.log(err)
    //           try {
    //             thi.$message.error(err.response.data.errmsg)
    //           } catch (err) {
    //             thi.$message.error('Run failed.')
    //             }
    //         })
    //       }
    //       thi.$router.go(0)
    //     }
    //   })
    // },
    stop (row) {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Stop ${row.id}?`,
        okType: 'danger',
        onOk () {
          const formData = new FormData()
          formData.append('status', 'interrputed')
          axios({
            url: `/ml/test/${row.id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).then(res => {
                thi.$message.success('Stop successfully.')
                thi.resetForm()
                thi.$refs.table.refresh(true)
              }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('Stop failed.')
                }
            })
        }
      })
    },
    stops () {
      const thi = this
      this.$confirm({
        title: 'Warning',
        content: `Stop these?`,
        okType: 'danger',
        async onOk () {
          const formData = new FormData()
          formData.append('status', 'interrputed')
          console.log(thi.selectedRows)
          for (var i = 0; i < thi.selectedRows.length; i++) {
          await axios({
            url: `/ml/test/${thi.selectedRows[i].id}`,
            method: 'put',
            processData: false,
            headers: {
               'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData
            }).catch(err => {
              console.log(err)
              try {
                thi.$message.error(err.response.data.errmsg)
              } catch (err) {
                thi.$message.error('Stop failed.')
                }
            })
          }
          thi.$router.go(0)
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
      this.filter_status = ''
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
