# Rustic Manager 规格说明

**架构原则：一个 rustic 仓库对应一个 rustic-manager 实例**

## 模块A：智能定时备份

**功能：**
- 使用APScheduler定时调度
- 调用`rustic backup --skip-if-unchanged`
- 根据备份结果动态调整频率

**间隔变量：**
- `min`：最小间隔（默认 3 分钟）
- `max`：最大间隔（默认 30 分钟）
- `init`：初始间隔（默认 15 分钟）

**Obsidian 插件：**
- 默认：min=1.5, max=5, init=3（分钟）
- 每分钟发送心跳，超时 3 分钟恢复配置

**调度规则：**
- 开机启动 → init
- 有变更 → interval / 2（不低于 min）
- 无变更 → interval × 2（不超过 max）

## 模块B：磁盘空间监控

**功能：**
- 记录磁盘空间历史数据到SQLite
- A part 备份后检查磁盘空间变化，超过限额发送Windows通知

**配置变量：**
- `record_times`：记录时机列表（默认 `["time:0:00", "startup", "shutdown"]`）
- `change_limit`：空间变化限额（默认 30MB）

**记录时机：**
- `time:0:00`：每天 0 点
- `startup`：开机时
- `shutdown`：关机时

**预警：**
- A part 备份后检测一次
- 磁盘空间变化超过 `change_limit` 发送Windows通知

**数据表：**
- `paths`：路径映射表
  - `id`：主键
  - `path`：监控路径
  - `disk_table_name`：磁盘空间表名
  - `backup_table_name`：备份历史表名

- 每个路径独立磁盘空间表（如 `disk_usage_1`）
  - `id`：主键
  - `used_bytes`：已用空间
  - `timestamp`：记录时间

- 每个路径独立备份历史表（如 `backup_history_1`）
  - `id`：主键
  - `snapshot_id`：快照ID
  - `duration_seconds`：备份耗时
  - `space_change_bytes`：空间变化量
  - `timestamp`：备份时间

## 模块C：离线Web面板

**功能：**
- 展示磁盘空间曲线
- 展示备份历史统计

**技术栈：**
- Electron（桌面应用）
- better-sqlite3（读取数据库）

**项目结构：**
- `main.js`：主进程，读取 SQLite
- `renderer.js`：渲染进程，图表渲染
- `index.html`：界面
- `package.json`：依赖配置

**开发运行：**
```bash
npx electron .
```

**打包发布：**
```bash
npx electron-packager . rustic-panel
```

## 数据存储

- SQLite数据库：`data/rustic-manager.db`
- 配置文件：`config/app.toml`

## 预警通知

- 控制台输出
- 日志文件记录
- Windows系统通知
