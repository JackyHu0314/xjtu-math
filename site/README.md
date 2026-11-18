# 西交数学资料站

基于 [Astro Starlight](https://starlight.astro.build/) 的西安交通大学数学与统计学院资料站。

## 本地运行

```bash
npm install
python3 scripts/sync.py   # 从 ../资料 和 ../培养方案/专业课程.csv 生成数据
npm run dev               # http://localhost:4321
```

## 目录

- `src/content/docs/plans/`：培养方案页面
- `src/content/docs/courses/<分组>/<课程>.mdx`：课程页。`sync.py` 只在页面不存在时创建，之后可以手写「课程简介」「学习经验」
- `src/content/docs/more/`：竞赛与暑校、讲座与讨论班等
- `src/data/*.json`：由 `sync.py` 生成，不要手改
- `scripts/sync.py`：新增课程时在 `COURSES` 里加一行（课程名 → 侧边栏分组、URL）

## 资料文件

`public/files/` 是指向 `../资料` 各子目录的符号链接（由 `sync.py` 创建，已 gitignore；`参考书_版权所有_不公开` 和隐藏目录不会被链接）。
打包时这些文件会被复制进 `dist/files/`，随网站一起发布。资料多到放不下时（单文件超过 25 MB 或总量很大），再改成对象存储，并设置环境变量 `PUBLIC_FILES_BASE=https://你的存储域名`。

## 部署（Cloudflare Pages）

第一次需要登录 Cloudflare（会打开浏览器授权）：

```bash
npx wrangler login
```

之后每次更新资料或页面，运行一条命令即可：同步数据 → 打包 → 发布。

```bash
npm run deploy
```

网站地址：https://xjtu-math-materials.pages.dev（生产分支为 production）
