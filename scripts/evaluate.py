"""Run all acceptance cases, save actual traces and assertions. Never fabricate live evidence."""
import argparse,copy,json,sqlite3,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.agent import run,MockModel,LiveModel,ModelError
ROOT=Path(__file__).resolve().parents[1]
def evaluate(mode,output):
 f=json.loads((ROOT/'data/fixture.json').read_text());out=Path(output);out.mkdir(parents=True,exist_ok=True)
 model=LiveModel() if mode=='live' else MockModel();records=[]
 with tempfile.TemporaryDirectory() as tmp:
  for name,mid,slot,fail in [('normal','M01',1,False),('missing','M02',0,False),('risk','M03',0,False),('conflict','M01',0,False),('save_failure','M01',0,True),('duplicate_first','M01',0,False),('duplicate_repeat','M01',0,False),('changed_occupancy','M01',0,False),('confirmed_alternative','M01',0,False)]:
   fixture=copy.deepcopy(f);r={'material_ids':[mid],'requested_slot':f['slots'][slot]}
   if name=='changed_occupancy':fixture['occupied_slots'].append(f['slots'][1])
   if name=='confirmed_alternative':r['confirmed_slot']=f['slots'][2];fixture['occupied_slots'].append(f['slots'][1])
   shared=name in ('duplicate_first','duplicate_repeat','changed_occupancy','confirmed_alternative')
   db=str(Path(tmp)/('repeat' if shared else name));p=out/name;p.mkdir(exist_ok=True)
   result=run(r,fixture,model,db,fail_save=fail);item=result['items'][0]
   with sqlite3.connect(db) as conn:rows=[json.loads(row[0]) for row in conn.execute('SELECT payload FROM drafts')]
   expected={'normal':('approved','saved'),'missing':('missing_information','not_attempted'),'risk':('blocked','not_attempted'),'conflict':('approved','saved'),'save_failure':('approved','failed'),'duplicate_first':('approved','saved'),'duplicate_repeat':('approved','duplicate'),'changed_occupancy':('approved','updated'),'confirmed_alternative':('approved','updated')}[name]
   checks={'review':item['review_status']==expected[0],'save':item['draft_save_status']==expected[1],'not_published':not item['published'],'workflow_status':result['status']==('failed' if fail else 'completed'),'draft_count':len(rows)==(0 if name in ('missing','risk','save_failure') else 1)}
   if name in ('conflict','duplicate_first','duplicate_repeat','changed_occupancy','save_failure'):checks['confirmation']=item['confirmation_status']=='pending_confirmation'
   if name in ('normal','confirmed_alternative'):checks['confirmation']=item['confirmation_status']=='confirmed'
   if name=='conflict':checks['alternative_slot']=item['suggested_slot']==f['slots'][1]
   if name in ('changed_occupancy','confirmed_alternative'):checks['alternative_slot']=item['suggested_slot']==f['slots'][2]
   if rows:checks['hard_requirement_preserved']=rows[0]['requested_slot']==r['requested_slot']
   for filename,value in [('input.json',r),('fixture.json',fixture),('output.json',result),('draft_snapshot.json',rows),('assertions.json',checks)]:
    (p/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
   records.append({'case':name,'passed':all(checks.values()),'checks':checks,'trace':f'{name}/output.json'})
   print(name, 'PASS' if all(checks.values()) else 'FAIL',flush=True)
   if result['reason']=='model_error':
    print(json.dumps(result['trace'][-1]['observation'],ensure_ascii=False));break
 summary={'model_mode':mode,'provider':getattr(model,'provider','offline'),'model':getattr(model,'model','scripted-test-double'),'expected_cases':9,'executed_cases':len(records),'passed_cases':sum(x['passed'] for x in records),'complete':len(records)==9 and all(x['passed'] for x in records),'cases':records,'limitation':'Offline tests do not prove real model decisions.' if mode=='mock' else 'Review at least two traces for observation-dependent actions; automated assertions alone are insufficient.'}
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 report=['# '+mode+' execution results','',f"Executed {len(records)}/9; passed {summary['passed_cases']}. Model: {summary['model']}.",'','| Case | Pass | Evidence |','|---|---|---|']
 report += [f"| {x['case']} | {x['passed']} | [Trace]({x['trace']}), [assertions]({x['case']}/assertions.json) |" for x in records]
 (out/'REPORT.md').write_text('\n'.join(report)+'\n\n'+summary['limitation']+'\n')
 return 0 if summary['complete'] else 2
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['mock','live'],default='mock');p.add_argument('--output',required=True);a=p.parse_args()
 try:sys.exit(evaluate(a.mode,a.output))
 except ModelError as e:print(json.dumps(e.details,ensure_ascii=False,indent=2));sys.exit(2)
