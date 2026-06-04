# Low-Light Segmentation Paper Agent

## 安装

```bash
python -m pip install -r requirements.txt
```

## 用法

```bash
python agent.py --input data/papers/example.pdf --mode auto
python agent.py --input notes/example.md --mode default
python agent.py --input data/papers/example.pdf --mode multimodal
```

## 模式说明

- `default`：只走本地解析
- `auto`：默认模式，解析质量差时建议切换多模态
- `multimodal`：强制按多模态场景处理

## 第一版能力边界

当前版本优先保证：

- PDF 与 Markdown 输入
- 六段式结构化输出
- 面向低光照夜间语义分割的研究关联分析

当前版本暂不保证：

- 图表级精读
- 大规模论文库管理
- 实验日志自动解析
