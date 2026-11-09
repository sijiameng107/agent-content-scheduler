import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from src.agent import run,MockModel,Tools
F=json.loads(Path('data/fixture.json').read_text())
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/'db');self.req={'material_ids':['M01'],'requested_slot':F['slots'][0]}
 def tearDown(self):self.tmp.cleanup()
 def go(self,**kw):return run(self.req,kw.pop('fixture',F),MockModel(),self.db,**kw)
 def count(self):
  with sqlite3.connect(self.db) as c:return c.execute('SELECT count(*) FROM drafts').fetchone()[0]
 def test_conflict(self):
  s=self.go()['items'][0];self.assertEqual(s['suggested_slot'],F['slots'][1]);self.assertEqual(s['confirmation_status'],'pending_confirmation');self.assertFalse(s['published'])
 def test_normal(self):
  self.req['requested_slot']=F['slots'][1];s=self.go()['items'][0];self.assertEqual(s['confirmation_status'],'confirmed');self.assertEqual(s['draft_save_status'],'saved')
 def test_missing(self):
  self.req['material_ids']=['M02'];s=self.go()['items'][0];self.assertEqual(s['review_status'],'missing_information');self.assertEqual(s['draft_save_status'],'not_attempted')
 def test_risk(self):
  self.req['material_ids']=['M03'];s=self.go()['items'][0];self.assertEqual(s['review_status'],'blocked');self.assertTrue(s['risk_reasons'])
 def test_duplicate(self):
  self.go();self.assertEqual(self.go()['items'][0]['draft_save_status'],'duplicate');self.assertEqual(self.count(),1)
 def test_failed_save(self):
  r=self.go(fail_save=True);self.assertEqual(r['status'],'failed');self.assertEqual(r['items'][0]['draft_save_status'],'failed');self.assertEqual(self.count(),0)
 def test_changed_occupancy(self):
  self.go();f=copy.deepcopy(F);f['occupied_slots'].append(F['slots'][1]);s=self.go(fixture=f)['items'][0];self.assertEqual(s['suggested_slot'],F['slots'][2]);self.assertEqual(s['draft_save_status'],'updated');self.assertEqual(s['confirmation_status'],'pending_confirmation');self.assertEqual(self.count(),1)
 def test_confirmation(self):
  self.go();self.req['confirmed_slot']=F['slots'][1];s=self.go()['items'][0];self.assertEqual(s['confirmation_status'],'confirmed');self.assertEqual(s['draft_save_status'],'updated')
 def test_limit(self):
  r=self.go(max_steps=1);self.assertEqual(r['status'],'incomplete');self.assertEqual(r['reason'],'limit_reached');self.assertEqual(r['steps_used'],1)
 def test_bypass(self):
  t=Tools(F,self.req,self.db)
  try:
   self.assertIn('error',t.call('save_draft',{'material_id':'M01','proposed_slot':F['slots'][1]}));self.assertIn('error',t.call('publish',{}));self.assertIn('error',t.call('read_material',{'material_id':'other'}))
  finally:t.close()
 def test_early_finish(self):
  class Early:
   mode='mock'
   def decide(self,*a):return {'action':'finish','arguments':{},'decision_summary':'done'}
  self.assertEqual(run(self.req,F,Early(),self.db)['status'],'incomplete')
 def test_no_slots(self):
  f=copy.deepcopy(F);f['occupied_slots']=f['slots'];self.assertEqual(self.go(fixture=f)['status'],'incomplete')
 def test_batch(self):
  f=copy.deepcopy(F);f['materials']['M04']=dict(f['materials']['M01']);self.req['material_ids']=['M01','M04'];r=self.go(fixture=f);self.assertEqual(r['status'],'completed');self.assertNotEqual(r['items'][0]['suggested_slot'],r['items'][1]['suggested_slot'])
if __name__=='__main__':unittest.main()
