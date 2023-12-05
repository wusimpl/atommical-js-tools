# Atomicals dmint 进阶指南

![](/Users/williamsandy/Pictures/0a5501d3-bc32-432c-955a-465136d5f992.jpg)



## 一、写在前面

鉴于 Atomicals 生态还十分早期，并且前端 mint 也要收服务费，掌握使用官方脚本进行 mint 的方法还是十分必要的，本文将从安装 atomcials-js 脚本开始到如何使用脚本 dmint，再到如何查看 container 元数据与 item 查重进行详细介绍。

不了解 dmint？请先参考这篇文章：[Atomicals dmint 简易指南 — wusimpl (mirror.xyz)](https://mirror.xyz/wusimpl.eth/0RGSKVlw07OvW0LzPNHv60M9ZOmU4navEgIIKw2NlPY)

本文略长，请勿紧张，可直接跳至感兴趣处阅读。



## 二、命令行的基本知识（熟悉者可以跳过此节）

命令行终端是操控电脑运行各种程序的字符界面程序，相比可视化界面来说更加简洁，快速，但是上手难度也比较大。

首先了解第一个概念：**当前工作目录**，这表明你的所有指令都相对于你的当前工作目录来寻找其他文件或文件夹。查看当前工作目录的命令是：

`pwd`

执行结果：

![](/Users/williamsandy/Pictures/ada32701-afe3-4256-9509-60f2cde351b6.jpg)

可以看到我当前的目录是**/Users/williamsandy**

现在我想要跳转到**/Users/williamsandy/code**目录，可以使用命令：

`cd code`

或者

`cd ./code`

**.**表示当前目录，可以省略。

执行结果：

![](/Users/williamsandy/Pictures/8ca48413-2ca2-40d9-8296-fb699a34254d.jpg)

然后我想查看这个目录有什么文件，可以使用命令：

`ls`

![](/Users/williamsandy/Pictures/b9f9be14-74e0-4ef0-895d-400aca57db8f.jpg)

可以看到我的 code 目录有一个文本文件 **abc.txt**和一个文件夹**atomicals-js**。



## 三、安装 atomcials-js 脚本

1. 安装 node.js

首先请确保你已经安装了 node.js，且可以在命令行中成功查看到 node 版本。

查看 node 版本的命令：

`node -v`

执行结果：

![](/Users/williamsandy/Pictures/e4ca6b5f-efc4-495e-974b-9c25a77e48e0.jpg)

我电脑上的版本是 v16，大家安装的版本可能有所不同。

2. 安装 git

node.js 和 git 工具网上教程多如牛毛，请大家自行安装。

![](/Users/williamsandy/Pictures/b31a5f28-2cb9-4690-9bed-c92914560ae7.jpg)

3. 下载 atomicals-js 代码

现在我想将 atomicals-js 代码下载到**/Users/williamsandy/code/**目录下，所以我先执行：

`cd ./code`

![](/Users/williamsandy/Pictures/6412972c-3cdc-471b-b739-3aecfd78d407.jpg)

然后执行 clone 命令：

`git clone https://github.com/atomicals/atomicals-js`

![](/Users/williamsandy/Pictures/a66db321-4841-46dd-8359-3c496a8916da.jpg)

然后执行：

`ls`

![](/Users/williamsandy/Pictures/eb06a5f8-8c3f-44b8-ab02-d5d0618ca170.jpg)

可以看到代码已经被我们下载到了 code 目录，然后我进入 **atomicals-js**目录。

`cd ./atomicals-js`

4. 安装依赖项

使用 npm 包管理工具安装 atomicals-js 需要的依赖：

`npm install`

执行结果：![](/Users/williamsandy/Pictures/e28f4841-3e91-4835-a024-f98a2a939817.jpg)

可以看到执行失败了，**ERR**就是error，失败的意思，原因也写得很清楚了：**invalid version**。从 stackoverflow（[Npm ERR! Invalid version on npm install - Stack Overflow](https://stackoverflow.com/questions/71383116/npm-err-invalid-version-on-npm-install)） 的回答可以得知，可能是 yarn.lock 或者 pnpm-lock.yaml 文件的问题，让我们来把这两个碍事的文件删掉：

`rm yarn.lock pnpm-lock.yaml`

然后再执行：

`npm install`

![](/Users/williamsandy/Pictures/a0708cfe-85be-462d-9bfb-58e7202f67cc.jpg)

这下没有报错了，虽然有很多烦人的 WARNING 警告信息，但这不影响运行。

5. 编译

使用命令：

`npm run build`

![](/Users/williamsandy/Pictures/3bac660a-6e5f-49b1-a962-9e7b8f205d8a.jpg)

可以看到我已经成功编译，没有显示异常的日志信息。

7. 使用 atomicals-js 工具

运行命令：

`node dist/cli.js -h`

![](/Users/williamsandy/Pictures/986b67d6-9e00-4c96-9605-34510f304125.jpg)

可以看到 cli.js 打印出了 Atomicals CLI 工具的使用方法，大家可以把这些输出喂给GPT或者翻译就知道这些命令分别是什么意思了。

所以 Atomicals CLI 工具的基本用法就是：

`node dist/cli.js <command> <options>`

**\<command\>** 和 **\<options\>** 可以填什么东西命令行都给你打印出来了。

对于 \<options\>，可以填 -v 和 -h，表示输出版本或者帮助的意思，比如我上面的呐喊命令中的 -h 就是输出 cli.js 的帮助文本。

8. 初始化钱包

使用命令：

`node dist/cli.js wallet-init`

来初始化钱包。初始化的本质是创建一个 wallet.json 文件来保存钱包的私钥。

![](/Users/williamsandy/Pictures/1cb2a774-97e4-46e4-be03-d881891c906c.jpg)

可以看到 wallet.json 中有钱包的助记词，通过助记词生成了两个私钥，一个私钥地址叫做**primary**，一个叫做**funding**，funding wallet 默认作为花费 btc 的钱包，primary wallet 默认作为接收 atomicals 的钱包。

**atomicals-js**工具最近的升级将 wallet.json 放到了 **./wallets/wallet.json**下面。其实并不是非要执行 **node dist/cli.js wallet-init**命令，你完全可以把一个格式正确的 wallet.json 文件放在 ./wallets 目录下，这样也算完成了初始化。

*现在你已经完成了使用Atomicals CLI工具的所有必备条件，可以开始你的 Atomicals 之旅了！*

下面是一些可选操作。

9. 更改 Atomicals RPC 索引节点（可选）

代码根目录中的 **.env**文件存放着节点的配置信息，更改此文件可以配置节点信息。

![](/Users/williamsandy/Pictures/b9c30ec5-b2f8-4b53-ad5c-015f881ad71c.jpg)

大家可以使用文本编辑器编辑 .env 文件来更改节点：

![](/Users/williamsandy/Pictures/33129b44-7bc4-490f-8eaf-e064f8a0befa.jpg)

可以看到 .env 文件总共只有4行配置是有效的，以 # 开头的行都是注释！

而第 13 行的 **ELECTRUMX****\_PROXY****\_BASE****\_URL** 就是节点配置信息，比如我想使用 NextDAO 的公共节点可以这么写：

`ELECTRUMX_PROXY_BASE_URL=https://ep.nextdao.xyz/proxy`

如果自己配置了节点，也可以改成自己的节点位置，比如我在我局域网的**10.110.8.8**的6000端口搭建了 Atomicals ElectrumX Server服务，那么可以写成：

`ELECTRUMX_PROXY_BASE_URL=http://10.110.8.8:6000/proxy`

或者我在本机的5050端口搭建了节点，那么可以写成：

`ELECTRUMX_PROXY_BASE_URL=http://localhost:5050/proxy`



可用的公共节点列表请参考：[https://x.com/wusimpl/status/1729829443097526572?s=20](https://x.com/wusimpl/status/1729829443097526572?s=20)

搭建个人 atom 节点可参考：[Web5 ｜ BTC 生态](https://web5.ink/insc/btc)



10. 简化 CLI 命令的使用（可选）

安装另一个包管理工具**yarn**可简化命令的使用。

原来的命令是：

`node dist/cli.js <command> <option>`

安装 yarn 之后，命令是：

`yarn cli <command> <option>`

也就是 **node dist/cli.js**和 **yarn cli**等效。



## 四、查看 Container 元数据

可以简单的把 Atomicals 的 Container 理解为以太坊三的 NFT Collection，即一个 NFT 集合。

CLI 工具提供了查询 container 元数据的方法，这对我们想 mint 这个 container 的用户来说特别重要，因为其中包括了稀有度分级、难度、支付给项目方的费用、mint 激活时间等信息。

查询命令：

`yarn cli get-container-items <container name> 0 0`

比如我想查询 crabada 的信息：

`yarn cli get-container-items crabada 0 0`

输出了一个大堆东西，是一个 json 文件，由于文件太长，我这里只展示部分内容。

1. 首先是容器的名字：

![](/Users/williamsandy/Pictures/a1d886b8-4384-49a5-9ade-b2eb3b808c2d.jpg)

2. 然后是 mint 规则，这个最为重要：

![](/Users/williamsandy/Pictures/ff809238-2cf6-4bd5-8d99-8ceeb3514a22.jpg)

rules 里面是一个数组，里面有若干条规则，每条规则用 { } 包裹。我们来看第一条规则：

![](/Users/williamsandy/Pictures/38deb374-0370-4d4e-94c0-8588c1d792c2.jpg)

o字段：第一行表示需要向脚本**512031994d8ee86db69f327bc54f675d8ff6349fc0e28d1defe52dd17e4fbf4026dd**输出 88888 sats

p字段：匹配该规则的 item，用正则表达式规定。例如正则表达式**^[0-7]$**的含义就是匹配以 0~7 开头的 item。比如你想打的 NFT 的编号是 1233，那么你就需要符合这条规则。

bitworkc字段：这表明你要提交该 mint 交易时需要的工作量。例如**81981981.9**表示你的 commit tx id 前8位必须是89981981，第9位必须是 9~f 的数字（16进制）。需要匹配八位数字，这个 POW 的难度可以说是非常难了，一般匹配 7 位数都需要花上个人电脑 CPU 几天的时间来计算。

综上所述，第一条规则的意思就是：mint token id 以0～7开头的 NFT 需要支付 88888 聪的费用，并且需要完成前缀为81981981.9的POW证明。



我们再来看最后一条规则：

![](/Users/williamsandy/Pictures/27a5bc12-8a3f-4baa-ada8-97312513c4ea.jpg)

有了上面的解释，这条规则的含义就很清晰了，除了前面几条规则匹配到的 Token ID，剩下的所有其他 NFT，需要支付 19999 聪的费用，并完成前缀为 8198.10 的POW证明（**.****\***的意思就是匹配所有情况）。

3. 激活高度与总量

![](/Users/williamsandy/Pictures/a5b578cb-5490-419e-a561-949d817312e2.jpg)

在规则后面，就显示了 **mint****\_height**和**items**信息，他们一个是可以开始 mint 的区块高度，一个是这个容器所含的 NFT 总量。

4. 其他信息

返回的整个 json 还包含了很多其他可能有用的东西，比如这个容器的唯一编号 **atomical****\_id**，有兴趣的朋友请自行研究吧。



另外我将 Atomicals 的官方文档爬了下来做了一个 GPTs，开通了 ChatGPT Plus的朋

友有问题可以问它噢！但不保证答案正确哈：[https://chat.openai.com/g/g-WIsAjMyLg-atomicals-guide](https://chat.openai.com/g/g-WIsAjMyLg-atomicals-guide)



## 五、查重

查重是 dmint 你看中的 NFT 之前的必备工作，因为你不知道链上是否有其他人已经提交了该 NFT 的 mint，所以在 mint 之前一定要查重，并且在 POW 计算的过程中，每产生一个新的区块就要查重一次，如果发现有人已经 mint 了你的编号，马上换其他编号。

这里有一个极端情况——你和你的对手（mint 同一个 token id 的人）在同一个区块提交了 commit 交易，据群友的经验，似乎 gas 高的那一方会成为获胜者，所以真正的查重还需要查询内存池里面的交易，但这已经超出了本文的范畴。

查重的命令很简单：

`yarn cli get-container-item <container name> <token id>`

例如我想打capybaras的8601号 NFT，它长这样：

![](/Users/williamsandy/Pictures/89bc25d2-db4a-46be-a65c-86f140c9ad1e.jpg)

那么命令就是：

`yarn cli get-container-item capybaras 8601`

返回的结果也是 json：

![](/Users/williamsandy/Pictures/b8021335-f9a4-4299-9af7-f2298e092b8d.jpg)

可以看到 status 为 verfied，这说明这个 NFT 已经被 mint，且距离 mint 成功已经过了四个区块，是铁打不动的再也没人能抢走的了。

如果 status 是 pending，就说明 mint 交易已经成功，但是还没有过四个区块，这个时候仍是悬而未定的，但是也和你没关系了，直接换另一个 token id 吧。

如果 status 是 null，那么就可以 mint，但是不能确保内存池中是否已经存在和你 token id 相同的 commit 交易。

![](/Users/williamsandy/Pictures/31895c6b-46f5-49f8-83e5-e3532f766610.jpg)

我们来看 toothy 6666 号的查重信息（截取了部分）：

![](/Users/williamsandy/Pictures/5edaf7ed-435e-4732-9969-6ee748570949.jpg)

可以看到 candidates 字段有3个元素，很明显第2和第3个打废了，第2个虽然和第1个在同一个区块成交（819181），但是第一个给的 gas 应该高一些，我们来用 txid 在区块链浏览器查一下：

候选人1:

![](/Users/williamsandy/Pictures/547fdfb0-5058-4c06-9f6d-11bcfed87a15.jpg)

候选人2:

![](/Users/williamsandy/Pictures/1c0236dd-06b8-4cb8-9010-0c938db2a089.jpg)

可以看到候选人1给的 gas 是 166，而候选人2只有100。



## 六、mint

有了上面的铺垫之后，mint 也就是一个命令的事：

`yarn cli mint-item <container name> <token id> <manifest file>`

需要着重解释的是 \<manifest file\> 这个字段，它是你 token id 对应的 json 文件的路径，里面包含 \<token id\> 号 NFT 的元数据，包括这个 NFT 图片的二进制数据。它通常由项目方提供下载。

如果你需要 mint-item 命令的详细帮助，可以执行：

`yarn cli mint-item -h`

![](/Users/williamsandy/Pictures/169fd61b-b040-4c4f-bce3-632992c749e1.jpg)

这里值得关注的是上面红框中的 5 个选项。

--rbf：如果开启，这笔交易就可以加速了，如果你后面发现 gas 不够，那么开启这个选项就可以使用 Sparrow Wallet 等支持加速的钱包软件来加速该笔交易。这应该是最近才更新的功能。

--initialowner：mint 到的 NFT 发到哪一个地址，也就是我们通常说的接收地址（receive address）。

--satsbyte：这个没什么好说的，就是gas fee，听说已经修复了实际 gas 比给的 gas 高很多的 bug，我还没测试。

--funding：就是你要用哪个钱包付款，就是我们通常说的 funding address，你 mint 的时候跳出来的那个二维码地址，就是 funding address。

--disablechalk：关闭挖矿时每个哈希实时记录的功能。设置此项可以提高挖矿性能。



要注意 **initialowner**和 **funding**选项，后面跟的是这个钱包的别名，而不是钱包的地址，例如我的 wallet.json 长这样：

![](/Users/williamsandy/Pictures/fe486c64-29db-470c-b7ff-65bae72b817b.jpg)

我导入了两个钱包，一个取名为 AAA，一个 BBB，那么我就可以吧 AAA 或者 BBB 作为 接收钱包或者发送钱包，可能的命令例如：

`yarn cli mint-item crabada 1111 ./crabada/item-1111.json --initialowner AAA --funding BBB --satsbyte 40`



## 七、结语

感谢能坚持看到此处的朋友！Atomicals Proctocol 很年轻，但这里已经聚集了很多优秀的 builder 和 contributers，还有很多看好 Atomicals 的人，如果你认为 Atomicals 未来也大有可为，欢迎关注我的推特，获得更多 Atomicals 相关的知识、脚本等。

个人推特：[wusimpl (@wusimpl) / Twitter](https://twitter.com/wusimpl)

