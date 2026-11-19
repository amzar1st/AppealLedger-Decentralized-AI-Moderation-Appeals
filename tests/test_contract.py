"""Deterministic contract tests with a small host double, not a GenVM emulator."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

class Return:
    def __init__(self, value): self.calldata = value

class Host:
    responses = []
    disagreement = False
    @classmethod
    def prompt(cls, prompt):
        assert 'CASE_DATA' in prompt
        return cls.responses.pop(0)
    @classmethod
    def run(cls, leader, validator):
        result = leader()
        if not validator(Return(result)):
            raise RuntimeError('Validator disagreement')
        return result

fake = types.ModuleType('genlayer')
fake.__all__ = ['gl', 'Address', 'u256', 'TreeMap']
class Address(str):
    def __new__(cls, value):
        return str.__new__(cls, '0x' + format(value, '040x') if isinstance(value, int) else value)

fake.Address, fake.u256, fake.TreeMap = Address, int, dict
fake.gl = types.SimpleNamespace(Contract=object, message=types.SimpleNamespace(sender_address='admin'),
    public=types.SimpleNamespace(write=lambda f:f, view=lambda f:f),
    nondet=types.SimpleNamespace(exec_prompt=Host.prompt),
    vm=types.SimpleNamespace(Return=Return, run_nondet_unsafe=Host.run))
sys.modules['genlayer'] = fake
spec = importlib.util.spec_from_file_location('contract', Path(__file__).parents[1]/'contracts/appeal_ledger.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ContractTests(unittest.TestCase):
    def setUp(self):
        fake.gl.message.sender_address = 'admin'
        self.c = m.AppealLedger(100, 100)
        self.c.policies, self.c.cases = {}, {}
        self.now = 1000
        self.c._now = lambda: self.now
        self.rules = 'Advertising is prohibited. Governance partnership proposals are permitted.'
        self.content = 'Governance proposal: approve a commercial partnership.'
        self.p = self.c.register_policy('ads', self.rules, 'https://example.org/rules/v1')
        self.case = self.c.register_decision(self.p, 'author', self.content, m.digest(self.content), 'Advertising', 'https://example.org/posts/1')
        Host.responses = []
    def appeal(self):
        fake.gl.message.sender_address = 'author'
        self.c.submit_appeal(self.case, 'This is governance.', 'The complete public post is attached to the decision.')
    def response(self, applies='YES', violation='NO', evidence='SUFFICIENT'):
        return m.encode(dict(applicability=applies, violation=violation, evidence=evidence,
            policy_quote='Governance partnership proposals are permitted.', content_quote='Governance proposal', reason='The exception applies to this proposal.'))
    def review(self, response=None):
        Host.responses = [response or self.response(), response or self.response()]
        self.c.review_appeal(self.case)
    def test_three_verdicts(self):
        for violation, evidence, expected in [('YES','SUFFICIENT','UPHOLD'), ('NO','SUFFICIENT','OVERTURN'), ('UNCERTAIN','INSUFFICIENT','INCONCLUSIVE')]:
            with self.subTest(expected=expected):
                self.setUp(); self.appeal(); self.review(self.response(violation=violation,evidence=evidence))
                fake.gl.message.sender_address = 'anyone'
                self.c.finalize_appeal(self.case)
                case = json.loads(self.c.get_case(self.case))
                self.assertEqual(case['verdict'], expected)
                self.assertEqual(len(case['audit']),4)
    def test_nonapplicable_rule_overturns(self):
        self.appeal(); self.review(self.response(applies='NO'))
        self.c.finalize_appeal(self.case)
        self.assertEqual(json.loads(self.c.get_case(self.case))['verdict'],'OVERTURN')
    def test_admin_and_author_permissions(self):
        fake.gl.message.sender_address = 'stranger'
        with self.assertRaises(ValueError): self.c.register_policy('x','x','x')
        with self.assertRaises(ValueError): self.c.register_decision(self.p,'stranger','x',m.digest('x'),'x','x')
        with self.assertRaises(ValueError): self.c.submit_appeal(self.case,'x','x')
    def test_numeric_abi_author_normalized(self):
        case_id = self.c.register_decision(self.p, 42, self.content, m.digest(self.content), 'Advertising', 'public')
        fake.gl.message.sender_address = Address(42)
        self.c.submit_appeal(case_id, 'governance', 'public post')
        self.assertEqual(json.loads(self.c.get_case(case_id))['author'], '0x000000000000000000000000000000000000002a')
    def test_hash_mismatch(self):
        with self.assertRaises(ValueError): self.c.register_decision(self.p,'author','changed','0'*64,'x','x')
    def test_locked_policy(self):
        old = self.c.get_policy(self.p)
        self.c.register_policy('ads','All partnerships banned.','https://example.org/v2')
        self.appeal(); self.review()
        self.assertEqual(self.c.get_policy(self.p),old)
        self.assertEqual(json.loads(self.c.get_case(self.case))['policy_version'],self.p)
    def test_one_appeal(self):
        self.appeal()
        with self.assertRaises(ValueError): self.c.submit_appeal(self.case,'again','again')
        self.review(); self.c.finalize_appeal(self.case)
        with self.assertRaises(ValueError): self.c.submit_appeal(self.case,'again','again')
        with self.assertRaises(ValueError): self.c.finalize_appeal(self.case)
    def test_appeal_deadline_inclusive(self):
        self.now=1100; self.appeal()
        self.setUp(); self.now=1101
        fake.gl.message.sender_address='author'
        with self.assertRaises(ValueError): self.c.submit_appeal(self.case,'x','x')
    def test_review_timeout(self):
        self.appeal()
        with self.assertRaises(ValueError): self.c.finalize_appeal(self.case)
        self.now=1101
        with self.assertRaises(ValueError): self.c.review_appeal(self.case)
        self.c.finalize_appeal(self.case)
        case=json.loads(self.c.get_case(self.case))
        self.assertEqual(case['verdict'],'INCONCLUSIVE')
        self.assertEqual(case['finalization_reason'],'REVIEW_TIMEOUT')
    def test_review_at_boundary(self):
        self.appeal(); self.now=1100; self.review()
        self.now=5000; self.c.finalize_appeal(self.case)
        self.assertEqual(json.loads(self.c.get_case(self.case))['verdict'],'OVERTURN')
    def test_no_review_or_finalize_without_appeal(self):
        with self.assertRaises(ValueError): self.c.review_appeal(self.case)
        self.now=5000
        with self.assertRaises(ValueError): self.c.finalize_appeal(self.case)
    def test_disagreement_preserves_pending_case(self):
        self.appeal(); before=self.c.get_case(self.case)
        Host.responses=[self.response(),self.response(violation='YES')]
        with self.assertRaises(RuntimeError): self.c.review_appeal(self.case)
        self.assertEqual(before,self.c.get_case(self.case))
    def test_validator_failure_rejects_review(self):
        self.appeal(); before=self.c.get_case(self.case)
        Host.responses=[self.response(),'not JSON']
        with self.assertRaises(ValueError): self.c.review_appeal(self.case)
        self.assertEqual(before,self.c.get_case(self.case))
    def test_malformed_assessments(self):
        valid=json.loads(self.response())
        for key,value in [('applicability','MAYBE'),('evidence','yes'),('policy_quote','invented'),('content_quote','invented'),('reason',''),('content_quote','')]:
            data=dict(valid); data[key]=value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError): m.assessment(m.encode(data),self.rules,self.content)
        with self.assertRaises(ValueError): m.assessment('[]',self.rules,self.content)
    def test_different_reason_wording_agrees(self):
        self.appeal(); second=json.loads(self.response()); second['reason']='A policy exception permits this.'
        Host.responses=[self.response(),m.encode(second)]
        self.c.review_appeal(self.case)
    def test_applicability_disagreement_rejected(self):
        self.appeal(); Host.responses=[self.response(),self.response(applies='NO')]
        with self.assertRaises(RuntimeError): self.c.review_appeal(self.case)
    def test_audit_chain(self):
        self.appeal(); self.review(); self.c.finalize_appeal(self.case)
        case=json.loads(self.c.get_case(self.case)); previous=''
        for item in case['audit']:
            self.assertEqual(item['previous'],previous)
            entry=dict(item); saved=entry.pop('hash')
            self.assertEqual(m.digest(m.encode(entry)),saved); previous=saved
        self.assertEqual(case['audit'][-1]['state_hash'],m.digest(m.encode({k:v for k,v in case.items() if k!='audit'})))
    def test_bounds_and_unknown_ids(self):
        for windows in [(0,100),(100,2592001)]:
            with self.assertRaises(ValueError): m.AppealLedger(*windows)
        with self.assertRaises(ValueError): self.c.get_case('missing')
        with self.assertRaises(ValueError): self.c.get_policy('missing')
        with self.assertRaises(ValueError): self.c.register_policy('ads','x'*12001,'x')

if __name__=='__main__': unittest.main()
