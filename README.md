# ML-Platform

这是一个支持PMML，ONNX，Keras的机器学习模型服务管理平台。允许对模型进行部署。

## 使用说明

### 构建

前端需要使用yarn进行构建，需要npm 16，更高的版本可能有支持问题。输入如下指令安装yarn

```shell
npm install -g yarn
```

来到Frontend/ml-platform下，输入命令

```shell
yarn install
yarn build
```

安装依赖项，并进行编译。编译完的前端在dist文件夹下。

### 部署

打开Frontend/ml-platform/deploy/nginx.conf

依使用需求，将其中的47.94.221.102替换为部署端的公网ip或局域网ip。

随后返回项目根目录。安装好docker和docker-compose后，输入以下命令

```shell
docker-compose build
docker-compose up
```

此时已经成功部署，前端在本机8000端口，后端在本机8001端口。
## 示例

请参考使用文档 [使用文档](使用文档.pdf)。

## 参考仓库

- [DaaS-Client](github.com/autodeployai/daas-client) — 使用Python与PMML，ONNX，Keras模型进行交互。

## 使用许可

[MIT](LICENSE) © Richard Littauer
