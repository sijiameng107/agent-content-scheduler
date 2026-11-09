import io,json,os,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch,MagicMock
from src.agent import LiveModel,ModelError,run,Tools,build_messages
F=json.loads(Path('data/fixture.json').read_text())
R={'material_ids':['M01'],'requested_slot':F['slots'][0]}
class Tests(unittest.TestCase):
 def model(self):
  with patch.dict(os.environ,{'ZHIPU_API_KEY':'test-key-not-a-real-credential'}):return LiveModel()
 def test_saved_result_is_observation_not_next_action(self):
  event={'action':'save_draft','arguments':{'material_id':'M01','proposed_slot':F['slots'][1]},'decision_summary':'save proposal','observation':{'saved':True,'save_status':'saved'}}
  messages=build_messages(R,[event])
  self.assertEqual(messages[2]['role'],'assistant')
  observed=json.loads(messages[3]['content'])
  self.assertTrue(observed['result']['saved'])
  self.assertEqual(observed['type'],'executed_tool_result')
  self.assertIn('finish',messages[-1]['content'])
 def test_permanent_error_presented_without_rewriting(self):
  event={'action':'save_draft','arguments':{'material_id':'M01','proposed_slot':F['slots'][1]},'decision_summary':'save proposal','observation':{'error':'save_failed','saved':False,'retryable':False}}
  messages=build_messages(R,[event])
  self.assertEqual(json.loads(messages[3]['content'])['result'],event['observation'])
  self.assertIn('do not retry',messages[-1]['content'])
 def test_available_requested_slot_cannot_be_arbitrarily_changed(self):
  with tempfile.TemporaryDirectory() as d:
   request={'material_ids':['M01'],'requested_slot':F['slots'][1]}
   t=Tools(F,request,str(Path(d)/'db'));t.read_material('M01');t.check_rules('M01');t.query_slots('M01')
   result=t.save_draft('M01',F['slots'][2]);self.assertEqual(result['error'],'preferred_slot_available');self.assertEqual(t.db.execute('SELECT count(*) FROM drafts').fetchone()[0],0);t.close()
 def test_premature_finish_is_returned_to_model(self):
  class Recover:
   mode='mock'
   def __init__(self):self.seen=False
   def decide(self,r,h):
    if not h:return {'action':'finish','arguments':{},'decision_summary':'mistaken end'}
    self.seen=h[-1]['observation'].get('error')=='unfinished_materials'
    return {'action':'read_material','arguments':{'material_id':'M01'},'decision_summary':'read unfinished item'}
  with tempfile.TemporaryDirectory() as d:
   m=Recover();r=run(R,F,m,str(Path(d)/'db'),max_steps=2);self.assertTrue(m.seen);self.assertEqual(r['trace'][1]['action'],'read_material');self.assertEqual(r['status'],'incomplete')
 def test_provider_and_auth(self):
  m=self.model();res=MagicMock();res.__enter__.return_value=io.StringIO(json.dumps({'id':'fake','choices':[{'finish_reason':'stop','message':{'content':json.dumps({'action':'finish','arguments':{},'decision_summary':'done'})}}]}))
  with patch('urllib.request.OpenerDirector.open',return_value=res) as call:
   self.assertEqual(m.decide(R,[])['action'],'finish');req=call.call_args.args[0];self.assertEqual(req.full_url,'https://open.bigmodel.cn/api/paas/v4/chat/completions');self.assertEqual(req.get_header('Authorization'),'Bearer '+m.key);self.assertEqual(json.loads(req.data)['model'],'glm-4-flash-250414')
 def test_http_error_redacted(self):
  m=self.model();error=urllib.error.HTTPError(m.endpoint,401,'bad',{},io.BytesIO(json.dumps({'error':{'code':'1000','message':'bad '+m.key}}).encode()))
  with patch('urllib.request.OpenerDirector.open',side_effect=error):
   with self.assertRaises(ModelError) as got:m.decide(R,[])
  self.assertEqual(got.exception.details['http_status'],401);self.assertNotIn(m.key,json.dumps(got.exception.details))
 def test_missing_key_no_fallback(self):
  with patch.dict(os.environ,{'ZHIPU_API_KEY':'','OPENROUTER_API_KEY':'wrong-platform'}):
   with self.assertRaises(ModelError):LiveModel()
 def test_invalid_response(self):
  m=self.model();res=MagicMock();res.__enter__.return_value=io.StringIO('{"choices":[]}')
  with patch('urllib.request.OpenerDirector.open',return_value=res):
   with self.assertRaises(ModelError):m.decide(R,[])
 def test_unsafe_existing_draft_invalidated(self):
  with tempfile.TemporaryDirectory() as d:
   t=Tools(F,R,str(Path(d)/'db'));t.read_material('M01');t.check_rules('M01');t.query_slots('M01');t.save_draft('M01',F['slots'][1]);t.f=json.loads(json.dumps(F));t.f['materials']['M01']['text']='保证收益';t.check_rules('M01');row=json.loads(t.db.execute('SELECT payload FROM drafts').fetchone()[0]);self.assertFalse(row['active']);t.close()
 def test_failure_retains_proposal(self):
  with tempfile.TemporaryDirectory() as d:
   t=Tools(F,R,str(Path(d)/'db'),True);t.read_material('M01');t.check_rules('M01');t.query_slots('M01');t.save_draft('M01',F['slots'][1]);self.assertEqual(t.state['M01']['suggested_slot'],F['slots'][1]);self.assertEqual(t.state['M01']['confirmation_status'],'pending_confirmation');t.close()
 def test_observation_drives_next_model_call(self):
  class RespondingModel:
   mode='mock'
   def __init__(self):self.seen=[]
   def decide(self,r,h):
    self.seen.append(json.loads(json.dumps(h)))
    if not h:return {'action':'read_material','arguments':{'material_id':'M01'},'decision_summary':'inspect'}
    assert h[-1]['observation']['found'] is True
    return {'action':'finish','arguments':{},'decision_summary':'end for controller test'}
  with tempfile.TemporaryDirectory() as d:
   m=RespondingModel();run(R,F,m,str(Path(d)/'db'),max_steps=2);self.assertEqual(len(m.seen),2);self.assertEqual(m.seen[1][0]['action'],'read_material')
 def test_malformed_action_bounded(self):
  class Bad:
   mode='mock'
   def decide(self,*args):return {'action':[],'arguments':{},'decision_summary':'bad'}
  with tempfile.TemporaryDirectory() as d:self.assertEqual(run(R,F,Bad(),str(Path(d)/'db'))['reason'],'model_error')
if __name__=='__main__':unittest.main()
