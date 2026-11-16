#!/usr/bin/env python3
"""scenes.json을 "한 단계 = 한 줄" 형식으로 다시 정렬한다 (내용은 바꾸지 않음).

사용: python3 tools/format-scenes.py          # scenes.json을 제자리에서 정리
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dumps(data):
    def steps(items, ind):
        if not items:
            return "[]"
        return "[\n" + ",\n".join(ind + "  " + json.dumps(s, ensure_ascii=False) for s in items) + "\n" + ind + "]"

    blocks = []
    for s in data["scenes"]:
        keys = [k for k in s if k not in ("history", "steps")]
        head = ", ".join(f"{json.dumps(k)}: {json.dumps(s[k], ensure_ascii=False)}" for k in keys)
        blocks.append("    {\n      " + head + ",\n"
                      '      "history": ' + steps(s.get("history") or [], "      ") + ",\n"
                      '      "steps": ' + steps(s.get("steps") or [], "      ") + "\n    }")
    top = [f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},' for k, v in data.items() if k != "scenes"]
    return "{\n" + "\n".join(top) + '\n  "scenes": [\n' + ",\n".join(blocks) + "\n  ]\n}\n"


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scenes.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = dumps(data)
    assert json.loads(out) == data
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print("formatted", path)
