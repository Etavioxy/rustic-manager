# Rustic Manager 规格说明

**架构原则：一个 rustic 仓库对应一个 rustic-manager 实例**

## 模块A：智能定时备份

**功能：**
- 使用APScheduler定时调度
- 调用`rustic backup --skip-if-unchanged`
- 根据备份结果动态调整频率

## 模块B：磁盘空间监控

**功能：**
- 每日固定时间检查磁盘空间
- 记录历史数据到SQLite数据库
- 多级预警：70%（信息）、80%（警告）、90%（严重）

**数据表：**
- `disk_usage`: 记录每日磁盘使用情况
- `backup_history`: 记录备份历史

**技术栈：**
- Rust + sysinfo + rusqlite

## 模块C：离线Web面板

**功能：**
- 本地HTTP服务器
- 展示文件修改时间线
- 展示磁盘空间曲线
- 展示备份历史统计

**技术栈：**
- Rust + actix-web + serde
- 前端框架：待定

## 数据存储

- SQLite数据库：`data/rustic-manager.db`
- 配置文件：`config/app.toml`

## 预警通知

- 控制台输出
- 日志文件记录
- Windows系统通知
