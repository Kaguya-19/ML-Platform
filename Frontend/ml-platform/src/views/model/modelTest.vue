<template>
  <page-header-wrapper title="Sample Model" :content="$t('model_test_guideline')">
    <!-- 选择菜单：模型概述/测试 -->
    <a-menu mode="horizontal">
      <a-menu-item @click="showPage('info')">Model infomation</a-menu-item>
      <a-menu-item @click="showPage('test')">Model test</a-menu-item>
    </a-menu>
    <!-- 模型概述 -->
    <template v-if="page=='info'">
      <!-- 基本信息 -->
      <a-card :bordered="false">
        <a-row type="flex">
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
      </a-card>
      <!-- 输入/目标变量 -->
      <a-row type="flex" :gutter="16" style="margin-top: 20px">
        <a-col :span="12">
          <a-card title="Input variable" :bordered="false">
            <a-table :columns="inputColumns" :data-source="inputData">
            </a-table>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="Object variable" :bordered="false">
            <a-table :columns="objectColumns" :data-source="objectData">
            </a-table>
          </a-card>
        </a-col>
      </a-row>
    </template>
    <!-- 模型测试 -->
    <template v-if="page=='test'">
      <a-row type="flex" :gutter="16">
        <a-col :span="12">
          <a-card title="Input" :bordered="false">
            <a-form>
              <a-form-item v-for='(data, index) in inputData' :key="index" :label='data.iField'>
                <a-input/>
              </a-form-item>
              <a-form-item :wrapper-col="{ span: 14, offset: 15 }">
                <a-button @click.prevent="onSubmit">Clear</a-button>
                <a-button type="primary" @click="reset" style="margin-left: 16px">Submit</a-button>
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="Output" :bordered="false">
            <textarea style="border: none">
              Here is the outcome!
            </textarea>
          </a-card>
        </a-col>
      </a-row>
    </template>
  </page-header-wrapper>
</template>

<script>
const inputData = [
  {
    key: '1',
    iField: 'length(cm)',
    iType: 'double',
    iMeasurement: 'continuous'
    // iValue:
  },
  {
    key: '2',
    iField: 'length(cm)',
    iType: 'double',
    iMeasurement: 'continuous'
    // iValue:
  },
  {
    key: '3',
    iField: 'length(cm)',
    iType: 'double',
    iMeasurement: 'continuous'
    // iValue:
  }
]
// 输入变量表格Column
const inputColumns = [
  {
    title: 'Field',
    dataIndex: 'iField',
    key: 'iField'
  },
  {
    title: 'Type',
    dataIndex: 'iType',
    key: 'iType'
  },
  {
    title: 'Measurement ',
    key: 'iMeasurement',
    dataIndex: 'iMeasurement'
  },
  {
    title: 'Value',
    key: 'iValue',
    dataIndex: 'iValue'
  }
]
const objectData = [
  {
    key: '1',
    iField: 'length(cm)',
    iType: 'double',
    iMeasurement: 'continuous',
    iValue: '0,1,2'
  }
]
// 目标变量表格Column
const objectColumns = [
  {
    title: 'Field',
    dataIndex: 'iField',
    key: 'iField'
  },
  {
    title: 'Type',
    dataIndex: 'iType',
    key: 'iType'
  },
  {
    title: 'Measurement ',
    key: 'iMeasurement',
    dataIndex: 'iMeasurement'
  },
  {
    title: 'Value',
    key: 'iValue',
    dataIndex: 'iValue'
  }
]
export default {
  name: 'ModelTest',
  data () {
    return {
      // form: this.$form.createForm(this),
      modelAlgorithm: 'MiningModel(classification)',
      modelEngine: 'PyPMML',
      modelType: 'PMML',
      modelTime: '2022-8-7 23:07',
      page: 'info',
      inputData,
      inputColumns,
      objectData,
      objectColumns
    }
  },

  methods: {
    // handler
    handleSubmit (e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          console.log('Received values of form: ', values)
        }
      })
    },
    showPage (key) {
      this.page = key
      console.log('page:', this.page)
    }
  }
}
</script>

<style scoped>
</style>
