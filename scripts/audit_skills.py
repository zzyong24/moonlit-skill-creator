#!/usr/bin/env python3
"""Read-only structural signals; not a semantic, security or behavior certification."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

EXCLUDED = {'.git', 'node_modules', '__pycache__', '.venv', '.pytest_cache'}
LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')
PERSONAL = re.compile(r'/Users/(?!<|\$)[A-Za-z0-9_.-]+/|C:\\\\Users\\\\[^\\\s]+', re.I)


def audit(folder: Path) -> dict:
    name_in_catalog = folder.name
    folder = folder.resolve()
    findings = []

    def add(level, code, path, line, detail):
        findings.append(dict(severity=level, code=code,
                             path=str(path.relative_to(folder)), line=line, detail=detail))

    main = folder / 'SKILL.md'
    if not main.is_file():
        return {'skill': name_in_catalog, 'findings': [dict(severity='error', code='missing_entry',
                path='SKILL.md', line=1, detail='缺少入口')], 'behavior': '未验证'}
    body = main.read_text(encoding='utf-8')
    front = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', body, re.S)
    if not front:
        add('error', 'frontmatter', main, 1, '缺少 YAML frontmatter')
    else:
        fields = front.group(1)
        name = re.search(r'^name:\s*[\x22\x27]?([a-z0-9-]+)[\x22\x27]?\s*$', fields, re.M)
        if not name or name.group(1) != name_in_catalog:
            add('error', 'name', main, 2, '名称应与目录一致')
        if not re.search(r'^description:\s*\S', fields, re.M):
            add('error', 'description', main, 2, '缺少非空 description')
    if len(body) > 14000:
        add('warning', 'entry_size', main, 1, f'入口 {len(body)} 字符；检查是否可按需路由，不强制拆分')
    reachable = {main.resolve()}
    edges = {}
    for path in sorted(folder.rglob('*.md')):
        if any(p in EXCLUDED for p in path.relative_to(folder).parts) or path.is_symlink():
            continue
        edges[path.resolve()] = []
        for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if PERSONAL.search(line):
                # Never echo matching content: it could contain private data.
                add('warning', 'personal_path', path, line_no, '发现个人路径；判断是运行依赖还是来源记录')
            for raw in LINK.findall(line):
                target = raw.strip().split(' "', 1)[0].strip('<>').split('#', 1)[0]
                if not target or re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I):
                    continue
                if any(c in target for c in '{}<>$'):
                    continue
                dest = (path.parent / target).resolve()
                if not dest.is_relative_to(folder):
                    add('warning', 'external_relative_link', path, line_no,
                        '跨安装目录链接；应以显式依赖契约解析，或确认是工作区文档')
                elif not dest.exists():
                    add('error', 'missing_resource', path, line_no, f'本地资源不存在：{target}')
                else:
                    edges[path.resolve()].append(dest)
    # Backtick references remain valid agent navigation; flag only as a review signal.
    queue = [main.resolve()]
    while queue:
        for dest in edges.get(queue.pop(), []):
            if dest not in reachable:
                reachable.add(dest)
                queue.append(dest)
    for path in sorted((folder / 'references').rglob('*.md')):
        if path.resolve() not in reachable:
            add('info', 'reference_navigation', path, 1,
                '未由 Markdown 链接图抵达；检查反引号导航、动态路由或历史用途')
    return {'skill': name_in_catalog, 'entry_chars': len(body), 'findings': findings,
            'behavior': '未验证', 'security': '未进行秘密扫描'}


def main():
    if sys.version_info < (3, 10):
        raise SystemExit('需要 Python 3.10+')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    parser.add_argument('--prefix', default='moonlit-')
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error('目录不存在')
    folders = [args.root] if (args.root / 'SKILL.md').is_file() else sorted(
        p for p in args.root.iterdir() if p.is_dir() and p.name.startswith(args.prefix))
    if not folders:
        parser.error('没有找到待审查 Skill')
    results = [audit(p) for p in folders]
    errors = sum(f['severity'] == 'error' for r in results for f in r['findings'])
    report = {'schema_version': 1, 'scope': str(args.root.resolve()),
              'skill_count': len(results), 'errors': errors, 'skills': results}
    if args.format == 'json':
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f'{len(results)} 个 Skill，{errors} 个结构错误；未进行行为或安全认证')
        for result in results:
            print(result['skill'])
            for f in result['findings']:
                print(f"  {f['severity']} {f['code']} {f['path']}:{f['line']} — {f['detail']}")
    return int(errors > 0)


if __name__ == '__main__':
    raise SystemExit(main())
