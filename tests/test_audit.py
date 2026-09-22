import importlib.util
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

    def codes(self):
        return {f['code'] for f in module.audit(self.skill)['findings']}

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
        target=self.skill.with_name('0123456789abcdef')
        self.skill.rename(target)
        self.skill.symlink_to(target,target_is_directory=True)
        self.assertEqual(self.codes(),set())

    def test_external_is_warning_not_missing(self):
        self.write('[依赖](../other/SKILL.md)')
        self.assertEqual(self.codes(), {'external_relative_link'})

    def test_personal_path_not_echoed(self):
        self.write('读取 /Users/private-person/secret-file')
        result = module.audit(self.skill)
        self.assertNotIn('private-person', str(result))
        self.assertIn('personal_path', self.codes())

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
