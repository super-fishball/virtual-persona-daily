# 注入回显 denylist（起步，可扩）。
_INJECTION_ECHO = (
    "忽略以上指令",
    "忽略上述指令",
    "ignore the above",
    "ignore previous instructions",
    "disregard previous",
)
# 不安全内容 denylist（起步词表，可扩）。
_UNSAFE_TERMS = ("炸弹制作方法", "制毒")
# 泄漏 prompt：系统指令**片段**被回显的最小连续字数（C2：片段检测，非整条逐字）。
_LEAK_MIN_LEN = 16


def _leaks_fragment(folded_text: str, system_instruction: str) -> bool:
    """systemInstruction 任一连续 ≥_LEAK_MIN_LEN 字跨度出现在输出 → 视为泄漏片段。

    F5：大小写不敏感（casefold），与注入回显/不安全词检测口径一致。
    """
    si = system_instruction.strip().casefold()
    if len(si) < _LEAK_MIN_LEN:
        return False
    for i in range(len(si) - _LEAK_MIN_LEN + 1):
        if si[i : i + _LEAK_MIN_LEN] in folded_text:
            return True
    return False


def scan_output(text: str, system_instruction: str) -> str | None:
    """对输出文本做三类规则匹配；命中返回原因码，否则 None。

    block-only、只看输出文本、不读业务语义（GW-1 硬线）；三类均大小写不敏感（F5）。
    """
    folded = text.casefold()
    for needle in _INJECTION_ECHO:
        if needle.casefold() in folded:
            return "injection_echo"

    if _leaks_fragment(folded, system_instruction):  # C2：片段检测
        return "prompt_leak"

    for term in _UNSAFE_TERMS:
        if term.casefold() in folded:
            return "unsafe_content"

    return None
