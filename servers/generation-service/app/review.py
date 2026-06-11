import re

from app.errors import CODE_PERSONALITY_REJECTED, GenError

# 结构化规则启发式（spec §9·③）：纵深第二道，cheap、命中即拒，非穷尽、非 ML。
_ROLE_MARKERS = re.compile(r"(?i)\b(system|assistant|user)\s*[:：]")
_DELIMITER_MARKERS = re.compile(r"(#{3,}|</?(system|prompt|context)>)", re.IGNORECASE)
# 含 `=` 于字符类内：base64 带 `=` 填充时（含拼接的多段 blob）填充符不应切断长串判定。
_BASE64_BLOB = re.compile(r"[A-Za-z0-9+/=]{80,}")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def review_personality(text: str) -> None:
    """录入审核第二道：命中注入特征即 400 personality_rejected。"""
    for pattern in (_ROLE_MARKERS, _DELIMITER_MARKERS, _BASE64_BLOB, _CONTROL_CHARS):
        if pattern.search(text):
            raise GenError(400, CODE_PERSONALITY_REJECTED, "personality rejected by review")
