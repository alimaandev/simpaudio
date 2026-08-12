from xml.etree import ElementTree as ET


def strip_ssml(ssml: str) -> str:
    if "<" not in ssml:
        return ssml
    try:
        root = ET.fromstring(f"<root>{ssml}</root>")
    except ET.ParseError:
        return ssml
    parts = []
    if root.text:
        parts.append(root.text)
    for child in root:
        parts.append(_get_all_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def _get_all_text(elem) -> str:
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        if child.tag == "break":
            parts.append(" ")
        else:
            parts.append(_get_all_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


class SSMLNode:
    def __init__(self, tag="text", text="", attrs=None):
        self.tag = tag
        self.text = text
        self.attrs = attrs or {}
        self.children = []

    def _content_ssml(self) -> str:
        parts = []
        if self.text and not self.children:
            parts.append(self.text)
        for c in self.children:
            parts.append(c.to_ssml())
        return "".join(parts)

    def to_ssml(self) -> str:
        if self.tag in ("root",):
            return "".join(c.to_ssml() for c in self.children)
        if self.tag == "text":
            return self.text or ""
        if self.tag == "break":
            time = self.attrs.get("time", "500ms")
            return f'<break time="{time}"/>'
        if self.tag == "prosody":
            parts = ["<prosody"]
            for k, v in self.attrs.items():
                parts.append(f' {k}="{v}"')
            parts.append(">")
            parts.append(self._content_ssml())
            parts.append("</prosody>")
            return "".join(parts)
        if self.tag == "emphasis":
            level = self.attrs.get("level", "strong")
            parts = [f'<emphasis level="{level}">']
            parts.append(self._content_ssml())
            parts.append("</emphasis>")
            return "".join(parts)
        if self.tag == "p":
            parts = ["<p>", self._content_ssml(), "</p>"]
            return "".join(parts)
        if self.tag == "say-as":
            interpret = self.attrs.get("interpret-as", "characters")
            parts = [f'<say-as interpret-as="{interpret}">']
            parts.append(self._content_ssml())
            parts.append("</say-as>")
            return "".join(parts)
        return self.text or ""

    def _content_plain(self) -> str:
        parts = []
        if self.text:
            parts.append(self.text)
        for c in self.children:
            parts.append(c.to_plain_text())
        return "".join(parts)

    def to_plain_text(self) -> str:
        if self.tag == "break":
            return " "
        if self.tag == "text":
            return self.text or ""
        return self._content_plain()


def ssml_to_tree(ssml: str) -> SSMLNode:
    if "<" not in ssml:
        node = SSMLNode("text", ssml)
        return node
    try:
        root = ET.fromstring(f"<root>{ssml}</root>")
    except ET.ParseError:
        return SSMLNode("text", ssml)

    node = SSMLNode("root")
    if root.text:
        node.children.append(SSMLNode("text", root.text))
    for child in root:
        node.children.append(_element_to_node(child))
        if child.tail:
            node.children.append(SSMLNode("text", child.tail))
    return node


def _element_to_node(elem) -> SSMLNode:
    tag_map = {
        "break": "break", "prosody": "prosody",
        "emphasis": "emphasis", "p": "p", "say-as": "say-as",
    }
    tag = tag_map.get(elem.tag, "text")
    node = SSMLNode(tag, elem.text or "", dict(elem.attrib))
    for child in elem:
        node.children.append(_element_to_node(child))
        if child.tail:
            node.children.append(SSMLNode("text", child.tail))
    return node