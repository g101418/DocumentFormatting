import re
import json

# --- 1. CONFIG (保持不变) ---
CONFIG_JSON_STRING = """
{
  "tag_definitions": [
    {"tag_key": "DOC_YEAR", "display_name": "年份", "start_tag": "【年份】", "end_tag": "【-年份】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "DOC_GENRE", "display_name": "文种", "start_tag": "【文种】", "end_tag": "【-文种】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "DOC_ID", "display_name": "文号", "start_tag": "【文号】", "end_tag": "【-文号】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},

    {"tag_key": "H0", "display_name": "大标题", "start_tag": "【大标题】", "end_tag": "【-大标题】", "allow_unclosed": false, "allow_nested": false, "allow_multiline": true},
    
    {"tag_key": "H1", "display_name": "一级标题", "start_tag": "【一级标题】", "end_tag": "【-一级标题】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "H2", "display_name": "二级标题", "start_tag": "【二级标题】", "end_tag": "【-二级标题】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "H3", "display_name": "三级标题", "start_tag": "【三级标题】", "end_tag": "【-三级标题】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "H4", "display_name": "四级标题", "start_tag": "【四级标题】", "end_tag": "【-四级标题】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    
    {"tag_key": "P_H1", "display_name": "一级标题开头段", "start_tag": "【一级标题开头段】", "end_tag": null, "allow_unclosed": true, "allow_nested": true, "allow_multiline": true},
    {"tag_key": "P_H2", "display_name": "二级标题开头段", "start_tag": "【二级标题开头段】", "end_tag": null, "allow_unclosed": true, "allow_nested": true, "allow_multiline": true},
    {"tag_key": "PARAGRAPH", "display_name": "正文", "start_tag": "【正文】", "end_tag": null, "allow_unclosed": true, "allow_nested": true, "allow_multiline": true},

    {"tag_key": "BOLD", "display_name": "加粗", "start_tag": "【加粗】", "end_tag": "【-加粗】", "allow_unclosed": false, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "ITALIC_KAI", "display_name": "楷体强调", "start_tag": "【楷体强调】", "end_tag": "【-楷体强调】", "allow_unclosed": false, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "SIGNATURE", "display_name": "落款", "start_tag": "【落款】", "end_tag": "【-落款】", "allow_unclosed": false, "allow_nested": false, "allow_multiline": true},
    {"tag_key": "SIGNATURE_DATE", "display_name": "落款日期", "start_tag": "【落款日期】", "end_tag": "【-落款日期】", "allow_unclosed": true, "allow_nested": false, "allow_multiline": false},
    {"tag_key": "INCLUDE", "display_name": "引入文件", "start_tag": "【引入文件】", "end_tag": "【-引入文件】", "allow_unclosed": false, "allow_nested": false, "allow_multiline": false}
  ]
}
"""
CONFIG_DATA = json.loads(CONFIG_JSON_STRING)

class ParserError(Exception):
    pass

def preprocess_text(raw_text: str) -> list[str]:
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace('\u3000', ' ').replace('\xa0', ' ')
    lines = text.split('\n')
    # 保留空行，但后续处理会忽略纯空行，这里只是为了行号对齐
    processed_lines = [line.strip() for line in lines if line.strip()]
    return processed_lines

def process_document(lines: list[str], config: dict):
    # --- 初始化映射 ---
    tag_map = {}
    end_tag_map = {}
    for tag_def in config['tag_definitions']:
        tag_map[tag_def['start_tag']] = tag_def
        if tag_def['end_tag']:
            end_tag_map[tag_def['end_tag']] = tag_def

    # --- 核心数据结构 ---
    result_root = []  # 最终返回的列表
    container_stack = [result_root] # 容器栈：始终指向当前应该写入内容的列表 (children list)
    tag_stack = [] # 标签栈：记录当前打开的标签元数据 (tag_key, tag_def, start_line)
    
    # 辅助正则
    sorted_tags = sorted(list(tag_map.keys()) + list(end_tag_map.keys()), key=len, reverse=True)
    tag_regex = re.compile(f'({"|".join(re.escape(t) for t in sorted_tags)})')

    # --- 内部辅助函数：安全追加文本 ---
    def append_text(text_content):
        current_list = container_stack[-1]
        # 优化：如果当前列表最后一个元素已经是字符串，则合并
        if current_list and isinstance(current_list[-1], str):
            current_list[-1] += text_content
        else:
            current_list.append(text_content)

    for i, line in enumerate(lines):
        line_num = i + 1
        
        # --- 处理多行标签的换行符 ---
        if tag_stack:
            top_key, top_def, _ = tag_stack[-1]
            if top_def['allow_multiline'] and not top_def['allow_unclosed']:
                if line_num > tag_stack[-1][2]: 
                    append_text("\n") # 将换行符写入数据结构

        parts = tag_regex.split(line)
        
        for part in parts:
            if not part:
                continue

            # --- 情况 A: 起始标签 ---
            if part in tag_map:
                new_tag_def = tag_map[part]
                
                # 1. 隐式闭合检查 (Implicit Closing)
                if tag_stack:
                    top_key, top_def, top_start_line = tag_stack[-1]
                    if top_def['allow_unclosed'] and new_tag_def['allow_unclosed']:
                         tag_stack.pop()
                         container_stack.pop()

                # 2. 嵌套检查
                if tag_stack:
                    top_key, top_def, top_start_line = tag_stack[-1]
                    if not top_def['allow_nested']:
                         raise ParserError(f"行{line_num}: 嵌套违规！标签 '{top_def['display_name']}' (行{top_start_line}) 不允许内部包含 '{new_tag_def['display_name']}'。")

                # 3. 创建新节点并压栈
                new_node = {
                    "type": new_tag_def['tag_key'],
                    "children": []
                }
                container_stack[-1].append(new_node)
                tag_stack.append((new_tag_def['tag_key'], new_tag_def, line_num))
                container_stack.append(new_node["children"])

            # --- 情况 B: 结束标签 ---
            elif part in end_tag_map:
                closing_tag_def = end_tag_map[part]
                
                if not tag_stack:
                    raise ParserError(f"行{line_num}: 孤立的结束标签 '{closing_tag_def['display_name']}'。")
                
                top_key, top_def, top_start_line = tag_stack[-1]
                
                if top_key != closing_tag_def['tag_key']:
                    # 尝试处理未闭合流式标签
                    if top_def['allow_unclosed']:
                        tag_stack.pop()
                        container_stack.pop()
                        if not tag_stack or tag_stack[-1][0] != closing_tag_def['tag_key']:
                            raise ParserError(f"行{line_num}: 闭合顺序错乱。尝试闭合 '{closing_tag_def['display_name']}'，但栈顶不匹配。")
                    else:
                        raise ParserError(f"行{line_num}: 闭合错误。栈顶是 '{top_def['display_name']}'，却遇到了 '{closing_tag_def['display_name']}'。")

                # 正常闭合
                tag_stack.pop()
                container_stack.pop()

            # --- 情况 C: 普通文本 ---
            else:
                content = part.strip()
                if content:
                    append_text(content)

        # --- 行末处理 (End of Line Processing) ---
        j = len(tag_stack) - 1
        while j >= 0:
            stack_key, stack_def, start_line = tag_stack[j]
            
            if start_line == line_num:
                if not stack_def['allow_multiline']:
                    if stack_def['allow_unclosed']:
                        # 自动闭合 (单行)
                        if j != len(tag_stack) - 1:
                             # 如果单行标签不在栈顶，说明前面有未闭合的内联标签，逻辑上不应该发生，或者前面那个标签已跨行（也应报错）
                             raise ParserError(f"行{line_num}: 内部逻辑错误或多层单行嵌套错误。")

                        tag_stack.pop()
                        container_stack.pop()
                    else:
                        # 单行、必须闭合 -> 报错 (如加粗)
                        raise ParserError(f"行{line_num}: 格式错误。标签 '{stack_def['display_name']}' 是单行标签且必须闭合，但在行末仍未闭合。")
            j -= 1

    # --- 文件结束 (EOF) ---
    while tag_stack:
        stack_key, stack_def, start_line = tag_stack[-1]
        
        if stack_def['allow_unclosed']:
            # 允许不闭合的，在文件末尾自动闭合
            tag_stack.pop()
            container_stack.pop()
        else:
            # 必须闭合的，如果残留则是错误
            raise ParserError(f"文件末尾错误：标签 '{stack_def['display_name']}' (行{start_line}) 未闭合。")

    return result_root

# --- 辅助函数：漂亮打印结构 ---

def print_structure(data, indent=0):
    """辅助函数：漂亮打印结果结构"""
    spacer = "  " * indent
    for item in data:
        if isinstance(item, str):
            # 打印文本时，只显示部分内容，避免打印大段换行符
            display_text = item.replace('\n', ' [\\n] ')
            if len(display_text) > 50:
                 display_text = display_text[:50] + "..."
            print(f"{spacer}📄 TEXT: {display_text}")
        else:
            print(f"{spacer}📦 TAG: {item['type']}")
            if item['children']:
                print_structure(item['children'], indent + 1)


# --- 核心测试函数 ---

def run_test(name: str, text: str, should_fail: bool = False):
    """
    运行单个测试案例并打印结果。

    Args:
        name: 测试案例名称。
        text: 输入的带标签文本。
        should_fail: 预期测试是否会引发 ParserError。
    """
    print(f"\n{'='*20} {name} {'='*20}")
    print(f"[输入文本]:\n{text.strip()}")
    print("-" * 50)
    
    lines = preprocess_text(text)
    result = None
    
    try:
        result = process_document(lines, CONFIG_DATA)
        
        if should_fail:
            print(f"\n❌ [测试失败] 预期应报错但未报错！")
        else:
            print(f"\n✅ [测试通过] 解析成功。")
            print("\n[结果结构预览]:")
            print_structure(result)
            
    except ParserError as e:
        if should_fail:
            print(f"\n✅ [测试通过] 成功捕获预期错误: {e}")
        else:
            print(f"\n❌ [测试失败] 发生意外错误: {e}")
    except Exception as e:
         print(f"\n❌ [测试失败] 代码崩溃: {e}")


if __name__ == "__main__":
    
    # --- 场景 1: 标准公文流 (隐式闭合测试) ---
    case_1 = """
    【年份】2025
    【大标题】
    关于印发《排版规范》的通知
    【-大标题】
    【一级标题】一、基本原则
    【二级标题】（一）一致性
    【正文】所有文档格式需保持一致。
    【一级标题】二、具体要求
    【正文】见附件。
    """
    run_test("场景1: 标准公文流 & 隐式闭合", case_1)

    # --- 场景 2: 合法嵌套 & 多行内容换行还原 ---
    case_2 = """
    【正文】
    这是一个包含【加粗】重要信息【-加粗】的段落。
    这是段落的第二行，应该记录换行符。
    这里引入一个文件：【引入文件】table.csv【-引入文件】。
    """
    run_test("场景2: 合法嵌套 & 换行还原", case_2)

    # --- 场景 3: 非法嵌套 (严格父级约束) ---
    # 大标题(allow_nested=False) 内部不允许出现 【加粗】
    case_3 = """
    【大标题】
    关于【加粗】违规排版【-加粗】的通报
    【-大标题】
    """
    run_test("场景3: 非法嵌套 (预期报错)", case_3, should_fail=True)

    # --- 场景 4: 单行标签跨行错误 ---
    # 加粗(allow_multiline=False, allow_unclosed=False) 必须在行内闭合
    case_4 = """
    【正文】
    这是一个【加粗】未闭合跨行
    的错误示范。【-加粗】
    """
    run_test("场景4: 单行标签跨行 (预期报错)", case_4, should_fail=True)

    # --- 场景 5: 标签交叉闭合 (错乱) ---
    # 栈顶是【加粗】，却试图闭合【正文】
    case_5 = """
    【正文】
    开始一段文字 【加粗】 粗体部分 【-正文】
    """
    run_test("场景5: 交叉闭合 (预期报错)", case_5, should_fail=True)
    
    # --- 场景 6: 连续的单行自动闭合 ---
    # 【年份】和【文号】都是 allow_multiline=False, allow_unclosed=True。
    case_6 = """
    【年份】2025
    【文号】[2025] 101号
    【正文】正文开始...
    """
    run_test("场景6: 连续单行自动闭合", case_6)

    # --- 场景 7: 必须闭合的多行标签在 EOF 未闭合 ---
    # 大标题是必须闭合的，文件结束了还没闭合 -> 报错
    case_7 = """
    【大标题】
    这是一个忘记闭合的标题
    """
    run_test("场景7: EOF未闭合错误 (预期报错)", case_7, should_fail=True)