import re
import json
from typing import List, Dict, Union, Any

# --- 1. CONFIG (使用用户提供的新配置) ---
CONFIG_JSON_STRING = """
{
  "tag_definitions": [
    {
      "tag_key": "DOC_YEAR",
      "display_name": "年份",
      "start_tag": "【年份】",
      "end_tag": "【-年份】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "DOC_GENRE",
      "display_name": "文种",
      "start_tag": "【文种】",
      "end_tag": "【-文种】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "DOC_ID",
      "display_name": "文号",
      "start_tag": "【文号】",
      "end_tag": "【-文号】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "H0",
      "display_name": "大标题",
      "start_tag": "【大标题】",
      "end_tag": "【-大标题】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": true,
      "single_label_only": false
    },
    {
      "tag_key": "H1",
      "display_name": "一级标题",
      "start_tag": "【一级标题】",
      "end_tag": "【-一级标题】",
      "allow_unclosed": true,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "H2",
      "display_name": "二级标题",
      "start_tag": "【二级标题】",
      "end_tag": "【-二级标题】",
      "allow_unclosed": true,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "H3",
      "display_name": "三级标题",
      "start_tag": "【三级标题】",
      "end_tag": "【-三级标题】",
      "allow_unclosed": true,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "H4",
      "display_name": "四级标题",
      "start_tag": "【四级标题】",
      "end_tag": "【-四级标题】",
      "allow_unclosed": true,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H1",
      "display_name": "一级标题开头段",
      "start_tag": "【一级标题开头段】",
      "end_tag": null,
      "allow_unclosed": true,
      "allow_nested": true,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H2",
      "display_name": "二级标题开头段",
      "start_tag": "【二级标题开头段】",
      "end_tag": null,
      "allow_unclosed": true,
      "allow_nested": true,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H3",
      "display_name": "三级标题开头段",
      "start_tag": "【三级标题开头段】",
      "end_tag": null,
      "allow_unclosed": true,
      "allow_nested": true,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H4",
      "display_name": "四级标题开头段",
      "start_tag": "【四级标题开头段】",
      "end_tag": null,
      "allow_unclosed": true,
      "allow_nested": true,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H1_HEAD",
      "display_name": "段内一级标题",
      "start_tag": "【段内一级标题】",
      "end_tag": "【-段内一级标题】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H2_HEAD",
      "display_name": "段内二级标题",
      "start_tag": "【段内二级标题】",
      "end_tag": "【-段内二级标题】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H3_HEAD",
      "display_name": "段内三级标题",
      "start_tag": "【段内三级标题】",
      "end_tag": "【-段内三级标题】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "P_H4_HEAD",
      "display_name": "段内四级标题",
      "start_tag": "【四级标题开头段】",
      "end_tag": "【-四级标题开头段】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "PARAGRAPH",
      "display_name": "正文",
      "start_tag": "【正文】",
      "end_tag": null,
      "allow_unclosed": true,
      "allow_nested": true,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "BOLD",
      "display_name": "加粗",
      "start_tag": "【加粗】",
      "end_tag": "【-加粗】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "ITALIC_KAI",
      "display_name": "楷体强调",
      "start_tag": "【楷体强调】",
      "end_tag": "【-楷体强调】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": false
    },
    {
      "tag_key": "SIGNATURE",
      "display_name": "落款",
      "start_tag": "【落款】",
      "end_tag": "【-落款】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": true,
      "single_label_only": false
    },
    {
      "tag_key": "SIGNATURE_DATE",
      "display_name": "落款日期",
      "start_tag": "【落款日期】",
      "end_tag": "【-落款日期】",
      "allow_unclosed": true,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": true
    },
    {
      "tag_key": "INCLUDE",
      "display_name": "引入文件",
      "start_tag": "【引入文件】",
      "end_tag": "【-引入文件】",
      "allow_unclosed": false,
      "allow_nested": false,
      "allow_multiline": false,
      "single_label_only": true
    }
  ]
}
"""
CONFIG_DATA = json.loads(CONFIG_JSON_STRING)

class ParserError(Exception):
    pass

def preprocess_text(raw_text: str) -> List[str]:
    """仅处理换行符，不进行行首行尾修剪。"""
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    return lines

def process_document(lines: List[str], config: Dict[str, List[Dict[str, Any]]]):
    # --- 初始化映射 ---
    tag_map = {}
    end_tag_map = {}
    for tag_def in config['tag_definitions']:
        tag_map[tag_def['start_tag']] = tag_def
        if tag_def['end_tag']:
            end_tag_map[tag_def['end_tag']] = tag_def

    # --- 核心数据结构 ---
    result_root = []  
    container_stack = [result_root] 
    tag_stack = [] 
    
    # 辅助正则
    sorted_tags = sorted(list(tag_map.keys()) + list(end_tag_map.keys()), key=len, reverse=True)
    tag_regex = re.compile(f'({"|".join(re.escape(t) for t in sorted_tags)})')

    # --- 内部辅助函数：安全追加文本 ---
    def append_text(text_content):
        if not text_content.strip() and text_content != "\n":
             return
             
        current_list = container_stack[-1]
        if current_list and isinstance(current_list[-1], str):
            current_list[-1] += text_content
        else:
            current_list.append(text_content)

    for i, line in enumerate(lines):
        line_num = i + 1
        
        # 1. 消除 UTF-8 空白字符，并进行行首行尾修剪
        line_cleaned = line.replace('\u3000', ' ').replace('\xa0', ' ')
        trimmed_line = line_cleaned.strip()
        
        if not trimmed_line:
            continue

        # --- 检查 single_label_only 约束 (已修复对结束标签的误判) ---
        tags_on_line = tag_regex.findall(trimmed_line)
        
        # 1. 找到该行所有的 SLO 起始标签
        slo_start_tags_on_line = [t for t in tags_on_line if t in tag_map and tag_map[t].get('single_label_only')]
        
        if slo_start_tags_on_line:
            # Enforce: 多个 SLO 起始标签在一行
            if len(slo_start_tags_on_line) > 1:
                raise ParserError(f"行{line_num}: 约束违规。发现多个 Single Label Only 标签同时出现在一行。")
            
            slo_start_tag = slo_start_tags_on_line[0]
            slo_def = tag_map[slo_start_tag]
            
            # 定义该 SLO 元素允许出现在本行的所有标签（起始标签和结束标签）
            allowed_tags = {slo_def['start_tag']}
            if slo_def['end_tag']:
                allowed_tags.add(slo_def['end_tag'])
            
            # 2. 检查是否有除 SLO 起始/结束标签外的其他标签
            for t in tags_on_line:
                if t not in allowed_tags:
                     raise ParserError(f"行{line_num}: 约束违规。Single Label Only 标签 '{slo_def['display_name']}' 旁边发现了其他标签 '{t}'。")

            # 3. 检查标签外部是否存在内容
            temp_line = trimmed_line
            for tag in tags_on_line:
                # 使用 replace 确保只替换一次
                temp_line = temp_line.replace(tag, '|SPLIT|', 1) 
            
            content_parts = [p.strip() for p in temp_line.split('|SPLIT|')]
            
            # 检查第一个和最后一个部分（即标签外部）是否包含文本
            if content_parts[0] or content_parts[-1]:
                raise ParserError(f"行{line_num}: 约束违规。Single Label Only 标签 '{slo_def['display_name']}' 旁边发现了额外内容。")

        # --- 处理多行标签的换行符 ---
        if tag_stack:
            top_key, top_def, _ = tag_stack[-1]
            if top_def['allow_multiline'] and not top_def['allow_unclosed']:
                if line_num > tag_stack[-1][2]: 
                    append_text("\n") 
        
        parts = tag_regex.split(trimmed_line)
        for part in parts:
            if not part:
                continue

            # --- 情况 A: 起始标签 ---
            if part in tag_map:
                new_tag_def = tag_map[part]
                
                # 1. 隐式闭合检查
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
                    if top_def['allow_unclosed']:
                        tag_stack.pop()
                        container_stack.pop()
                        if not tag_stack or tag_stack[-1][0] != closing_tag_def['tag_key']:
                            raise ParserError(f"行{line_num}: 闭合顺序错乱。")
                    else:
                        raise ParserError(f"行{line_num}: 闭合错误。栈顶是 '{top_def['display_name']}' (行{top_start_line})，却遇到了 '{closing_tag_def['display_name']}'。")

                # 正常闭合
                tag_stack.pop()
                container_stack.pop()

            # --- 情况 C: 普通文本 ---
            else:
                append_text(part)

        # --- 行末处理 (End of Line Processing) ---
        j = len(tag_stack) - 1
        while j >= 0:
            stack_key, stack_def, start_line = tag_stack[j]
            
            if not stack_def['allow_multiline']:
                if stack_def['allow_unclosed']:
                    if j == len(tag_stack) - 1:
                        tag_stack.pop()
                        container_stack.pop()
                    else:
                        j -= 1
                        continue
                else:
                    if start_line == line_num:
                        raise ParserError(f"行{line_num}: 格式错误。标签 '{stack_def['display_name']}' 必须在行内显式闭合，但未闭合。")
            j -= 1

    # --- 文件结束 (EOF) ---
    while tag_stack:
        stack_key, stack_def, start_line = tag_stack[-1]
        
        if stack_def['allow_unclosed']:
            tag_stack.pop()
            container_stack.pop()
        else:
            raise ParserError(f"文件末尾错误：标签 '{stack_def['display_name']}' (行{start_line}) 未闭合。")

    return result_root

# --- 辅助函数：漂亮打印结构 ---

def print_structure(data: List[Union[str, Dict[str, Any]]], indent: int = 0):
    """辅助函数：漂亮打印结果结构"""
    spacer = "  " * indent
    for item in data:
        if isinstance(item, str):
            display_text = item.strip().replace('\n', ' [\\n] ')
            if len(display_text) > 50:
                 display_text = display_text[:50] + "..."
            if display_text:
                 print(f"{spacer}📄 TEXT: {display_text}")
        else:
            print(f"{spacer}📦 TAG: {item['type']}")
            if item['children']:
                print_structure(item['children'], indent + 1)


# --- 核心测试函数 ---

def run_test(name: str, text: str, should_fail: bool = False):
    """运行单个测试案例并打印结果。"""
    print(f"\n{'='*20} {name} {'='*20}")
    print(f"[输入文本]:\n{text.strip()}")
    print("-" * 50)
    
    lines = preprocess_text(text)
    
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
         print(f"\n❌ [测试失败] 代码崩溃: {type(e).__name__}: {e}")


if __name__ == "__main__":
    
    # --- A. 成功的测试用例 (验证基本功能) ---
    
    run_test("场景1: 显式闭合 (年份) & 隐式闭合 (H1/H2/正文)", """
    【年份】2025【-年份】
    【大标题】
    关于印发《排版规范》的通知
    【-大标题】
    【一级标题】一、基本原则
    【二级标题】（一）一致性
    【正文】所有文档格式需保持一致。
    【一级标题】二、具体要求
    【正文】见附件。
    """)

    run_test("场景6: 连续流式自动闭合", """
    【一级标题】一
    【二级标题】二
    【正文】正文开始...
    """)
    
    run_test("场景8: single_label_only 成功 (已修复)", """
    【落款日期】2025年1月1日【-落款日期】
    【正文】正常内容。
    """)
    
    # --- B. 预期失败的约束案例 (验证错误处理) ---

    # B1. 嵌套约束失败
    run_test("场景3: 嵌套违规 (H0 不允许嵌套) (预期报错)", """
    【大标题】
    关于【加粗】违规排版【-加粗】的通报
    【-大标题】
    """, should_fail=True)

    # B2. 闭合/跨行约束失败
    run_test("场景4: 严格单行标签跨行 (DOC_YEAR 预期报错)", """
    【年份】2025
    【-年份】
    """, should_fail=True)

    run_test("场景5: 闭合顺序错乱 (预期报错)", """
    【正文】
    开始一段文字 【加粗】 粗体部分 【-正文】
    """, should_fail=True)
    
    run_test("场景7: EOF未闭合错误 (H0 必须闭合) (预期报错)", """
    【大标题】
    这是一个忘记闭合的标题
    """, should_fail=True)
    
    # B3. Single Label Only 约束失败
    
    # 场景2: 包含 SLO 标签的行，但标签前后有文本
    run_test("场景2: SLO 标签前后有文本 (违反 SLO 约束) (预期报错)", """
    【正文】
    这是一个包含【加粗】重要信息【-加粗】的段落。
    这里引入一个文件：【引入文件】table.csv【-引入文件】。
    """, should_fail=True)

    # 场景9: single_label_only 失败案例 (标签后有文本)
    run_test("场景9: SLO 失败 (标签后有文本) (预期报错)", """
    【落款日期】2025年1月1日【-落款日期】文本
    【正文】正常内容。
    """, should_fail=True)
    
    # 场景10: single_label_only 失败案例 (多个标签)
    run_test("场景10: SLO 失败 (同一行有多个标签) (预期报错)", """
    【引入文件】file.doc【-引入文件】【年份】2025【-年份】
    【正文】正常内容。
    """, should_fail=True)