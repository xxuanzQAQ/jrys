# JRYS · 今日运势

基于 [gsuid_core](https://github.com/Stareven233/gsuid_core) 框架的今日运势插件，玄学解卦风格，生成精美运势卡片图片。

---

## 功能预览

- 根据用户 ID + 日期生成专属运势，同一天多次查询结果相同
- 运势卡片包含：卦象标题、星星评级（0~10 星）、爻辞（两列两行）、四维属性条、占断建议
- 支持随机背景图叠加，自动渐变融合
- SSAA 2× 超采样渲染，输出 540px 高清无锯齿图片
- 主题随机（秋叶 / 樱花 / 冰雪 / 森系 / 星空）

---

## 命令列表

| 命令 | 说明 |
|---|---|
| `今日运势` / `运势` / `jrys` | 获取今日运势卡片 |
| `悔签` / `重新抽取运势` | 重新抽取运势（每日限一次） |
| `逆天改命` / `改命` / `nitiangaiming` | 消耗一次改命机会重新生成运势（每日限 2 次，20% 概率失败） |
| `随机背景` / `随机运势图` / `jrysn` | 预览一张随机背景图 |

### 逆天改命规则

- 普通用户每日最多改命 **2 次**，有 **20% 概率失败**（失败仍消耗次数）
- 成功后 70% 倾向抽到好运势，30% 完全随机
- **Bot 主人（masters）** 拥有无限改命权限，必定成功，不消耗次数

---

## 安装方法

在 gsuid_core 管理面板的插件市场中搜索 `JRYS` 安装，或手动克隆到插件目录：

```bash
cd gsuid_core/plugins
git clone https://github.com/<your-username>/JRYS.git
```

重启 gsuid_core 后插件自动加载。

---

## 背景图配置

将 JPG / PNG / WebP 格式的图片放入以下目录，插件会随机选取作为运势卡片背景：

```
gsuid_core/plugins/JRYS/JRYS/utils/resource/bg/
```

- 不放置背景图也可正常使用，卡片将以主题纯色背景显示
- 建议图片尺寸不低于 540×400 像素，竖向图片效果更佳

---

## 配置项

在 gsuid_core 管理面板 → 插件配置 → JRYS 中可修改：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `BotName` | `命运` | 显示在运势建议框左侧的机器人名称 |

也可直接编辑 `data/JRYS/config.json`：

```json
{
  "BotName": "小维"
}
```

---

## 主人权限

gsuid_core 系统配置中 `masters` 列表内的用户 ID 即为主人，享有：

- 逆天改命无限次数
- 改命必定成功
- 次数不累计

主人 ID 在 gsuid_core 系统设置（`core_config` → `masters`）中配置。

---

## 目录结构

```
JRYS/
├── README.md
├── pyproject.toml
├── __init__.py
├── __nest__.py
└── JRYS/
    ├── __init__.py
    ├── __full__.py
    ├── jrys.py            # 核心逻辑与绘图
    ├── jrys_config.py     # 插件配置
    └── utils/resource/
        ├── RESOURCE_PATH.py
        ├── bg/            # 背景图目录（自行放置）
        └── cache/         # 用户运势缓存（自动生成）
```

---

## 免责声明

本插件内容纯属娱乐，所有运势结果均为随机生成，不代表任何真实预测。
请相信科学，勿迷信占卜。

