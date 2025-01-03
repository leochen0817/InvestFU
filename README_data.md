## 爬虫数据

### 背景

- 金融信息来源广，且较为专业，人力资源有限
- 金融市场需要时刻行情、资金异常及舆情等
- 投资组合众多，涉及资管规模庞大

所以我们需要定制一些爬虫工具，实时监控并收录重要信息，成为数字资产重要的一环。

### Playwright爬虫

**Playwright** 是一款由 Microsoft 开发的开源自动化测试框架，专为现代 Web 应用设计。**Playwright** 提供了强大的功能，能够模拟真实用户在 Web 页面上的操作，提高了测试效率，帮助开发者和测试人员构建更高质量的软件。

#### 前置条件
```bash
项目根目录下，安装完requirements.txt之后，即已安装了Playwright相关依赖包。
不过还需要安装浏览器以适配Playwright工具。
1、保证电脑上已安装过Chrome浏览器
2、打开CMD，输入命令 playwright install chromium
如上，就完成了Playwright浏览器的安装
```

handle_cninfo.py handle_eastmoney.py handle_ssc.py 三个文件都是通过Playwright进行爬虫工作。
运行方式如下：
```bash
python handle_cninfo.py 
python handle_eastmoney.py 
python handle_ssc.py
```

### API获取数据

handle_canghai_api.py 是通过调用沧海数据的API接口获取相关数据，目前以【获取历史行情】为例，运行方式如下：
```bash
python handle_canghai_api.py 
```
**注意**：请到 https://tsanghi.com/ 注册账号，并复制token，替换token变量的值。如需大量数据，请开通沧海会员版本。

### 数据转换

handle_jsonl.py 是转换行业数据，制成标准的jsonl预训练格式。

具体可参考rag目录下的文档介绍。

