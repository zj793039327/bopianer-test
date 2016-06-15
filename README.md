# 开发必读
##微信调试相关
###微信测试账号申请
####开通
每个人都可以申请测试账号,访问[这个地址][1]开通即可，微信扫一扫就可以了

测试号申请完成以后，会有对应的appid与秘钥，填写到后面的配置中即可, 需要特殊注意的有三个地方：

1. **JS接口安全域名配置**
2. **网页授权获取用户基本信息** 

注意：对于测试账号，这两个地址可以是ip

####JS接口安全域名配置
这个安全域名，主要与后期在html调用微信功能有关系，需要配置到主域名即可， 比如“baidu.com”

####网页授权获取用户基本信息
这个域名是用来获取用户的openid的，主要是微信验证和回调使用的，需要配置到你自己的详细域名，不能只是主域名

###微信web开发工具
微信提供了专门的开发者工具，利用工具，可以mock一部分功能，进行jssdk的相关开发，其数据都是测试用的
[地址][2]

微信开发工具也可以直接调试微信公众号，只不过域名可能有问题，这个还需要验证
###ngrok域名工具
为了支持调试，可以采用曲线救国的办法，通过ngrok，将自身电脑上的端口绑定到ngrok的网址中进行调试。代价就是比较慢和不稳定

[地址][3]

具体使用方式就是下载ngrok的包，在命令行执行：

```bash
./ngrok http 8000
# 如果网速太慢， 可以参考
# ./ngrok http -region eu 8000 # 调整连接的区域，参考命令./ngrok help http
```
而且还可以访问 localhost：4040查看请求的情况
ngrok比较鸡贼， 每次启动都会变换域名，如果想绑定一个域名，则需要交费。。。（2015年的时候，貌似还是免费的）

一旦这个启动以后，就好办了

可以通过域名直接在设备上面调试本机程序

##django环境相关
###部署环境
1. 安装python2.7的环境，具体不在赘述
2. 安装pip工具，pip是python下的包管理工具
3. 通过pip安装以下依赖：
```bash
Django (1.9.4)
mysqlclient (1.3.7)
oss2 (2.1.1)
pip (8.1.2)
pycrypto (2.6.1)
requests (2.6.0)
setuptools (19.4)
six (1.10.0)
wechat-sdk (0.6.3)
wheel (0.26.0)
xmltodict (0.9.2)
```

###修改配置
1. 数据库配置, 替换对应的数据库以及用户名密码
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bopianer',
        'USER': 'root',
        'PASSWORD': '12345678',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}
```


3. 微信参数配置

按照上一个步骤中申请的结果, 修改即可
```python
WECHAT_APPID = 'wx27fe96e421ebb5d4'
WECHAT_APPSECRET = '12f2f4302ef8ede31fa40148098d2c75'
WECHAT_TOKEN = '123123123'

ASSET_ENCRYPT_KEY = 12345678

```

###启动服务

1. 创建表结构
由于django的特性, 需要根据model生成数据库表, 执行以下命令, 进行创建, 在项目的根目录中
```bash
#1. 
manage.py migrations
#2.
manage.py migrate
```
没有错误的信息化, 就是执行成功

2. 运行程序, 运行程序可以通过命令行进行, 也可以通过idea,pycharm等IDE进行启动, 下面介绍命令行的
```bash
manage.py runserver 8000 # 此处端口可以自己制定, 默认8000
```


##接口相关

### 业务接口
参见rap


[1]: http://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index "微信测试号"
[2]: https://mp.weixin.qq.com/wiki/10/e5f772f4521da17fa0d7304f68b97d7e.html "微信开发者工具"
[3]: ngrok.com "域名处理"