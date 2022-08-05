<template>
  <page-header-wrapper title="Sample Model" :content="$t('model_test_guideline')">
    <a-card :bordered="false">
      <a-row class="propertyList">
        <a-col :xs="4">
          <div class="propertyName">Type</div>
          <div class="propertyContent">{{ modelType }}</div>
        </a-col>
        <a-col :xs="6">
          <div class="propertyName">Algorithm</div>
          <div class="propertyContent">{{ modelAlgorithm }}</div>
        </a-col>
        <a-divider type="vertical"/>
        <a-col :xs="4">
          <div class="propertyName">Engine</div>
          <div class="propertyContent">{{ modelEngine }}</div>
        </a-col>
        <a-col :xs="6">
          <div class="propertyName">Description</div>
          <div class="propertyContent">{{ modelDescription }}</div>
        </a-col>
      </a-row>
      <a-divider/>
    </a-card>
    <!-- <textarea/> -->
    <div>
      <a-card :bordered="false">
        <!-- <s-table
          :data=inputVar,
        >

        </s-table> -->
      </a-card>
      <a-card :bordered="false">
        <a-form>
          <!-- <a-form-item :v-for="(para, index) in paras">
          </a-form-item> -->
        </a-form>
      </a-card>
    </div>
  </page-header-wrapper>
</template>

<script>
export default {
  name: 'ModelTest',
  data () {
    return {
      // form: this.$form.createForm(this),
      modelAlgorithm: 'MiningModel(classification)',
      modelEngine: 'PyPMML',
      modelType: 'PMML',
      modelDescription: 'This is a sample model.'
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
    }
  }
}
</script>

<style scoped>
  a-form {
    display: flex;
  }
  a-card {
    margin-right: 10px;
  }
  .propertyName {
    font-weight: 600;
    font-size: 17px;
    color: black;
  }
  #divider {
    size: 200;
  }
</style>
