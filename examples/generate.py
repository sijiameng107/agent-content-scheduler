"""Generate actual mock evidence, not real-model decision evidence."""
import copy,json,tempfile
from pathlib import Path
from src.agent import run,MockModel
f=json.loads(Path('data/fixture.json').read_text())
def save(name,r,f,db,fail=False):
 p=Path('examples')/name;p.mkdir(exist_ok=True)
 for n,v in [('input.json',r),('fixture.json',f),('output.json',run(r,f,MockModel(),db,fail_save=fail))]:(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
with tempfile.TemporaryDirectory() as tmp:
 for name,m,slot,fail in [('normal','M01',1,False),('missing','M02',0,False),('risk','M03',0,False),('conflict','M01',0,False),('save_failure','M01',0,True)]:save(name,{'material_ids':[m],'requested_slot':f['slots'][slot]},f,str(Path(tmp)/name),fail)
 r={'material_ids':['M01'],'requested_slot':f['slots'][0]};db=str(Path(tmp)/'repeat');save('duplicate_first',r,f,db);save('duplicate_repeat',r,f,db)
 changed=copy.deepcopy(f);changed['occupied_slots'].append(f['slots'][1]);save('changed_occupancy',r,changed,db)
