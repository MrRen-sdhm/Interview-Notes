# CMake常用命令

## 基本语法

`COMMAND(args...)`，多个参数用空白符分隔

## 常用命令

## 1. cmake_minimum_required (VERSION 3.4.1)

指定需要的最小的cmake版本

## 2. aux_source_directory

查找源文件并保存到相应的变量中:

```bash
#查找当前目录下所有源文件并保存至SRC_LIST变量中
aux_source_directory(. SRC_LIST)
```

## 3. add_library

### 3.1 添加一个库

```css
add_library(<name> [STATIC | SHARED | MODULE] [EXCLUDE_FROM_ALL] source1 source2 ... sourceN)
```

- 添加一个名为``的库文件
- 指定`STATIC, SHARED, MODULE`参数来指定要创建的库的类型, `STATIC`对应的静态库(.a)，`SHARED`对应共享动态库(.so)
- `[EXCLUDE_FROM_ALL]`, 如果指定了这一属性，对应的一些属性会在目标被创建时被设置(**指明此目录和子目录中所有的目标，是否应当从默认构建中排除, 子目录的IDE工程文件/Makefile将从顶级IDE工程文件/Makefile中排除**)
- `source1 source2 ... sourceN`用来指定源文件

### 3.2 导入已有的库

```css
add_library(<name> [STATIC | SHARED | MODULE | UNKNOWN] IMPORTED)
```

导入了一个已存在的``库文件，导入库一般配合`set_target_properties`使用，这个命令用来指定导入库的路径,比如：

```bash
add_library(test SHARED IMPORTED)
set_target_properties(  test #指定目标库名称
                        PROPERTIES IMPORTED_LOCATION #指明要设置的参数
                        libs/src/${ANDROID_ABI}/libtest.so #设定导入库的路径)
```

## 4. set

设置CMake变量

**例子：**

```bash
# 设置可执行文件的输出路径(EXCUTABLE_OUTPUT_PATH是全局变量)
set(EXECUTABLE_OUTPUT_PATH [output_path])
```

```bash
# 设置库文件的输出路径(LIBRARY_OUTPUT_PATH是全局变量)
set(LIBRARY_OUTPUT_PATH [output_path])
```

```bash
# 设置C++编译参数(CMAKE_CXX_FLAGS是全局变量)
set(CMAKE_CXX_FLAGS "-Wall std=c++11")
```

```bash
# 设置源文件集合(SOURCE_FILES是本地变量即自定义变量)
set(SOURCE_FILES main.cpp test.cpp ...)
```

## 5. include_directories

设置头文件位置

```ruby
# 可以用相对货绝对路径，也可以用自定义的变量值
include_directories(./include ${MY_INCLUDE})
```

## 6. add_executable

添加可执行文件

```bash
add_executable(<name> ${SRC_LIST})
```

## 7. target_link_libraries

将若干库链接到目标库文件

```jsx
target_link_libraries(<name> lib1 lib2 lib3)
```

将`lib1, lib2, lib3`链接到``上

> NOTE: 链接的顺序应当符合gcc链接顺序规则，被链接的库放在依赖它的库的后面，即如果上面的命令中，lib1依赖于lib2, lib2又依赖于lib3，则在上面命令中必须严格按照`lib1 lib2 lib3`的顺序排列，否则会报错
>  也可以自定义链接选项, 比如针对lib1使用`-WL`选项,`target_link_libraries( lib1 -WL, lib2 lib3)`

## 8. add_definitions

为当前路径以及子目录的源文件加入由`-D`引入得`define flag`

```undefined
add_definitions(-DFOO -DDEBUG ...)
```

## 9. add_subdirectory

如果当前目录下还有子目录时可以使用`add_subdirectory`，子目录中也需要包含有`CMakeLists.txt`

```bash
# sub_dir指定包含CMakeLists.txt和源码文件的子目录位置
# binary_dir是输出路径， 一般可以不指定
add_subdirecroty(sub_dir [binary_dir])
```

## 10. file

文件操作命令

```bash
# 将message写入filename文件中,会覆盖文件原有内容
file(WRITE filename "message")
```

```bash
# 将message写入filename文件中，会追加在文件末尾
file(APPEND filename "message")
```

```csharp
# 从filename文件中读取内容并存储到var变量中，如果指定了numBytes和offset，
# 则从offset处开始最多读numBytes个字节，另外如果指定了HEX参数，则内容会以十六进制形式存储在var变量中
file(READ filename var [LIMIT numBytes] [OFFSET offset] [HEX])
```

```xml
# 重命名文件
file(RENAME <oldname> <newname>)
```

```bash
# 删除文件， 等于rm命令
file(REMOVE [file1 ...])
```

```bash
# 递归的执行删除文件命令, 等于rm -r
file(REMOVE_RECURSE [file1 ...])
```

```css
# 根据指定的url下载文件
# timeout超时时间; 下载的状态会保存到status中; 下载日志会被保存到log; sum指定所下载文件预期的MD5值,如果指定会自动进行比对，如果不一致，则返回一个错误; SHOW_PROGRESS，进度信息会以状态信息的形式被打印出来
file(DOWNLOAD url file [TIMEOUT timeout] [STATUS status] [LOG log] [EXPECTED_MD5 sum] [SHOW_PROGRESS])
```

```bash
# 创建目录
file(MAKE_DIRECTORY [dir1 dir2 ...])
```

```bash
# 会把path转换为以unix的/开头的cmake风格路径,保存在result中
file(TO_CMAKE_PATH path result)
```

```objectivec
# 它会把cmake风格的路径转换为本地路径风格：windows下用"\"，而unix下用"/"
file(TO_NATIVE_PATH path result)
```

```css
# 将会为所有匹配查询表达式的文件生成一个文件list，并将该list存储进变量variable里, 如果一个表达式指定了RELATIVE, 返回的结果将会是相对于给定路径的相对路径, 查询表达式例子: *.cxx, *.vt?
NOTE: 按照官方文档的说法，不建议使用file的GLOB指令来收集工程的源文件
file(GLOB variable [RELATIVE path] [globbing expressions]...)
```

## 11. set_directory_properties

设置某个路径的一种属性

```undefined
set_directory_properties(PROPERTIES prop1 value1 prop2 value2)
```

`prop1 prop`代表属性，取值为：

- INCLUDE_DIRECTORIES
- LINK_DIRECTORIES
- INCLUDE_REGULAR_EXPRESSION
- ADDITIONAL_MAKE_CLEAN_FILES

## 12. set_property

在给定的作用域内设置一个命名的属性

```csharp
set_property(<GLOBAL | 
            DIRECTORY [dir] | 
            TARGET [target ...] | 
            SOURCE [src1 ...] | 
            TEST [test1 ...] | 
            CACHE [entry1 ...]>
             [APPEND] 
             PROPERTY <name> [value ...])
```

第一个参数决定了属性可以影响的作用域,必须为以下值：

- GLOBAL 全局作作用域,不接受名字
- DIRECTORY 默认为当前路径，但是同样也可以用[dir]指定路径
- TARGET 目标作用，可以是0个或多个已有的目标
- SOURCE 源作用域， 可以是0个过多个源文件
- TEST 测试作用域, 可以是0个或多个已有的测试
- CACHE 必须指定0个或多个cache中已有的条目

`PROPERTY`参数是必须的