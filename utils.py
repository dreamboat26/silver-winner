import re

PRESENTATION_CONFIG = """
[comment]: # (CODE_THEME = base16/zenburn)
[comment]: # (controls: true)
[comment]: # (keyboard: true)

"""


def get_presentation_config() -> str:
    return PRESENTATION_CONFIG


def get_safe_foldername(topic: str) -> str:
    return topic.replace(" ", "_").lower()


def sanitize_markdown(text: str) -> str:
    pattern = r"(?s)(```mermaid.*?)(^.*?Note over.*?$)(.*?```)"
    result = re.sub(
        pattern,
        lambda m: m.group(1)
        + re.sub(r"^.*?Note over.*?\n?", "", m.group(2), flags=re.M)
        + m.group(3),
        text,
        flags=re.M,
    )
    pattern2 = r"^(#{1,2})\s"
    result = re.sub(pattern2, r"### ", result, flags=re.M)
    pattern3 = r"!\[.+\]\(\./(.*?\.png)\)"
    result = re.sub(pattern3, r"![diagram](./media/\1)", result, flags=re.M)
    result = result.replace("flowchart TD", "flowchart LR")
    return result + "\n\n"
