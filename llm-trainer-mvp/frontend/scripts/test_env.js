#!/usr/bin/env node

/**
 * 前端环境配置测试脚本
 * 用于测试不同环境的配置加载
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 获取项目根目录
const ROOT_DIR = path.resolve(__dirname, '..');

// 支持的环境类型
const ENV_TYPES = ['development', 'test', 'production'];

/**
 * 打印带有分隔符的标题
 */
function printHeader(text) {
  console.log('\n' + '='.repeat(50));
  console.log(` ${text} `);
  console.log('='.repeat(50));
}

/**
 * 测试指定环境的配置
 */
async function testEnv(envType) {
  printHeader(`测试 ${envType} 环境配置`);
  
  // 切换环境
  console.log(`切换到 ${envType} 环境...`);
  execSync(`node ${path.join(__dirname, 'switch-env.js')} ${envType}`, { stdio: 'inherit' });
  
  // 读取当前环境配置
  const envFile = path.join(ROOT_DIR, '.env');
  const envContent = fs.readFileSync(envFile, 'utf8');
  
  // 解析环境变量
  const envVars = {};
  envContent.split('\n').forEach(line => {
    if (line && !line.startsWith('#')) {
      const [key, value] = line.split('=');
      if (key && value) {
        envVars[key.trim()] = value.trim();
      }
    }
  });
  
  // 打印环境变量
  console.log('当前环境变量:');
  console.log(JSON.stringify(envVars, null, 2));
  
  // 验证环境类型
  if (envVars.VITE_APP_ENV) {
    const expectedEnv = envType === 'development' ? 'dev' : 
                       envType === 'production' ? 'prod' : 'test';
    
    if (envVars.VITE_APP_ENV === expectedEnv) {
      console.log(`✅ 环境类型验证通过: ${envVars.VITE_APP_ENV}`);
    } else {
      console.log(`❌ 环境类型验证失败: 期望 ${expectedEnv}, 实际 ${envVars.VITE_APP_ENV}`);
    }
  } else {
    console.log('❌ 环境类型验证失败: 未找到 VITE_APP_ENV 变量');
  }
  
  // 验证API URL
  if (envVars.VITE_APP_API_URL) {
    let expectedUrl = 'http://localhost:8001';
    if (envType === 'production') {
      expectedUrl = 'https://api.llm-trainer.example.com';
    }
    
    if (envVars.VITE_APP_API_URL === expectedUrl) {
      console.log(`✅ API URL验证通过: ${envVars.VITE_APP_API_URL}`);
    } else {
      console.log(`❌ API URL验证失败: 期望 ${expectedUrl}, 实际 ${envVars.VITE_APP_API_URL}`);
    }
  } else {
    console.log('❌ API URL验证失败: 未找到 VITE_APP_API_URL 变量');
  }
}

/**
 * 主函数
 */
async function main() {
  printHeader('前端环境配置测试开始');
  
  for (const env of ENV_TYPES) {
    await testEnv(env);
  }
  
  printHeader('前端环境配置测试完成');
}

// 执行主函数
main().catch(err => {
  console.error('测试过程中发生错误:', err);
  process.exit(1);
});