# archived_issues_collector

- 此项目用于收集各个**归档文件**并根据**指定的版本号范围**来**汇总归档内容并重新格式化输出**为ChangeLog形式的内容
- 本项目的预期设计触发条件是通过github action流水线手动触发来运行,详见 [ChangeLog输出流水线使用指南](./ChangeLog输出流水线使用指南.md)
- 运行项目需要python解释器版本 >= `3.10` , 以及安装项目依赖的第三方库,例如使用这个命令 `pip install ./develop-requirements.txt`
- 本项目还支持通过命令行参数传入版本号范围以及配置文件路径来本地运行,详见[本地运行项目](#本地运行项目)

## 目前的归档文件源的配置
- 目前的归档文件来源有 :
  - 来自`RN_All_Issues`仓库的 [修改归档.md](https://github.com/Zero-Fanker/RN_All_Issues/blob/master/%E4%BF%AE%E6%94%B9%E5%BD%92%E6%A1%A3.md)
  - 来自`rn_internal_issues`镜像的BitBucket镜像仓库的 `修改归档.md`
  - 来自`rn_internal_issues`镜像的BitBucket镜像仓库的 `修改归档_old.md`

## 本地运行项目

- 直接运行`main.py`或者使用`-h` `--help`查看命令参数帮助信息
```bash
python ./archived_issues_collector/src/main.py 
```

## 项目结构

- `src/` 业务代码目录
- `tests/` 单元测试代码目录
- `config/` 配置文件目录
- `dev-requirements.txt/` 项目所需第三方库的定义,开发前使用
- `requirements.txt/` 项目所需第三方库的定义,流水线运行前使用
