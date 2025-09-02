<template>
  <div class="navigation">
    <el-menu
      :default-active="activeIndex"
      class="el-menu-demo"
      mode="horizontal"
      @select="handleSelect"
      router
    >
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/upload">数据上传</el-menu-item>
      <el-menu-item index="/train">模型训练</el-menu-item>
      <el-menu-item index="/predict">模型推理</el-menu-item>
    </el-menu>
  </div>
</template>

<script>
export default {
  name: 'Navigation',
  data() {
    return {
      activeIndex: '/'
    }
  },
  methods: {
    handleSelect(key) {
      this.activeIndex = key
    }
  }
}
</script>

<style scoped>
.navigation {
  border-bottom: 1px solid #e6e6e6;
}
</style>