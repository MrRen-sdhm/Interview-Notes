# Git概览⭐️

## 1. 集中式与分布式

Git 属于分布式版本控制系统，而 SVN 属于集中式。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208200656794.png"/> </div><br>

集中式版本控制只有中心服务器拥有一份代码，而分布式版本控制每个人的电脑上就有一份完整的代码。

集中式版本控制有安全性问题，当中心服务器挂了所有人都没办法工作了。

集中式版本控制需要连网才能工作，如果网速过慢，那么提交一个文件会慢的无法让人忍受。而分布式版本控制不需要连网就能工作。

分布式版本控制新建分支、合并分支操作速度非常快，而集中式版本控制新建一个分支相当于复制一份完整代码。



## 2. 中心服务器

中心服务器用来交换每个用户的修改，没有中心服务器也能工作，但是中心服务器能够 24 小时保持开机状态，这样就能更方便的交换修改。

Github 就是一个中心服务器。



## 3. 工作流

新建一个仓库之后，当前目录就成为了工作区，工作区下有一个隐藏目录 .git，它属于 Git 的版本库。

Git 的版本库有一个称为 Stage 的暂存区以及最后的 History 版本库，History 存储所有分支信息，使用一个 HEAD 指针指向当前分支。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208195941661.png"/> </div><br>

- git add files 把文件的修改添加到暂存区
- git commit 把暂存区的修改提交到当前分支，提交之后暂存区就被清空了
- git reset -- files 使用当前分支上的修改覆盖暂存区，用来撤销最后一次 git add files
- git checkout -- files 使用暂存区的修改覆盖工作目录，用来撤销本地修改

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208200014395.png"/> </div><br>

可以跳过暂存区域直接从分支中取出修改，或者直接提交修改到分支中。

- git commit -a 直接把所有文件的修改添加到暂存区然后执行提交
- git checkout HEAD -- files 取出最后一次修改，可以用来进行回滚操作

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208200543923.png"/> </div><br>



## 4. 分支实现

使用指针将每个提交连接成一条时间线，HEAD 指针指向当前分支指针。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208203219927.png"/> </div><br>

新建分支是新建一个指针指向时间线的最后一个节点，并让 HEAD 指针指向新分支，表示新分支成为当前分支。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208203142527.png"/> </div><br>

每次提交只会让当前分支指针向前移动，而其它分支指针不会移动。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208203112400.png"/> </div><br>

合并分支也只需要改变指针即可。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208203010540.png"/> </div><br>



## 5. 冲突

当两个分支都对同一个文件的同一行进行了修改，在分支合并时就会产生冲突。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208203034705.png"/> </div><br>

Git 会使用 <<<<<<< ，======= ，>>>>>>> 标记出不同分支的内容，只需要把不同分支中冲突部分修改成一样就能解决冲突。

```
<<<<<<< HEAD
Creating a new branch is quick & simple.
=======
Creating a new branch is quick AND simple.
>>>>>>> feature1
```



## 6. Fast forward

"快进式合并"（fast-farward merge），会直接将 master 分支指向合并的分支，这种模式下进行分支合并会丢失分支信息，也就不能在分支历史上看出分支信息。

可以在合并时加上 --no-ff 参数来禁用 Fast forward 模式，并且加上 -m 参数让合并时产生一个新的 commit。

```
$ git merge --no-ff -m "merge with no-ff" dev
```

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/image-20191208203639712.png"/> </div><br>



## 7. 储藏（Stashing）

在一个分支上操作之后，如果还没有将修改提交到分支上，此时进行切换分支，那么另一个分支上也能看到新的修改。这是因为所有分支都共用一个工作区的缘故。

可以使用 git stash 将当前分支的修改储藏起来，此时当前工作区的所有修改都会被存到栈中，也就是说当前工作区是干净的，没有任何未提交的修改。此时就可以安全的切换到其它分支上了。

```
$ git stash
Saved working directory and index state \ "WIP on master: 049d078 added the index file"
HEAD is now at 049d078 added the index file (To restore them type "git stash apply")
```

该功能可以用于 bug 分支的实现。如果当前正在 dev 分支上进行开发，但是此时 master 上有个 bug 需要修复，但是 dev 分支上的开发还未完成，不想立即提交。在新建 bug 分支并切换到 bug 分支之前就需要使用 git stash 将 dev 分支的未提交修改储藏起来。



## 8. SSH 传输设置

Git 仓库和 Github 中心仓库之间的传输是通过 SSH 加密。

如果工作区下没有 .ssh 目录，或者该目录下没有 id_rsa 和 id_rsa.pub 这两个文件，可以通过以下命令来创建 SSH Key：

```
$ ssh-keygen -t rsa -C "youremail@example.com"
```

然后把公钥 id_rsa.pub 的内容复制到 Github "Account settings" 的 SSH Keys 中。



## 9. gitignore 文件

忽略以下文件：

- 操作系统自动生成的文件，比如缩略图；
- 编译生成的中间文件，比如 Java 编译产生的 .class 文件；
- 自己的敏感信息，比如存放口令的配置文件。

不需要全部自己编写，可以到 [https://github.com/github/gitignore](https://github.com/github/gitignore) 中进行查询。



## 10. Git 命令一览

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/7a29acce-f243-4914-9f00-f2988c528412.jpg" width=""> </div><br>

比较详细的地址：http://www.cheat-sheets.org/saved-copy/git-cheat-sheet.pdf



# [常用Git命令手册](https://juejin.im/post/5a4de5d8f265da432c2444b9)⭐️

此文只是对Git有一定基础的人当记忆使用，比较简略，初级学员强烈推荐廖雪峰老师的Git系列教程，通俗易懂，[戳此处即可开始学习](https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000)

### 1.安装Git

- Linux

```bash
sudo apt-get install git
```

- Window:到Git官网下载安装：https://git-scm.com/downloads

### 2.配置全局用户Name和E-mail

```bash
$ git config --global user.name "Your Name"
$ git config --global user.email "email@example.com"
```

### 3.初始化仓库

```bash
git init
```

### 4.添加文件到Git仓库

```bash
git add <file>
```

提示：可反复多次使用，添加多个文件；

### 5.提交添加的文件到Git仓库

```bash
git commit
```

然后会弹出一个Vim编辑器输入本次提交的内容；

或者

```bash
git commit -m "提交说明"
```

### 6.查看仓库当前的状态

```bash
git status
```

### 7.比较当前文件的修改

```bash
$ git diff <file>
```

### 8.查看历史提交记录⭐️

```bash
git log
```

或者加上参数查看就比较清晰了

```bash
$ git log --pretty=oneline
```

### 9.回退版本⭐️

```bash
$ git reset --hard HEAD^
```

说明：在Git中，用HEAD表示当前版本，上一个版本就是HEAD\^，上上一个版本就是HEAD\^\^，以此类推，如果需要回退几十个版本，写几十个^容易数不过来，所以可以写，例如回退30个版本为：HEAD~30。

如果你回退完版本又后悔了，想回来，一般情况下是回不来的，但是如果你可以找到你之前的commit id的话，也是可以的，使用如下即可：

```bash
$ git reset --hard + commit id 
```

提示：commit id不需要写全，Git会自动查找；

补充说明：Git中，commit id是一个使用SHA1计算出来的一个非常大的数字，用十六进制表示，你提交时看到的一大串类似3628164...882e1e0的就是commit id（版本号）；

在Git中，版本回退速度非常快，因为Git在内部有个指向当前版本的HEAD指针，当你回退版本的时候，Git仅仅是把HEAD从指向回退的版本，然后顺便刷新工作区文件；

### 10.查看操作的历史命令记录

```bash
$ git reflog
```

结果会将你之前的操作的commit id和具体的操作类型及相关的信息打印出来，这个命令还有一个作用就是，当你过了几天，你想回退之前的某次提交，但是你不知道commit id了，通过这个你可查找出commit id,就可以轻松回退了，用一句话总结：穿越未来，回到过去，so easy！

### 11.diff文件

```bash
git diff HEAD -- <file>
```

说明：查看工作区和版本库里面最新版本文件的区别，也可以不加HEAD参数；

### 12.丢弃工作区的修改⭐️

```bash
$ git checkout -- <file>
```

说明：适用于工作区修改没有add的文件

### 13.丢弃暂存区的文件⭐️

```bash
$ git reset HEAD <file>
```

说明：适用于暂存区已经add的文件，注意执行完此命令，他会将暂存区的修改放回到工作区中，如果要想工作区的修改也丢弃，就执行第12条命令即可；

### 14.删除文件

```bash
$ rm <file>
```

然后提交即可；

如果不小心删错了，如果还没有提交的话使用下面命令即可恢复删除，注意的是它只能恢复最近版本提交的修改，你工作区的修改是不能被恢复的！

```bash
$ git checkout -- <file>
```

### 15.创建SSH key

```bash
$ ssh-keygen -t rsa -C "youremail@example.com"
```

一般本地Git仓库和远程Git仓库之间的传输是通过SSH加密的，所以我们可以将其生成的公钥添加到Git服务端的设置中即可，这样Git就可以知道是你提交的了；

### 16.与远程仓库协作⭐️

```bash
$ git remote add origin git@github.com:xinpengfei520/IM.git
```

删除本地库与远程库的关联：

```bash
$ git remote rm origin
```

作用：有时候我们需要关联其他远程库，需要先删除旧的关联，再添加新的关联，因为如果你已经关联过了就不能在关联了，不过想关联多个远程库也是可以的，前提是你的本地库没有关联任何远程库，操作如下：

先关联Github远程库：

```bash
$ git remote add github git@github.com:xinpengfei520/IM.git
```

接着关联码云远程库：

```bash
$ git remote add gitee git@gitee.com:xinpengfei521/IM.git
```

现在，我们用`git remote -v`查看远程库的关联信息，如果看到两组关联信息就说明关联成功了；

ok,现在我们的本地库可以和多个远程库协作了

如果要推送到GitHub，使用命令：

```bash
$ git push github master
```

如果要推送到码云，使用命令：

```bash
$ git push gitee master
```

### 17.推送到远程仓库

```bash
$ git push -u origin master
```

注意：第一次提交需要加一个参数-u,以后不需要

### 18.克隆一个远程库

```bash
$ git clone git@github.com:xinpengfei520/IM.git
```

### 19.Git分支管理⭐️

创建一个分支branch1

```bash
$ git branch branch1
```

切换到branch1分支：

```bash
$ git checkout branch1
```

创建并切换到branch1分支：

```bash
$ git checkout -b branch1
```

查看分支：

```bash
$ git branch
```

提示：显示的结果中，其中有一个分支前有个*号，表示的是当前所在的分支；

合并branch1分支到master：

```bash
$ git merge branch1
```

删除分支：

```bash
$ git branch -d branch1
```

### 20.查看提交的历史记录

```bash
$ git log
```

命令可以看到分支合并图

```bash
git log --graph
```

### 21.合并分支

禁用Fast forward模式合并分支

```bash
$ git merge --no-ff -m "merge" branch1
```

说明：默认Git合并分支时使用的是Fast forward模式，这种模式合并，删除分支后，会丢掉分支信息，所以我们需要强制禁用此模式来合并；

补充内容：实际开发中分支管理的策略

- master分支应该是非常稳定的，也就是仅用来发布新版本，平时不能在上面提交；
- 我们可以新开一个dev分支，也就是说dev分支是不稳定的，到版本发布时，再把dev分支合并到master上，在master分支发布新版本；
- 你和你的协作者平时都在dev分支上提交，每个人都有自己的分支，时不时地往dev分支上合并就可以了；

### 22.保存工作现场⭐️

```bash
$ git stash
```

作用：当你需要去修改其他内容时，这时候你的工作还没有做完，先临时保存起来，等干完其他事之后，再回来回复现场，再继续干活；为什么？因为暂存区是公用的，如果不通过stash命令隐藏，会带到其它分支去；

查看已经保存的工作现场列表：

```bash
$ git stash list
```

恢复工作现场(恢复并从stash list删除)：

```bash
$ git stash pop
```

或者：

```bash
git stash apply
```

恢复工作现场，但stash内容并不删除，如果你需要删除执行如下命令：

```bash
$ git stash drop
```

恢复指定的stash:

```bash
$ git stash apply stash@{0}
```

说明：其中stash@{0}为`git stash list`中的一种编号

### 23.丢弃一个没有被合并过的分支

强行删除即可：

```bash
$ git branch -D <name>
```

作用：实际开发中，添加一个新feature，最好新建一个分支，如果要丢弃这个没有被合并过的分支，可以通过上面的命令强行删除；

### 24.查看远程库的信息

```bash
$ git remote
```

显示更详细的信息：

```bash
$ git remote -v
```

### 25.推送分支

推送master到远程库

```bash
$ git push origin master
```

推送branch1到远程库

```bash
$ git push origin branch1
```

### 26.创建本地分支

```bash
$ git checkout -b branch1 origin/branch1
```

说明：如果远程库中有分支，clone之后默认只有master分支的，所以需要执行如上命令来创建本地分支才能与远程的分支关联起来；

### 27.指定本地branch1分支与远程origin/branch1分支的链接

```bash
$ git branch --set-upstream branch1 origin/branch1
```

作用：如果你本地新建的branch1分支，远程库中也有一个branch1分支(别人创建的)，而刚好你也没有提交过到这个分支，即没有关联过，会报一个`no tracking information`信息，通过上面命令关联即可；

### 28.创建标签⭐️

```bash
$ git tag <name>
```

例如：`git tag v1.0`

查看所有标签：

```bash
$ git tag
```

对历史提交打tag

先使用`$ git log --pretty=oneline --abbrev-commit`命令找到历史提交的commit id

例如对commit id 为123456的提交打一个tag:

```bash
$ git tag v0.9 123456
```

查看标签信息：

```bash
$ git show <tagname>
```

eg:`git show v1.0`

创建带有说明的标签，用-a指定标签名，-m指定说明文字，123456为commit id：

```bash
$ git tag -a v1.0 -m "V1.0 released" 123456
```

用私钥签名一个标签：

```bash
$ git tag -s v2.0 -m "signed V2.0 released" 345678
```

说明：签名采用PGP签名，因此，必须先要安装gpg（GnuPG），如果没有找到gpg，或者没有gpg密钥对，就会报错，具体请参考GnuPG帮助文档配置Key；

作用：用PGP签名的标签是不可伪造的，因为可以验证PGP签名；

删除标签：

```bash
$ git tag -d <tagname>
```

删除远程库中的标签：

比如要删除远程库中的 **V1.0** 标签，分两步：

[1] 先删除本地标签：`$ git tag -d V1.0`

[2] 再推送删除即可：`$ git push origin :refs/tags/V1.0`

推送标签到远程库：

```bash
$ git push origin <tagname>
```

推送所有标签到远程库：

```bash
$ git push origin --tags
```

### 29.自定义Git设置

Git显示颜色，会让命令输出看起来更清晰、醒目：

```bash
$ git config --global color.ui true
```

设置命令别名：

```bash
$ git config --global alias.st status
```

说明：--global表示全局，即设置完之后全局生效，st表示别名，status表示原始名

好了，现在敲`git st`就相当于是`git status`命令了，是不是方便？

当然还有其他命令可以简写，这里举几个：很多人都用co表示checkout，ci表示commit，br表示branch...
根据自己的喜好可以设置即可，个人觉得不是很推荐使用别名的方式；

推荐一个比较丧心病狂的别名设置：

```bash
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

效果自己去体会...

其他说明：配置的时候加上--global是针对当前用户起作用的，如果不加只对当前的仓库起作用；每个仓库的Git配置文件都放在 **.git/config** 文件中，我们可以打开对其中的配置作修改，可以删除设置的别名；而当前用户的Git配置文件放在用户主目录下的一个隐藏文件.gitconfig中，我们也可以对其进行配置和修改。

### 30.忽略文件规则

原则：

- 忽略系统自动生成的文件等；
- 忽略编译生成的中间文件、可执行文件等，比如Java编译产生的.class文件，自动生成的文件就没必要提交；
- 忽略你自己的带有敏感信息的配置文件，个人相关配置文件；
- 忽略与自己相关开发环境相关的配置文件；
- ...

使用：在Git工作区的根目录下创建一个特殊的 **.gitignore** 文件，然后把要忽略的文件名或者相关规则填进去，Git就会自动忽略这些文件，不知道怎么写的可参考：[github.com/github/giti…](https://github.com/github/gitignore),这里提供了一些忽略的规则，可供参考；

如果你想添加一个被 **.gitignore** 忽略的文件到Git中，但发现是添加不了的，所以我们可以使用强制添加`$ git add -f `

或者我们可以检查及修改 **.gitignore** 文件的忽略规则：

```bash
$ git check-ignore -v <file>
```

Git会告诉我们具体的 **.gitignore** 文件中的第几行规则忽略了该文件，这样我们就知道应该修改哪个规则了；

如何忽略已经提交到远程库中的文件？
如果你已经将一些文件提交到远程库中了，然后你想忽略掉此文件，然后在 **.gitignore** 文件中添加忽略，然而你会发现并没有生效，因为Git添加忽略时只有对没有跟踪的文件才生效，也就是说你没有add过和提交过的文件才生效，按如下命令：

比如说：我们要忽略.idea目录，先删除已经提交到本地库的文件目录

```bash
git rm --cached .idea
```

格式：git rm --cached + 路径

如果提示：fatal: not removing '.idea' recursively without -r

加个参数 -r 即可强制删除

```bash
$ git rm -r --cached .idea
```

然后，执行`git status`会提示你已经删除.idea目录了，然后执行commit再push就可以了，此时的.idea目录是没有被跟踪的，将.idea目录添加到 **.gitignore** 文件中就可以忽略了。

附图：

![这里写图片描述](https://user-gold-cdn.xitu.io/2018/1/4/160c049ccf1e2bd9?imageslim)

### git命令大全

```bash
git init                                                  # 初始化本地git仓库（创建新仓库）
git config --global user.name "xxx"                       # 配置用户名
git config --global user.email "xxx@xxx.com"              # 配置邮件
git config --global color.ui true                         # git status等命令自动着色
git config --global color.status auto
git config --global color.diff auto
git config --global color.branch auto
git config --global color.interactive auto
git config --global --unset http.proxy                    # remove  proxy configuration on git
git clone git+ssh://git@192.168.53.168/VT.git             # clone远程仓库
git status                                                # 查看当前版本状态（是否修改）
git add xyz                                               # 添加xyz文件至index
git add .                                                 # 增加当前子目录下所有更改过的文件至index
git commit -m 'xxx'                                       # 提交
git commit --amend -m 'xxx'                               # 合并上一次提交（用于反复修改）
git commit -am 'xxx'                                      # 将add和commit合为一步
git rm xxx                                                # 删除index中的文件
git rm -r *                                               # 递归删除
git log                                                   # 显示提交日志
git log -1                                                # 显示1行日志 -n为n行
git log -5
git log --stat                                            # 显示提交日志及相关变动文件
git log -p -m
git show dfb02e6e4f2f7b573337763e5c0013802e392818         # 显示某个提交的详细内容
git show dfb02                                            # 可只用commitid的前几位
git show HEAD                                             # 显示HEAD提交日志
git show HEAD^                                            # 显示HEAD的父（上一个版本）的提交日志 ^^为上两个版本 ^5为上5个版本
git tag                                                   # 显示已存在的tag
git tag -a v2.0 -m 'xxx'                                  # 增加v2.0的tag
git show v2.0                                             # 显示v2.0的日志及详细内容
git log v2.0                                              # 显示v2.0的日志
git diff                                                  # 显示所有未添加至index的变更
git diff --cached                                         # 显示所有已添加index但还未commit的变更
git diff HEAD^                                            # 比较与上一个版本的差异
git diff HEAD -- ./lib                                    # 比较与HEAD版本lib目录的差异
git diff origin/master..master                            # 比较远程分支master上有本地分支master上没有的
git diff origin/master..master --stat                     # 只显示差异的文件，不显示具体内容
git remote add origin git+ssh://git@192.168.53.168/VT.git # 增加远程定义（用于push/pull/fetch）
git branch                                                # 显示本地分支
git branch --contains 50089                               # 显示包含提交50089的分支
git branch -a                                             # 显示所有分支
git branch -r                                             # 显示所有原创分支
git branch --merged                                       # 显示所有已合并到当前分支的分支
git branch --no-merged                                    # 显示所有未合并到当前分支的分支
git branch -m master master_copy                          # 本地分支改名
git checkout -b master_copy                               # 从当前分支创建新分支master_copy并检出
git checkout -b master master_copy                        # 上面的完整版
git checkout features/performance                         # 检出已存在的features/performance分支
git checkout --track hotfixes/BJVEP933                    # 检出远程分支hotfixes/BJVEP933并创建本地跟踪分支
git checkout v2.0                                         # 检出版本v2.0
git checkout -b devel origin/develop                      # 从远程分支develop创建新本地分支devel并检出
git checkout -- README                                    # 检出head版本的README文件（可用于修改错误回退）
git merge origin/master                                   # 合并远程master分支至当前分支
git cherry-pick ff44785404a8e                             # 合并提交ff44785404a8e的修改
git push origin master                                    # 将当前分支push到远程master分支
git push origin :hotfixes/BJVEP933                        # 删除远程仓库的hotfixes/BJVEP933分支
git push --tags                                           # 把所有tag推送到远程仓库
git fetch                                                 # 获取所有远程分支（不更新本地分支，另需merge）
git fetch --prune                                         # 获取所有原创分支并清除服务器上已删掉的分支
git pull origin master                                    # 获取远程分支master并merge到当前分支
git mv README README2                                     # 重命名文件README为README2
git reset --hard HEAD                                     # 将当前版本重置为HEAD（通常用于merge失败回退）
git rebase
git branch -d hotfixes/BJVEP933                           # 删除分支hotfixes/BJVEP933（本分支修改已合并到其他分支）
git branch -D hotfixes/BJVEP933                           # 强制删除分支hotfixes/BJVEP933
git ls-files                                              # 列出git index包含的文件
git show-branch                                           # 图示当前分支历史
git show-branch --all                                     # 图示所有分支历史
git whatchanged                                           # 显示提交历史对应的文件修改
git revert dfb02e6e4f2f7b573337763e5c0013802e392818       # 撤销提交dfb02e6e4f2f7b573337763e5c0013802e392818
git ls-tree HEAD                                          # 内部命令：显示某个git对象
git rev-parse v2.0                                        # 内部命令：显示某个ref对于的SHA1 HASH
git reflog                                                # 显示所有提交，包括孤立节点
git show HEAD@{5}
git show master@{yesterday}                               # 显示master分支昨天的状态
git log --pretty=format:'%h %s' --graph                   # 图示提交日志
git show HEAD~3
git show -s --pretty=raw 2be7fcb476
git stash                                                 # 暂存当前修改，将所有至为HEAD状态
git stash list                                            # 查看所有暂存
git stash show -p stash@{0}                               # 参考第一次暂存
git stash apply stash@{0}                                 # 应用第一次暂存
git grep "delete from"                                    # 文件中搜索文本“delete from”
git grep -e '#define' --and -e SORT_DIRENT
git gc
git fsck
```

