<template>
  <div class="landing-container">
    <div class="landing-background">
      <div class="bg-gradient"></div>
      <div class="bg-particles"></div>
    </div>
    
    <!-- 顶部导航 -->
    <header class="landing-header">
      <div class="logo-container">
        <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="logo animate__animated animate__fadeIn" />
        <h1 class="brand-name animate__animated animate__fadeIn animate__delay-1s">LLM Trainer</h1>
      </div>
      <div class="nav-buttons">
        <el-button type="primary" @click="goToLogin" class="login-btn animate__animated animate__fadeIn animate__delay-2s">登录</el-button>
        <el-button @click="goToRegister" class="register-btn animate__animated animate__fadeIn animate__delay-2s">注册</el-button>
      </div>
    </header>
    
    <!-- 主要内容区 -->
    <main class="landing-main">
      <div class="hero-section">
        <h1 class="hero-title animate__animated animate__fadeInUp">简化AI模型训练流程</h1>
        <h2 class="hero-subtitle animate__animated animate__fadeInUp animate__delay-1s">专为开发者设计的大语言模型训练平台</h2>
        <p class="hero-description animate__animated animate__fadeInUp animate__delay-2s">
          LLM Trainer 提供直观的界面和强大的功能，帮助您轻松上传数据集、训练模型并进行推理测试，
          无需复杂的配置和深厚的机器学习背景。让AI模型训练变得简单而高效。
        </p>
        <div class="hero-stats animate__animated animate__fadeInUp animate__delay-3s">
          <div class="stat-item">
            <div class="stat-number">99%</div>
            <div class="stat-label">训练效率提升</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">50+</div>
            <div class="stat-label">预设模型参数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">24/7</div>
            <div class="stat-label">技术支持</div>
          </div>
        </div>
        <el-button type="primary" size="large" @click="goToLogin" class="cta-button animate__animated animate__fadeInUp animate__delay-4s">
          <el-icon class="el-icon--left"><ArrowRight /></el-icon>
          开始使用
        </el-button>
      </div>
      
      <!-- 功能特点区 -->
      <div class="features-section">
        <h2 class="section-title animate__animated animate__fadeIn animate__delay-1s">核心功能</h2>
        <div class="feature-cards centered-cards">
          <el-card class="feature-card animate__animated animate__fadeInLeft animate__delay-2s">
            <template #header>
              <div class="feature-header">
                <el-icon><Upload /></el-icon>
                <h3>数据集管理</h3>
              </div>
            </template>
            <p>轻松上传、预览和管理您的文本分类数据集，支持CSV格式，自动进行数据验证和预处理。智能数据清洗功能帮助您快速准备高质量训练数据。</p>
            <div class="feature-detail">
              <el-tag size="small">CSV导入</el-tag>
              <el-tag size="small">数据验证</el-tag>
              <el-tag size="small">自动预处理</el-tag>
            </div>
          </el-card>
          
          <el-card class="feature-card animate__animated animate__fadeInUp animate__delay-2s">
            <template #header>
              <div class="feature-header">
                <el-icon><Setting /></el-icon>
                <h3>模型训练</h3>
              </div>
            </template>
            <p>基于BERT的高效微调训练，可自定义训练参数，实时监控训练进度和性能指标。支持多种优化器和学习率策略，让您的模型训练更加高效。</p>
            <div class="feature-detail">
              <el-tag size="small">BERT微调</el-tag>
              <el-tag size="small">实时监控</el-tag>
              <el-tag size="small">参数优化</el-tag>
            </div>
          </el-card>
          
          <el-card class="feature-card animate__animated animate__fadeInRight animate__delay-2s">
            <template #header>
              <div class="feature-header">
                <el-icon><DataAnalysis /></el-icon>
                <h3>模型推理</h3>
              </div>
            </template>
            <p>使用训练好的模型进行实时文本分类预测，直观展示预测结果和置信度。支持批量推理和API集成，轻松将模型部署到您的应用中。</p>
            <div class="feature-detail">
              <el-tag size="small">实时预测</el-tag>
              <el-tag size="small">批量推理</el-tag>
              <el-tag size="small">API集成</el-tag>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 项目远景和未来规划区 -->
      <div class="vision-section">
        <h2 class="section-title animate__animated animate__fadeIn">项目远景与未来规划</h2>
        <div class="vision-content">
          <div class="vision-card animate__animated animate__fadeIn animate__delay-1s">
            <div class="vision-icon">
              <el-icon :size="40"><Aim /></el-icon>
            </div>
            <div class="vision-text">
              <h3>项目愿景</h3>
              <p>LLM Trainer致力于降低大语言模型训练的技术门槛，让更多开发者能够轻松构建和训练自己的文本分类模型。我们的目标是打造一个全面、易用且高效的模型训练平台，使AI技术更加普及和民主化。</p>
            </div>
          </div>
          
          <div class="vision-card animate__animated animate__fadeIn animate__delay-2s">
            <div class="vision-icon">
              <el-icon :size="40"><TrendCharts /></el-icon>
            </div>
            <div class="vision-text">
              <h3>技术路线</h3>
              <p>我们将持续跟进最新的NLP技术发展，不断优化模型训练流程和性能。未来计划支持更多预训练模型，如GPT、RoBERTa等，并引入更先进的微调技术，如LoRA和P-Tuning，以提供更高效的训练体验。</p>
              <div class="tech-roadmap">
                <el-tag type="info">多语言支持</el-tag>
                <el-tag type="info">更多预训练模型</el-tag>
                <el-tag type="info">高级微调技术</el-tag>
              </div>
            </div>
          </div>
          
          <div class="vision-card animate__animated animate__fadeIn animate__delay-3s">
            <div class="vision-icon">
              <el-icon :size="40"><Connection /></el-icon>
            </div>
            <div class="vision-text">
              <h3>功能规划</h3>
              <p>我们计划在未来版本中添加更多实用功能，包括数据增强工具、模型可解释性分析、自动超参数优化、模型部署一键集成等。同时，我们将提供更丰富的数据可视化和性能分析工具，帮助用户更好地理解和优化他们的模型。</p>
              <div class="feature-roadmap">
                <el-timeline>
                  <el-timeline-item timestamp="2023 Q4" placement="top">
                    <el-card>
                      <h4>数据增强与批量处理</h4>
                    </el-card>
                  </el-timeline-item>
                  <el-timeline-item timestamp="2024 Q1" placement="top">
                    <el-card>
                      <h4>模型可解释性分析</h4>
                    </el-card>
                  </el-timeline-item>
                  <el-timeline-item timestamp="2024 Q2" placement="top">
                    <el-card>
                      <h4>一键部署与API集成</h4>
                    </el-card>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 开始使用区 -->
      <div class="get-started-section">
        <h2 class="section-title animate__animated animate__fadeIn">准备好开始了吗？</h2>
        <p class="section-description animate__animated animate__fadeIn animate__delay-1s">创建账号或登录以体验完整功能</p>
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="goToRegister" class="action-btn animate__animated animate__fadeInUp animate__delay-2s">
            <el-icon class="el-icon--left"><Plus /></el-icon>
            创建账号
          </el-button>
          <el-button size="large" @click="goToLogin" class="action-btn animate__animated animate__fadeInUp animate__delay-2s">
            <el-icon class="el-icon--left"><Key /></el-icon>
            登录账号
          </el-button>
        </div>
        <div class="tech-badges animate__animated animate__fadeIn animate__delay-3s">
          <span class="tech-badge">Vue 3</span>
          <span class="tech-badge">Element Plus</span>
          <span class="tech-badge">FastAPI</span>
          <span class="tech-badge">BERT</span>
          <span class="tech-badge">PyTorch</span>
        </div>
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-logo">
          <img src="../assets/logo.svg" alt="LLM Trainer Logo" class="footer-logo-img" />
          <span class="footer-brand">LLM Trainer</span>
        </div>
        <div class="footer-links">
          <a href="#" class="footer-link">关于我们</a>
          <a href="#" class="footer-link">使用文档</a>
          <a href="#" class="footer-link">API参考</a>
          <a href="#" class="footer-link">联系我们</a>
        </div>
        <p class="copyright">&copy; {{ new Date().getFullYear() }} LLM Trainer. 保留所有权利。</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ArrowRight, Upload, Setting, DataAnalysis, Plus, Key, Aim, TrendCharts, Connection } from '@element-plus/icons-vue';
import { onMounted } from 'vue';

const router = useRouter();

function goToLogin() {
  router.push('/login');
}

function goToRegister() {
  router.push('/register');
}

// 创建背景粒子效果
onMounted(() => {
  createParticles();
});

function createParticles() {
  const particlesContainer = document.querySelector('.bg-particles');
  if (!particlesContainer) return;
  
  for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    
    // 随机位置
    const posX = Math.random() * 100;
    const posY = Math.random() * 100;
    
    // 随机大小
    const size = Math.random() * 5 + 2;
    
    // 随机动画延迟
    const animDelay = Math.random() * 10;
    
    particle.style.left = `${posX}%`;
    particle.style.top = `${posY}%`;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.animationDelay = `${animDelay}s`;
    
    particlesContainer.appendChild(particle);
  }
}
</script>

<!-- 导入动画库 -->
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"
/>

<style scoped>
.landing-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

.landing-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  opacity: 0.8;
}

.bg-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  background-color: rgba(99, 102, 241, 0.3);
  border-radius: 50%;
  animation: float 15s infinite ease-in-out;
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0.3;
  }
  25% {
    transform: translateY(-20px) translateX(10px) rotate(90deg);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-40px) translateX(20px) rotate(180deg);
    opacity: 0.9;
  }
  75% {
    transform: translateY(-20px) translateX(30px) rotate(270deg);
    opacity: 0.6;
  }
  100% {
    transform: translateY(0) translateX(0) rotate(360deg);
    opacity: 0.3;
  }
}

.landing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
  margin: 0;
}

.nav-buttons {
  display: flex;
  gap: 12px;
}

.landing-main {
  flex: 1;
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.hero-section {
  text-align: center;
  padding: 60px 20px;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 16px;
  background: linear-gradient(90deg, #4158D0, #C850C0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #606266;
}

.hero-description {
  font-size: 18px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 32px;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.cta-button {
  padding: 12px 24px;
  font-size: 18px;
}

.features-section {
  padding: 60px 0;
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 40px;
  color: #303133;
}

.feature-cards {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.centered-cards {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
  max-width: 1000px;
}

.feature-card {
  width: 300px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.feature-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.feature-header .el-icon {
  font-size: 24px;
  color: #409EFF;
}

.feature-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.vision-section {
  padding: 60px 0;
  background-color: rgba(245, 247, 250, 0.8);
  border-radius: 8px;
  margin: 40px 0;
}

.vision-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  margin-top: 40px;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}

.vision-card {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 90%;
  display: flex;
  gap: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.vision-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
}

.vision-icon {
  display: flex;
  align-items: flex-start;
  color: #409EFF;
  padding-top: 5px;
}

.vision-text {
  flex: 1;
}

.vision-text h3 {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin-top: 0;
  margin-bottom: 16px;
}

.vision-text p {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 20px;
}

.tech-roadmap, .feature-roadmap {
  margin-top: 20px;
}

.tech-roadmap .el-tag {
  margin-right: 10px;
  margin-bottom: 10px;
  padding: 6px 12px;
}

.feature-roadmap .el-timeline {
  margin-top: 20px;
}

.feature-roadmap .el-card {
  border-left: 4px solid #409EFF;
}

.feature-roadmap h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.get-started-section {
  text-align: center;
  padding: 60px 0;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  margin: 40px 0;
}

.section-description {
  font-size: 18px;
  color: #606266;
  margin-bottom: 32px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.action-btn {
  padding: 12px 24px;
  font-size: 16px;
}

.tech-badges {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}

.tech-badge {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
}

.landing-footer {
  padding: 40px 20px;
  background-color: #f5f7fa;
  color: #909399;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-logo-img {
  width: 30px;
  height: 30px;
}

.footer-brand {
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
}

.footer-links {
  display: flex;
  gap: 20px;
  margin: 16px 0;
}

.footer-link {
  color: #606266;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #409EFF;
}

.copyright {
  margin: 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .landing-header {
    padding: 15px 20px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 20px;
  }
  
  .feature-cards {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }
  
  .action-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>