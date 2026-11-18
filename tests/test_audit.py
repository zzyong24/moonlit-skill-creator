import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1] / 'scripts/audit_skills.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='skill relocation ')
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name) / 'moonlit-example'
        self.skill.mkdir()

    def write(self, text):
        (self.skill / 'SKILL.md').write_text('---\nname: moonlit-example\ndescription: 示例\n---\n' + text, encoding='utf-8')

    def codes(self, **kwargs):
        return {f['code'] for f in module.audit(self.skill, **kwargs)['findings']}

    def test_valid_relocated(self):
        self.write('[参考](references/guide.md)')
        (self.skill / 'references').mkdir()
        (self.skill / 'references/guide.md').write_text('指南', encoding='utf-8')
        self.assertEqual(self.codes(), set())

    def test_missing(self):
        self.write('[参考](references/no.md)')
        self.assertIn('missing_resource', self.codes())

    def test_content_addressed_snapshot(self):
        self.write('正文')
        target = self.skill.with_name('0123456789abcdef')
        self.skill.rename(target)
        self.skill.symlink_to(target, target_is_directory=True)
        self.assertEqual(self.codes(), set())

    def test_external_is_warning_not_missing(self):
        self.write('[依赖](../other/SKILL.md)')
        self.assertEqual(self.codes(), {'external_relative_link'})

    def test_personal_path_not_echoed(self):
        self.write('读取 ' + os.path.join('/', 'Users', 'private-person', 'secret-file'))
        result = module.audit(self.skill)
        self.assertNotIn('private-person', str(result))
        self.assertIn('personal_path', self.codes())

    def test_code_fence_and_inline_links_ignored_but_personal_path_caught(self):
        p = os.path.join('/', 'Users', 'private-person', 'cfg')
        self.write(
            '行内示例 `[反例](references/fake.md)`\n'
            '```markdown\n'
            '[代码块反例](references/fake2.md)\n'
            f'{p}\n'
            '```\n'
        )
        self.assertEqual(self.codes(), {'personal_path'})

    def test_missing_image_warning_and_template_placeholder_ignored(self):
        self.write('正文')
        (self.skill / 'README.md').write_text('![首图](assets/readme/hero.png)\n', encoding='utf-8')
        (self.skill / 'templates').mkdir()
        (self.skill / 'templates/out.md').write_text('![占位](assets/1-封面.png)\n', encoding='utf-8')
        findings = module.audit(self.skill)['findings']
        self.assertEqual([(f['severity'], f['code'], f['path']) for f in findings],
                         [('warning', 'missing_image', 'README.md')])

    def test_optional_vague_criterion_respects_negation(self):
        self.write(
            '## 验收标准\n'
            '- [ ] 开头前 10 字必须有冲击力，读完充满获得感\n'
            '- [ ] 行文整体有高级感、电影感，拒绝平铺直叙\n'
            '- [ ] 拒绝高级感套话，禁用“冲击力、获得感”等模糊形容词充当标准\n'
        )
        self.assertEqual(self.codes(), set())
        findings = [f for f in module.audit(self.skill, check_vague=True)['findings'] if f['code'] == 'vague_criterion']
        self.assertEqual([f['line'] for f in findings], [6, 7])

    def test_discover_all_and_skipped_non_moonlit_skills(self):
        self.write('正文')
        custom = Path(self.tmp.name) / 'custom-fork-skill'
        custom.mkdir()
        (custom / 'SKILL.md').write_text('---\nname: custom-fork-skill\ndescription: 自有fork\n---\n正文\n', encoding='utf-8')
        hidden = Path(self.tmp.name) / '.system'
        hidden.mkdir()

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = module.main([self.tmp.name, '--format', 'json'])
        self.assertEqual(rc, 0)
        report_default = json.loads(buf.getvalue())
        self.assertEqual(report_default['skill_count'], 1)
        self.assertEqual(report_default['skipped_unmatched_skills'], 1)

        buf_all = io.StringIO()
        with contextlib.redirect_stdout(buf_all):
            rc_all = module.main([self.tmp.name, '--all', '--format', 'json'])
        self.assertEqual(rc_all, 0)
        report_all = json.loads(buf_all.getvalue())
        self.assertEqual([s['skill'] for s in report_all['skills']], ['custom-fork-skill', 'moonlit-example'])

    def test_url_fragment_and_placeholder(self):
        self.write('[站点](https://example.com) [锚](#标题) [示例](<work-dir>/README.md)')
        self.assertEqual(self.codes(), set())

    def test_read_only(self):
        self.write('正文')
        before = {p: p.read_bytes() for p in self.skill.rglob('*') if p.is_file()}
        module.audit(self.skill)
        self.assertEqual(before, {p: p.read_bytes() for p in self.skill.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
