<template>
  <global-footer class="footer custom-render">
    <template v-slot:links>
      <a href="https://github.com/Kaguya-19/ML-Platform" target="_blank">Github</a>
    </template>
    <template v-slot:copyright>
      <a href="https://github.com/vueComponent" target="_blank">vueComponent</a>
    </template>
  </global-footer>
</template>

<script>
import { GlobalFooter } from '@ant-design-vue/pro-layout'

export default {
  name: 'ProGlobalFooter',
  components: {
    GlobalFooter
  }
}
</script>
