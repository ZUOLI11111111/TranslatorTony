# 翻译应用Java后端数据存储

这是翻译应用的Java后端组件，用于存储翻译记录和用户数据。使用Spring Boot和MySQL数据库实现。

## 技术栈

- Java 11
- Spring Boot 2.7.x
- Spring Data JPA
- MySQL 8.0
- Maven

## 功能特性

- 存储翻译记录到MySQL数据库
- 提供RESTful API访问翻译历史
- 支持按用户、语言、时间查询翻译记录
- 提供数据统计功能
- 支持搜索翻译记录
- 管理界面用于查看和管理翻译记录

## 安装与配置

### 前提条件

- JDK 11或更高版本
- Maven 3.6或更高版本
- MySQL 8.0

### 配置MySQL

1. 确保MySQL服务已启动
2. 创建数据库（应用程序会自动创建，也可手动创建）：

```sql
CREATE DATABASE translator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 如需修改数据库连接参数，编辑`src/main/resources/application.properties`文件

### 构建与运行

```bash
# 克隆项目
git clone <repository-url>
cd translator-app/java-backend

# 编译
mvn clean package

# 运行
java -jar target/translator-java-backend-0.0.1-SNAPSHOT.jar

# 或使用Maven直接运行
mvn spring-boot:run
```

## API文档

### 翻译记录接口

| 路径 | 方法 | 说明 |
|-----|-----|-----|
| `/api/translations` | POST | 保存翻译记录 |
| `/api/translations/{id}` | GET | 获取指定ID的翻译记录 |
| `/api/translations/{id}` | DELETE | 删除指定ID的翻译记录 |
| `/api/translations/user/{userId}` | GET | 获取指定用户的翻译记录 |
| `/api/translations/search` | GET | 搜索翻译记录 |
| `/api/translations/stats` | GET | 获取翻译统计信息 |

## 与Python后端集成

本Java后端可以与现有的Python后端集成，在每次翻译完成时自动保存记录到数据库。集成方式如下：

1. 在Python后端的`.env`文件中配置Java后端URL：

```
JAVA_BACKEND_URL=http://localhost:8080/api/translations
```

2. Python后端会在每次翻译完成后，通过HTTP POST请求将记录发送到Java后端存储

## 管理界面

访问Java后端的根路径可以打开管理界面：

```
http://localhost:8080/
```

通过管理界面可以：
- 查看所有翻译记录
- 搜索特定翻译
- 查看翻译详情
- 删除不需要的记录
- 查看翻译统计数据

## 许可证

MIT 