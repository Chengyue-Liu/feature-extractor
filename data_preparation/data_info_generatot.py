#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import multiprocessing
import os
from multiprocessing.dummy import Pool

from loguru import logger
from tqdm import tqdm

from feature_extraction.constants import TARGET_FILE_EXTENSION_SET
from feature_extraction.entities import Repository
from settings import DECOMPRESSED_DEBIAN_FILE_DIR_PATH, SRC_REPOS_JSON, BIN_REPOS_JSON
from utils.elf_utils import is_elf_file
from utils.json_util import dump_to_json


# @Time : 2023/12/6 18:25
# @Author : Liu Chengyue

def is_filter_repo(repo_name):
    """
    虽然在解压之前已经过滤过一次了，但是还是有很多漏网之鱼，这里补充过滤一下。

    :param repo_name:
    :return:
    """
    if repo_name.endswith(("-perl", "-java")):
        return True

    if repo_name.startswith(("python-", "php-", "golang-")):
        return True

    return False

# 一些不像是ELF的后缀名，先过滤掉，不然文件太多，判断一遍非常耗时。
NOT_ELF_EXTENSION_SET = {'.gz', '.txt', '.Debian', '.cnf', '.h', '.png', '.html', '.hpp', '.py', '.hxx', '.xml',
                         '.json',
                         '.js', '.yml', '.cert', '.cmake', '.c', '.php', '.svg', '.lua', '.jpg', '.conf', '.gif', '.go',
                         '.cpp', '.dat',
                         '.sh', '.md', '.hh', '.stderr', '.TXT', '.css', '.xhtml', '.cert',
                         '.vf', '.lisp', '.p_hi', '.dyn_hi', '.hi', '.zo', '.dep', '.desktop', '.result', '.docbook',
                         '.pm', '.qm', '.test', '.map', '.inc', '.out', '.m', '.a', '.rs', '.tfm', '.page',
                         '.bz2',  # 压缩文件
                         '.bc',  # LLVM Bitcode 文件
                         '.vbp',  # Visual Basic 项目文件
                         '.module',  # 模块文件
                         '.tex',  # LaTeX 文档
                         '.rst',  # reStructuredText 文档
                         '.ui',  # 用户界面文件
                         '.service',  # 系统服务文件
                         '.debug',  # 调试信息文件
                         '.pd',  # Pure Data 文件
                         '.rds',  # R 数据文件
                         '.tst',  # 测试文件
                         '.md5',  # MD5 校验文件
                         '.table',  # 表格文件
                         '.pas',  # Pascal 源代码文件
                         '.pl',  # Perl 源代码文件
                         '.rkt',  # Racket 源代码文件
                         '.scm',  # Scheme 源代码文件
                         '.ogg',  # Ogg Vorbis 音频文件
                         '.cfg',  # 配置文件
                         '.pc',  # Program Configuration 文件
                         '.rb',  # Ruby 源代码文件
                         '.mod',  # Fortran 模块文件
                         '.R',  # R 语言脚本文件
                         '.po',  # Gettext Portable Object 文件
                         '.ly',  # LilyPond 源代码文件
                         '.ppu',  # Free Pascal 编译单元文件
                         '.xpm',  # X Pixmap 图像文件
                         '.elmt',  # Element 文件
                         '.qml',  # Qt QML 文件
                         '.cl',  # OpenCL 源代码文件
                         '.xiz',  # Xilinx文件
                         '.la',  # Libtool库文件
                         '.fig',  # Xfig 图形文件
                         '.svgz',  # 压缩的SVG图形文件
                         '.pro',  # Qt项目文件
                         '.java',  # Java 源代码文件
                         '.prg',  # Program 文件
                         '.pdf',  # Adobe PDF 文件
                         '.sty',  # LaTeX 样式文件
                         '.idl',  # Interface Definition Language 文件
                         '.milk',  # MilkDrop 音频可视化文件
                         '.pfb',  # Type 1 字体二进制文件
                         '.cc',  # C++ 源代码文件
                         '.hlp',  # 帮助文件
                         '.beam',  # Erlang Beam 文件
                         '.sym',  # 符号表文件
                         '.wav',  # WAV 音频文件
                         '.asm',  # 汇编语言源代码文件
                         '.sip',  # PyQt 绑定文件
                         '.sci',  # Scilab 源代码文件
                         '.vim',  # Vim 脚本文件
                         '.ini',  # 配置文件
                         '.def',  # 定义文件
                         '.i',  # C/C++ 预处理器输出文件
                         '.pp',  # Pascal 源代码文件
                         '.ref',  # 引用文件
                         '.doc',  # 文档文件
                         '.mf',  # Metafont 源代码文件
                         '.elc',  # Emacs Lisp 编译文件
                         '.in',  # Autoconf 输入文件
                         '.sql',  # SQL 脚本文件
                         '.tcl',  # Tcl 脚本文件
                         '.hx',  # Haxe 编程语言源代码文件
                         '.H',  # C++ 头文件
                         '.tikz',  # TikZ 图形描述文件
                         '.xsd',  # XML Schema 文件
                         '.sch',  # 电路图文件
                         '.eps',  # Encapsulated PostScript 图形文件
                         '.fp',  # Fortran 程序文件
                         '.htm',  # HTML 文件
                         '.dic',  # 字典文件
                         '.csv',  # 逗号分隔值文件
                         '.rules',  # 规则文件
                         '.stp',  # STEP 文件
                         '.dot',  # Graphviz DOT 文件
                         '.vo',  # Coq 语言文件
                         '.pxd',  # Cython 头文件
                         '.sol',  # Solidity 源代码文件
                         '.spm',  # Simple Presentation Module 文件
                         '.rdx',  # 路由器配置文件
                         '.profile',  # 用户配置文件
                         '.hs',  # Haskell 源代码文件
                         '.erl',  # Erlang 源代码文件
                         '.rdb',  # Redis 数据库文件
                         '.ps',  # PostScript 文件
                         '.ipp',  # C++ 内联文件
                         '.toml',  # TOML 配置文件
                         '.m2',  # Maven 项目文件
                         '.ali',  # Ada 编译单元文件
                         '.fish',  # Fish shell 脚本文件
                         '.adb',  # Ada 源代码文件
                         '.pd_linux',  # Pure Data Linux 执行文件
                         '.f',  # Fortran 源代码文件
                         '.odg',  # OpenDocument 图形文件
                         '.htf',  # HyperTeX 字体文件
                         '.d',  # D 语言源代码文件
                         '.ads',  # Ada 规范文件
                         '.mm',  # Objective-C++ 源代码文件
                         '.enc',  # 编码文件
                         '.xbm',  # X Bitmap 图像文件
                         '.fd',  # TeX 字体定义文件
                         '.hlq',  # HLQ 数据库文件
                         '.qci',  # QuickTime 配置文件
                         '.el',  # Emacs Lisp 源代码文件
                         '.scrbl',  # Racket 文档文件
                         '.ml',  # OCaml 源代码文件
                         '.afm',  # Adobe 字体度量文件
                         '.patch',  # 补丁文件
                         '.td',  # TeX 文档文件
                         '.m4',  # M4 宏处理文件
                         '.lang',  # 语言文件
                         '.tiff',  # TIFF 图像文件
                         '.par',  # 参数文件
                         '.jar',  # Java 归档文件
                         '.inl',  # C++ 内联文件
                         '.phtml',  # PHP HTML 文件
                         '.pyi',  # Python 接口文件
                         '.v',  # Verilog 源代码文件
                         '.bmp',  # BMP 图像文件
                         '.ttl',  # Turtle RDF 三元组文件
                         '.opt',  # 编译器选项文件
                         '.yaml',  # YAML 配置文件
                         '.lfm',  # Lazarus 表单文件
                         '.ts',  # TypeScript 源代码文件
                         '.texi',  # Texinfo 文档文件
                         '.pb',  # Protocol Buffer 文件
                         '.lxx',  # Lexx 源代码文件
                         '.ltx',  # LaTeX 源代码文件
                         '.cfdg',  # Context Free Art 源代码文件
                         '.hrl',  # Erlang 头文件
                         '.deps',  # 依赖文件
                         '.cc-tst',  # C++ 测试文件
                         '.ldf',  # LISP 数据文件
                         '.csi',  # LISP 交互式解释器脚本
                         '.policy',  # 安全策略文件
                         '.stl',  # 3D 制图文件
                         '.sam',  # Sequence Alignment/Map 文件
                         '.rle',  # Run-Length Encoded 图像文件
                         '.entities',  # 实体文件
                         '.res',  # 资源文件
                         '.lyx',  # LyX 文档文件
                         '.pod',  # Perl POD 文档
                         '.tr',  # Troff 文本文件
                         '.zcos',  # Zea COS 文件
                         '.net',  # 仿真网络文件
                         '.control',  # 控制文件
                         '.fixed',  # 固定格式文件
                         '.xpi',  # Mozilla 扩展文件
                         '.rsp',  # 响应文件
                         '.class',  # Java 类文件
                         '.cif',  # Crystallographic Information 文件
                         '.template',  # 模板文件
                         '.mia',  # MATLAB 编译后文件
                         '.r',  # R 语言脚本文件
                         '.example',  # 示例文件
                         '.mkii',  # ConTeXt Mark II 文件
                         '.lst',  # 列表文件
                         '.pfm',  # Windows 字体度量文件
                         '.ldif',  # LDAP 数据交换格式文件
                         '.lpi',  # Lazarus 项目信息文件
                         '.awk',  # AWK 脚本文件
                         '.sce',  # Scilab 源代码文件
                         '.proc',  # VMS 过程文件
                         '.pbm',  # Portable Bitmap 图像文件
                         '.bci',  # IBM 3270 终端配置文件
                         '.qmlc',  # Qt QML 编译后文件
                         '.hd',  # SAS 数据文件
                         '.grc',  # GNU Radio Companion 文件
                         '.mkiv',  # ConTeXt Mark IV 文件
                         '.cmap',  # PDF 字符映射文件
                         '.load',  # Emacs Lisp 文件
                         '.mem',  # 其他内存文件
                         '.fasta',  # FASTA 序列文件
                         '.sl',  # SWIG 源代码文件
                         '.bm',  # Windows 打印位图文件
                         '.rcp',  # ReCap 项目文件
                         '.config',  # 配置文件
                         '.oct',  # Octave 脚本文件
                         '.fail',  # 测试失败文件
                         '.ckt',  # 电路文件
                         '.meta',  # 元文件
                         '.cmt',  # OCaml 标记文件
                         '.mlw',  # SML/NJ 特定的编译文件
                         '.lpk',  # Lazarus 包文件
                         '.spr',  # SpreadSheet 文件
                         '.sprite',  # Scratch Sprite 文件
                         '.dsp',  # Visual Studio 音频项目文件
                         '.cmti',  # OCaml 接口标记文件
                         '.mount',  # 文件系统挂载文件
                         '.theme',  # GTK 主题文件
                         '.inx',  # Adobe InCopy 文档文件
                         '.vapi',  # Vala 接口文件
                         '.jmod',  # Java 模块文件
                         '.scad',  # OpenSCAD 脚本文件
                         '.tt2',  # Template Toolkit 文件
                         '.csd',  # Csound 文件
                         '.frag',  # GLSL 片段着色器文件
                         '.pbl',  # PowerBuilder 库文件
                         '.S',  # 汇编语言源代码文件
                         '.ctb',  # AutoCAD 转换表文件
                         '.aug',  # Augeas 自动化文件编辑工具文件
                         '.colors',  # 颜色方案文件
                         '.mli',  # OCaml 接口文件
                         '.prl',  # Perl 库文件
                         '.gbs',  # Gerber 文件
                         '.rda',  # R 数据存档文件
                         '.make',  # GNU Makefile 文件
                         '.gi',  # GObject 接口文件
                         '.pov',  # POV-Ray 脚本文件
                         '.gxx',  # C++ 源代码文件
                         '.gorm',  # Gorm Interface 文件
                         '.classes',  # Java 类文件
                         '.pike',  # Pike 源代码文件
                         '.diff',  # 差异文件
                         '.mdc',  # MedCalc 文件
                         '.network',  # Wireshark 捕获文件
                         '.swg',  # SWIG 源代码文件
                         '.less',  # LESS 样式表文件
                         '.decTest',  # DEC测试文件
                         '.plugin',  # 插件文件
                         '.list',  # 列表文件
                         '.tga',  # TGA 图像文件
                         '.shape',  # Blender 形状文件
                         '.txx',  # C++ 模板文件
                         '.Rmd',  # R Markdown 文件
                         '.cmxs',  # OCaml 动态库文件
                         '.cs',  # C# 源代码文件
                         '.index',  # 索引文件
                         '.pem',  # PEM 证书文件
                         '.otf',  # OpenType 字体文件
                         '.lock',  # 锁文件
                         '.zip',  # ZIP 压缩文件
                         '.vos',  # OpenVOS 文件
                         '.proto',  # Protocol Buffers 文件
                         '.mk',  # Makefile 文件
                         '.ds',  # Datasheet 文件
                         '.db',  # 数据库文件
                         '.gnucash-xea',  # GnuCash 导出文件
                         '.step',  # STEP 3D 模型文件
                         '.mps',  # Mathematical Programming System 文件
                         '.al',  # ActionScript 文件
                         '.target',  # 编译目标
                         }


def is_filter_file(elf_path):
    """
    过滤掉不是elf的文件，加速elf筛选

     [('.h', 1953766), ('', 1427686), ('.png', 1278914), ('.html', 1105294), ('.mo', 585211), ('.hpp', 511953),
     ('.py', 504704), ('.ko', 386544), ('.so', 300430), ('.svg', 272701), ('.hxx', 177003), ('.xml', 161375),
     ('.page', 152596), ('.o', 136618), ('.tfm', 115544), ('.json', 112022), ('.js', 107594), ('.rs', 85749),
      ('.a', 75816), ('.m', 74802)]
    :param elf_path:
    :return:
    """
    dir_name, elf_name = os.path.split(elf_path)
    pure_name, extension = os.path.splitext(elf_name)
    if extension in NOT_ELF_EXTENSION_SET:
        return True

    return False


def get_useful_version_dir_paths():
    repo_id = 0
    version_id = 0
    results = []
    for category_name in os.listdir(DECOMPRESSED_DEBIAN_FILE_DIR_PATH):
        category_path = os.path.join(DECOMPRESSED_DEBIAN_FILE_DIR_PATH, category_name)
        if not os.path.isdir(category_path):
            continue
        for repo_name in os.listdir(category_path):
            # 过滤其他语言
            if is_filter_repo(repo_name):
                continue
            # 不存在的过滤
            library_path = os.path.join(category_path, repo_name)
            if not os.path.isdir(library_path):
                continue
            repo_id += 1
            for version_number in os.listdir(library_path):
                # 不存在的过滤
                version_path = os.path.join(library_path, version_number)
                if not os.path.isdir(version_path):
                    continue
                version_id += 1
                if version_id % 1000 == 0:
                    logger.info(f"get_version_dir_paths progres: {version_id}")
                # 没有源码过滤
                src_path = os.path.join(version_path, "source")
                if not os.path.isdir(src_path):
                    continue
                # 没有二进制过滤
                binary_path = os.path.join(version_path, "binary")
                if not os.path.isdir(binary_path):
                    continue
                results.append((repo_id, repo_name, version_id, version_number, version_path))
    return results


def find_c_and_cpp_files(args):
    """
    找出所有的c/cpp文件
    :param args:
    :return:
    """
    repo_id, repo_name, version_id, version_number, version_path = args

    src_path = os.path.join(version_path, "source")
    target_file_paths = []
    if os.path.isdir(src_path):
        target_file_paths = [os.path.join(root, f) for root, dirs, files in os.walk(src_path)
                             for f in files
                             if f.endswith(tuple(TARGET_FILE_EXTENSION_SET))]

    return repo_id, repo_name, version_id, version_number, version_path, target_file_paths


def update_repo_elf_files(repo: Repository):
    """
    筛选elf
    :param repo:
    :return:
    """
    repo.elf_paths = [path for path in repo.elf_paths if is_elf_file(path)]
    return repo


def generate_repositories_json():
    # step 1: 找到版本文件夹
    logger.info(f"step 0: get_version_dir_paths")
    results = get_useful_version_dir_paths()

    # step 1: 多进程筛选源码c/cpp文件
    pool_size = multiprocessing.cpu_count()
    with Pool(pool_size) as pool:
        # 使用 pool.map 异步处理每个 repository
        results = list(tqdm(pool.imap_unordered(find_c_and_cpp_files, results), total=len(results),
                            desc="step 1: find c files"))

    # step 2: 初始化 src_repo, bin_repo
    src_repos = []
    bin_repos = []
    release_id = 0
    arch_id = 0
    for repo_id, repo_name, version_id, version_number, version_path, target_file_paths in tqdm(results,
                                                                                                total=len(results),
                                                                                                desc="step 2: generate_repositories_json"):
        # 没有c/cpp 源码，过滤掉
        if len(target_file_paths) == 0:
            continue

        # source
        src_path = os.path.join(version_path, "source")
        src_repo = Repository(
            repo_path=src_path,
            repo_type="source",
            repo_id=repo_id,
            repo_name=repo_name,
            version_id=version_id,
            repo_version=version_number,
            target_src_file_num=len(target_file_paths)
        )
        src_repos.append(src_repo)

        # binary
        binary_path = os.path.join(version_path, "binary")
        for package_name in os.listdir(binary_path):
            package_path = os.path.join(binary_path, package_name)
            if not os.path.isdir(package_path):
                continue
            for release_number in os.listdir(package_path):
                release_path = os.path.join(package_path, release_number)
                if not os.path.isdir(release_path):
                    continue
                release_id += 1
                for arch_name in os.listdir(release_path):
                    arch_path = os.path.join(release_path, arch_name)
                    if not os.path.isdir(arch_path):
                        continue
                    arch_id += 1
                    elf_paths = []
                    for root, dirs, files in os.walk(arch_path):
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            if is_filter_file(file_path):
                                continue
                            # 此处只是筛选掉了明显不是的elf，添加进去的这些，也不代表都是ELF, 还需要后面进一步的确认。
                            elf_paths.append(file_path)
                    bin_repo = Repository(
                        repo_path=arch_path,
                        repo_type="binary",
                        repo_id=repo_id,
                        repo_name=repo_name,
                        version_id=version_id,
                        repo_version=version_number,
                        package_name=package_name,
                        release_id=release_id,
                        repo_release=release_number,
                        arch_id=arch_id,
                        repo_arch=arch_name,
                        elf_paths=elf_paths
                    )
                    bin_repos.append(bin_repo)

    # step 3: 多进程筛选bin repo 的 elf文件
    pool_size = multiprocessing.cpu_count()
    with Pool(pool_size) as pool:
        # 使用 pool.map 异步处理每个 repository
        bin_repos = list(tqdm(pool.imap_unordered(update_repo_elf_files, bin_repos),
                              total=len(bin_repos),
                              desc="step 3: filter elf files"))

    # step x: extension_dict
    logger.info(f"extension_dict")
    extension_dict = dict()
    for repo in tqdm(bin_repos, total=len(bin_repos), desc="create extension_dict"):
        for path in repo.elf_paths:
            dir_name, file_name = os.path.split(path)
            pure_name, extension = os.path.splitext(file_name)
            if extension not in extension_dict:
                extension_dict[extension] = 1
            else:
                extension_dict[extension] += 1
    with open('extension_dict.json', 'w') as f:
        json.dump(extension_dict, f, ensure_ascii=False, indent=4)

    # step 4: 过滤掉没有elf文件的二进制库
    logger.info(f"step 4: filter bin_repos")
    bin_repos = [repo for repo in bin_repos if repo.elf_paths]

    # step 5: 保存结果
    logger.info(f"saving json ...")
    dump_to_json([repo.custom_serialize() for repo in src_repos], SRC_REPOS_JSON)
    dump_to_json([repo.custom_serialize() for repo in bin_repos], BIN_REPOS_JSON)
    logger.info(f"src_repos: {len(src_repos)}, bin_repos: {len(bin_repos)}")
    logger.info(f"all finished.")
    return src_repos, bin_repos
