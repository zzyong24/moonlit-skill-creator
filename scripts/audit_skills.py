#!/usr/bin/env python3
"""Read-only structural signals; not a semantic, security or behavior certification."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

EXCLUDED = {'.git', 'node_modules', '__pycache__', '.venv', '.pytest_cache'}
MD_REF = re.compile(r'(!?)\[[^\]]*\]\(([^)]+)\)')
FENCE = re.compile(r'^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$')
INLINE_CODE = re.compile(r'`+[^`]*`+')
PERSONAL = re.compile(r'/Users/(?!<|\$)[A-Za-z0-9_.-]+/|C:\\\\Users\\\\[^\\\s]+', re.I)
HEADING = re.compile(r'^#{1,6}\s+(.*)$')
VAGUE_SECTION = re.compile(r'(验收|标准|检查|质量|交付|完成条件|Checklist|Acceptance)', re.I)
VAGUE_TERMS = re.compile(
    r'(高级感|电影感|冲击力|获得感|抓人眼球|吸引眼球|生动形象|通透感|质感拉满|极致体验|打动人心|引人入胜|极具张力'
    r'|(?:必须|确保|做到|保持|要求)[^。；\n]{0,8}(?:高级|生动|大气|惊艳|吸睛))'
)
NEGATION_PREFIX = re.compile(r'(禁止|严禁|禁用|不用|不要|避免|而非|代替|不以|不写|拒绝)[^。；，\n]{0,20}$')
META_NEGATION = re.compile(r'(空泛|模糊)(?:形容词|词|标准|表述)')


def audit(folder: Path, *, check_vague: bool = False) -> dict:
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
        rel_parts = path.relative_to(folder).parts
        if any(p in EXCLUDED for p in rel_parts) or path.is_symlink():
            continue
        edges[path.resolve()] = []
        fence = None
        in_vague_sec = False
        for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if PERSONAL.search(line):
                # Never echo matching content: it could contain private data.
                add('warning', 'personal_path', path, line_no, '发现个人路径；判断是运行依赖还是来源记录')
            m_fence = FENCE.match(line)
            if m_fence:
                marker = m_fence.group(1)
                if fence is None:
                    fence = (marker[0], len(marker))
                elif marker[0] == fence[0] and len(marker) >= fence[1] and not m_fence.group(2).strip():
                    fence = None
                continue
            if fence is not None:
                continue
            prose = INLINE_CODE.sub('', line)
            m_head = HEADING.match(prose)
            if m_head:
                in_vague_sec = bool(VAGUE_SECTION.search(m_head.group(1)))
            if check_vague and (in_vague_sec or re.search(r'^\s*[-*]\s*\[[ xX]\]|(?:必须|要求|验收|确保)', prose)):
                if not META_NEGATION.search(prose) and any(
                    not NEGATION_PREFIX.search(prose[:m.start()]) for m in VAGUE_TERMS.finditer(prose)
                ):
                    add('info', 'vague_criterion', path, line_no,
                        '疑似主观模糊验收词；人工核对是否应改为可观察、可核验条件')
            for bang, raw in MD_REF.findall(prose):
                target = raw.strip().split(' "', 1)[0].split(" '", 1)[0].strip('<>').split('#', 1)[0].strip()
                if not target or re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I):
                    continue
                if any(c in target for c in '{}<>$*'):
                    continue
                if bang and 'templates' in rel_parts:
                    continue
                dest = (path.parent / target).resolve()
                if not dest.is_relative_to(folder):
                    add('warning', 'external_relative_link', path, line_no,
                        '跨安装目录链接；应以显式依赖契约解析，或确认是工作区文档')
                elif not dest.exists():
                    if bang:
                        add('warning', 'missing_image', path, line_no, f'本地图片不存在：{target}')
                    else:
                        add('error', 'missing_resource', path, line_no, f'本地资源不存在：{target}')
                elif not bang:
                    edges[path.resolve()].append(dest)
    # Backtick references remain valid agent navigation; flag only as a review signal.
    queue = [main.resolve()]
    while queue:
        for dest in edges.get(queue.pop(), []):
            if dest not in reachable:
                reachable.add(dest)
                queue.append(dest)
    refs_dir = folder / 'references'
    if refs_dir.is_dir():
        for path in sorted(refs_dir.rglob('*.md')):
            if any(p in EXCLUDED for p in path.relative_to(folder).parts) or path.is_symlink():
                continue
            if path.resolve() not in reachable:
                add('info', 'reference_navigation', path, 1,
                    '未由 Markdown 链接图抵达；检查反引号导航、动态路由或历史用途')
    return {'skill': name_in_catalog, 'entry_chars': len(body), 'findings': findings,
            'behavior': '未验证', 'security': '未进行秘密扫描'}


def discover_skills(root: Path, prefix: str, scan_all: bool) -> tuple[list[Path], list[Path]]:
    if (root / 'SKILL.md').is_file():
        return [root], []
    effective_prefix = '' if scan_all else prefix
    if not effective_prefix:
        folders = sorted(
            p for p in root.iterdir()
            if p.is_dir() and not p.name.startswith('.') and p.name not in EXCLUDED and (p / 'SKILL.md').is_file()
        )
        return folders, []
    folders = sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith(effective_prefix))
    skipped = sorted(
        p for p in root.iterdir()
        if p.is_dir() and not p.name.startswith('.') and p.name not in EXCLUDED
        and not p.name.startswith(effective_prefix) and (p / 'SKILL.md').is_file()
    )
    return folders, skipped


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 10):
        raise SystemExit('需要 Python 3.10+')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    parser.add_argument('--prefix', default='moonlit-', help='父目录扫描时的子目录名前缀（默认 moonlit-）')
    parser.add_argument('--all', action='store_true', help='扫描父目录下所有含 SKILL.md 的子目录')
    parser.add_argument('--check-vague', action='store_true', help='可选提示验收/规则中疑似模糊形容词信号')
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error('目录不存在')
    folders, skipped = discover_skills(args.root, args.prefix, args.all)
    if not folders:
        if skipped:
            parser.error(
                f"没有匹配前缀 '{args.prefix}' 的 Skill（发现 {len(skipped)} 个其他含 SKILL.md 子目录；全量扫描请加 --all）"
            )
        parser.error('没有找到待审查 Skill')
    results = [audit(p, check_vague=args.check_vague) for p in folders]
    errors = sum(f['severity'] == 'error' for r in results for f in r['findings'])
    report = {'schema_version': 1, 'scope': str(args.root.resolve()),
              'skill_count': len(results), 'errors': errors, 'skills': results}
    if skipped:
        report['skipped_unmatched_skills'] = len(skipped)
    if args.format == 'json':
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        skip_note = f'（另跳过 {len(skipped)} 个非 {args.prefix} 子目录，全量加 --all）' if skipped else ''
        print(f'{len(results)} 个 Skill，{errors} 个结构错误{skip_note}；未进行行为或安全认证')
        for result in results:
            print(result['skill'])
            for f in result['findings']:
                print(f"  {f['severity']} {f['code']} {f['path']}:{f['line']} — {f['detail']}")
    return int(errors > 0)


if __name__ == '__main__':
    raise SystemExit(main())
