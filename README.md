# AssistGen - 基于大语言模型构建的智能客服系统

一个基于 FastAPI 和 Vue 3 构建的前后端分离的智能客服助手项目，支持多种大语言模型，如DeepSeek V3，Qwen2.5系列，Llama3系列等。涵盖了 Agent、RAG 在智能客服领域的主流应用落地需求场景。 

## 功能特性

### 1. 通用问答能力
- **支持 DeepSeek V3 在线API**
- **支持 使用 Ollama 接入任意对话模型，如Qwen2.5系列，Llama3系列**
- **灵活的模配置**

### 2. 深度思考能力
- **支持 DeepSeek R1 在线API**
- **支持 使用 Ollama 接入任意 Deepseek r1 模型系列**
- **灵活的模配置**


### 3. ollama 性能测试工具
- 单请求性能测试
- 并发性能测试
- 系统资源监控
- 自动化测试报告

## 快速启动

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 文件到 `llm_backend/.env` 文件中，并根据实际情况修改配置：

```env
# LLM 服务配置
CHAT_SERVICE=OLLAMA  # 或 DEEPSEEK
REASON_SERVICE=OLLAMA  # 或 DEEPSEEK

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=deepseek-coder:6.7b
OLLAMA_REASON_MODEL=deepseek-coder:6.7b

# DeepSeek 配置（如果使用）
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```
### 3. 安装Mysql数据库并在 `.env` 文件中配置数据库连接信息

### 4. 启动服务

```bash
# 进入后端目录
cd llm_backend

# 启动服务（默认端口 9000）
python run.py

# 如果需要修改 IP 和端口，编辑 run.py 中的配置：
uvicorn.run(
    "main:app",
    host="0.0.0.0",  # 修改监听地址
    port=8000,       # 修改端口号
    access_log=False,
    log_level="error",
    reload=True
)
```

服务启动后可以访问：
- API 文档：http://localhost:8000/docs
- 前端界面：http://localhost:8000

## 技术栈

- 后端：
  - FastAPI
  - SQLAlchemy
  - MySQL
  - Ollama/DeepSeek

- 前端：
  - Vue 3
  - Element Plus
  - TypeScript

## 注意事项

1. 生产环境部署时：
   - 修改 `.env` 中的 `SECRET_KEY`
   - 配置正确的 CORS 设置
   - 使用 HTTPS
   - 关闭 `reload=True`

2. 开发环境：
   - 可以启用 `reload=True` 实现热重载
   - 可以设置 `log_level="debug"` 查看更多日志

## License

MIT 

# 电商商品数据服务

这个项目提供了一个简单的Python服务，用于从Neo4j图数据库中获取电商商品信息，并通过API或Web界面将其展示给前端。

## 数据库结构

项目使用Neo4j图数据库存储电商相关数据，主要包含以下节点和关系：

### 节点 (Nodes)

1. **Product** - 商品
   - ProductID: 商品ID
   - ProductName: 商品名称
   - UnitPrice: 单价
   - UnitsInStock: 库存数量
   - UnitsOnOrder: 订购数量
   - QuantityPerUnit: 单位数量
   - Discontinued: 是否停产

2. **Category** - 商品类别
   - CategoryID: 类别ID
   - CategoryName: 类别名称
   - Description: 类别描述

3. **Supplier** - 供应商
   - SupplierID: 供应商ID
   - CompanyName: 公司名称
   - ContactName: 联系人姓名
   - Phone: 联系电话

4. **Customer** - 客户
   - CustomerID: 客户ID
   - CompanyName: 公司名称
   - ContactName: 联系人姓名

5. **Order** - 订单
   - OrderID: 订单ID
   - OrderDate: 订单日期

6. **Review** - 评论
   - ReviewID: 评论ID
   - ReviewText: 评论内容
   - Rating: 评分
   - ReviewDate: 评论日期

### 关系 (Relationships)

1. **BELONGS_TO** - 商品属于类别: (Product)-[:BELONGS_TO]->(Category)
2. **SUPPLIED_BY** - 商品由供应商提供: (Product)-[:SUPPLIED_BY]->(Supplier)
3. **CONTAINS** - 订单包含商品: (Order)-[:CONTAINS]->(Product)
4. **PLACED** - 客户下订单: (Customer)-[:PLACED]->(Order)
5. **WROTE** - 客户写评论: (Customer)-[:WROTE]->(Review)
6. **ABOUT** - 评论关于商品: (Review)-[:ABOUT]->(Product)

## 文件说明

项目包含两个主要文件：

1. **product_service.py** - 提供与Neo4j数据库交互的服务类，封装了各种查询商品信息的方法
2. **frontend_demo.py** - 基于Flask的Web应用，提供Web界面和API端点，使用product_service获取数据

## 安装依赖

```bash
pip install neo4j flask
```

## 配置数据库连接

默认连接参数:
- URI: `bolt://localhost:7687`
- 用户名: `neo4j`
- 密码: `password`
- 数据库: `neo4j`

可以通过两种方式修改:

1. 在代码中直接修改
2. 设置环境变量:
   ```bash
   export NEO4J_URI=bolt://localhost:7687
   export NEO4J_USERNAME=neo4j
   export NEO4J_PASSWORD=your_password
   export NEO4J_DATABASE=neo4j
   ```

## 使用ProductService

```python
from product_service import ProductService

# 创建服务实例
service = ProductService(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password"
)

# 使用上下文管理器自动处理连接
with service:
    # 获取类别
    categories = service.get_all_categories()
    print(f"类别数量: {len(categories)}")
    
    # 根据类别获取商品
    products = service.get_products_by_category("智能音箱")
    print(f"智能音箱类别下的商品数量: {len(products)}")
    
    # 获取商品详情
    product_details = service.get_product_details(1)
    print(f"商品详情: {product_details}")
    
    # 搜索商品
    search_results = service.search_products("智能")
    print(f"搜索结果数量: {len(search_results)}")
```

## 运行Web应用

```bash
python frontend_demo.py
```

访问 http://localhost:5000 查看Web应用。

## API端点

以下是可用的API端点:

- `GET /api/categories` - 获取所有商品类别
- `GET /api/products/category/<category_name>` - 获取指定类别下的商品
- `GET /api/products/<product_id>` - 获取指定商品的详细信息
- `GET /api/products/search?keyword=<keyword>` - 搜索商品
- `GET /api/products/featured` - 获取推荐商品
- `GET /api/products/popular` - 获取热门商品
- `GET /api/products/<product_id>/reviews` - 获取指定商品的评论

## 注意事项

1. 请确保Neo4j数据库已启动并已导入相关电商数据
2. 若要在生产环境使用，请确保添加适当的认证和安全机制
3. Web模板(HTML文件)需要自行创建在templates目录下 