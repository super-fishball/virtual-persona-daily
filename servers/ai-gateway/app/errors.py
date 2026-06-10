class GuardrailBlocked(Exception):
    """输出 guardrail 命中——block-only，映射为 HTTP 422。"""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class UpstreamUnavailable(Exception):
    """上游 DeepSeek 不可用/超时（重试后仍失败）——映射为 HTTP 502。"""
