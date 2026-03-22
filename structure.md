# 项目文件布局

```
rustic-manager/
├── config/
│   └── app.toml
│
├── data/
│   └── rustic-manager.db
│
├── logs/
│   └── rustic-manager.log
│
├── manager/
│   ├── main.py
│   ├── scheduler.py
│   ├── backup.py
│   ├── database.py
│   └── requirements.txt
│
├── panel/
│   ├── package.json
│   ├── electron/
│   │   ├── main.js
│   │   └── preload.js
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── DiskChart.vue
│   │   │   ├── BackupChart.vue
│   │   │   └── DateRangePicker.vue
│   │   └── utils/
│   │       └── chart.ts
│   ├── index.html
│   └── vite.config.ts
│
├── spec.md
├── structure.md
└── README.md
```
