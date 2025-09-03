#!/usr/bin/env node

/**
 * 前端环境切换脚本
 * 用于在开发、测试和生产环境之间切换
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 获取项目根目录
const ROOT_DIR = path.resolve(__dirname, '..');

// 支持的环境类型
const ENV_TYPES = ['development', 'test', 'production'];

// 环境文件映射
const ENV_FILES = {
  'development': '.env.development',
  'test': '.env.test',
  'production': '.env.production'
};

// 环境名称映射
const ENV_NAMES = {
  'development': '开发环境',
  'test': '测试环境',
  'production': '生产环境'
};

/**
 * 切换环境
 * @param {string} envType 环境类型
 */
function switchEnv(envType) {
  if (!ENV_TYPES.includes(envType)) {
    console.error(`错误: 不支持的环境类型 '${envType}'。支持的环境类型: ${ENV_TYPES.join(', ')}`);
    process.exit(1);
  }
  
  const sourceFile = path.join(ROOT_DIR, ENV_FILES[envType]);
  const targetFile = path.join(ROOT_DIR, '.env');
  
  if (!fs.existsSync(sourceFile)) {
    console.error(`错误: 环境配置文件 '${sourceFile}' 不存在`);
    process.exit(1);
  }
  
  try {
    fs.copyFileSync(sourceFile, targetFile);
    console.log(`成功: 已切换到${ENV_NAMES[envType]}配置`);
    
    // 清除缓存（可选）
    try {
      console.log('正在清除缓存...');
      execSync('npm run clean', { cwd: ROOT_DIR, stdio: 'inherit' });
    } catch (e) {
      console.log('注意: 清除缓存失败，可能需要手动重启开发服务器');
    }
  } catch (e) {
    console.error(`错误: 无法切换环境配置: ${e.message}`);
    process.exit(1);
  }
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('当前可用环境:');
    ENV_TYPES.forEach(env => {
      console.log(`  - ${env}: ${ENV_NAMES[env]}`);
    });
    console.log('\n使用方法: node switch-env.js <环境类型>');
    process.exit(0);
  }
  
  switchEnv(args[0]);
}

main();