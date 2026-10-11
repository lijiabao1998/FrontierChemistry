"""UNEXECUTED proposal: independent Decimal replay; never imports author code."""
import argparse
import copy
from decimal import Decimal as D, localcontext, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path
import random
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from admission_guard import require_admission

HERE=Path(__file__).resolve().parent
DATA='problems/CHEM-004/experiments/chem004_r1/lit_data/freesolv_database.txt'
DIGEST='2d13f095713bc39b85f85dd7b4e5483fbb12fc694bf253bb1d92a4c4d484f260'
EXPECTED_NAMES=('wrong-denominator','uncertainty-also-scaled','gaff-mae-tamper','test-mae-tamper',
                'fail-to-pass','overall-fail-to-pass','missing-check','nonfinite-metric','poison-id-tamper')

def parse(raw):
    if len(raw)!=144897 or hashlib.sha256(raw).hexdigest()!=DIGEST:
        raise ValueError('dataset bytes/hash changed')
    rows=[]; seen=set()
    for line in raw.decode('utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        parts=[x.strip() for x in line.split(';')]
        if len(parts)<10 or not all(parts[i] for i in (0,1,2,3,4,5,6)):
            raise ValueError('missing dataset fields')
        ident=parts[0]
        if ident in seen: raise ValueError('duplicate compound ID')
        seen.add(ident)
        exp,unc,calc,calc_unc=map(D,parts[3:7])
        if not all(x.is_finite() for x in (exp,unc,calc,calc_unc)) or unc<0 or calc_unc<0:
            raise ValueError('invalid numerical field')
        rows.append({'id':ident,'exp':exp,'unc':unc,'calc':calc})
    if len(rows)!=642: raise ValueError('wrong number of records')
    return rows

def display(x): return str(x.quantize(D('.001'),rounding=ROUND_HALF_EVEN))

def replay(rows,scale_uncertainty=False):
    with localcontext() as c:
        c.prec=60
        rng=random.Random(42); order=list(range(len(rows))); rng.shuffle(order)
        train,test=order[:513],order[513:]
        train_sum=sum((rows[i]['exp'] for i in train),D(0)); mu=train_sum/D(513)
        abs_error=sum((abs(mu-rows[i]['exp']) for i in test),D(0))
        sq_error=sum(((mu-rows[i]['exp'])**2 for i in test),D(0))
        poisoned=rng.sample(test,12)
        flags=[]; scores=[]
        for i in poisoned:
            row=rows[i]; label=row['exp']*D('4.184')
            source_unc=row['unc']*D('4.184') if scale_uncertainty else row['unc']
            unc=max(source_unc,D('.1'))
            numerator=abs(train_sum-D(513)*label)
            flagged=numerator>D(10)*D(513)*unc
            if flagged: flags.append(row['id'])
            scores.append({'id':row['id'],'poisoned_label':str(label),'unchanged_uncertainty':str(row['unc']),
                           'effective_uncertainty':str(unc),'exact_scaled_numerator':str(numerator),
                           'exact_scaled_threshold':str(D(10)*D(513)*unc),'z':str(numerator/(D(513)*unc)),'flagged':flagged})
        n=len(flags); detection=D(n)/D(12)
        return {'dataset_rows':642,'unit':'kcal/mol','seed':42,'train_ids':[rows[i]['id'] for i in train],
         'test_ids':[rows[i]['id'] for i in test],'poison_ids':[rows[i]['id'] for i in poisoned],
         'flagged_ids':flags,'missed_ids':[rows[i]['id'] for i in poisoned if rows[i]['id'] not in flags],
         'training_mean':str(mu),'gaff_mae':str(sum((abs(r['calc']-r['exp']) for r in rows),D(0))/D(642)),
         'gaff_mae_3dp':display(sum((abs(r['calc']-r['exp']) for r in rows),D(0))/D(642)),
         'test_mae':str(abs_error/D(129)),'test_mae_3dp':display(abs_error/D(129)),
         'test_rmse':str((sq_error/D(129)).sqrt()),'test_rmse_3dp':display((sq_error/D(129)).sqrt()),
         'poisoned_count':12,'flagged_count':n,'detection_denominator':12,'detection_fraction':str(n)+'/12',
         'detection_rate':str(detection),'uncertainty_policy':'SCALED_BY_4.184' if scale_uncertainty else 'UNSCALED_FLOOR_0.1','flag_rule':'STRICT_Z_GT_10',
         'C5_pass':detection>=D('.90'),'C5_verdict':'PASS' if detection>=D('.90') else 'FAIL',
         'total_scientific_verdict':'PASS' if detection>=D('.90') else 'FAIL','poison_scores':scores,
         'C2_net_charge_clean':'NOT_RUN','C4_scaffold_split_degrades':'INHERITED_FAIL_NOT_RUN'}

def contract(value,reference):
    # This is a report-integrity comparator to an independent replay, not a new chemical evaluator.
    required=set(reference)
    return set(value)==required and all(value[k]==reference[k] for k in required)

def controls(reference,rows):
    cases=[]
    for name,field,value in [
      ('wrong-denominator','detection_denominator',reference['flagged_count']),
      ('uncertainty-also-scaled','uncertainty_policy','SCALED_BY_4.184'),
      ('gaff-mae-tamper','gaff_mae_3dp','0.000'),
      ('test-mae-tamper','test_mae_3dp','0.000'),
      ('fail-to-pass','C5_verdict','PASS'),
      ('overall-fail-to-pass','total_scientific_verdict','PASS'),
      ('missing-check','C5_pass',None),
      ('nonfinite-metric','gaff_mae','NaN')]:
        mutant=copy.deepcopy(reference)
        if name=='uncertainty-also-scaled':mutant=replay(rows,scale_uncertainty=True)
        elif name=='wrong-denominator':
            mutant[field]=value
            mutant['detection_fraction']=str(reference['flagged_count'])+'/'+str(reference['flagged_count'])
            mutant['detection_rate']='1';mutant['C5_pass']=True;mutant['C5_verdict']='PASS';mutant['total_scientific_verdict']='PASS'
        elif name=='missing-check': mutant.pop(field)
        else: mutant[field]=value
        cases.append({'name':name,'rejected':not contract(mutant,reference),'mutant':mutant})
    mutant=copy.deepcopy(reference); mutant['poison_ids'][0]='NONEXISTENT_ID'
    cases.append({'name':'poison-id-tamper','rejected':not contract(mutant,reference),'mutant':mutant})
    return cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--round',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();require_admission(a.repo,a.round,'CHEM-004',HERE/'PROTOCOL.json')
    rows=parse((HERE/'reference'/DATA).read_bytes());r=replay(rows)
    checks=controls(r,rows)
    if tuple(x['name'] for x in checks)!=EXPECTED_NAMES or any(type(x['rejected']) is not bool for x in checks):
        raise ValueError('missing, empty, extra or invalid named controls')
    replication=(r['gaff_mae_3dp'],r['test_mae_3dp'],r['test_rmse_3dp'],r['flagged_count'])==('1.114','3.120','4.382',8)
    r.update(controls=checks,replication_pass=replication,all_controls_rejected=all(x['rejected'] for x in checks))
    r['audit_verdict']='BOUNDED_REPLICATION_COMPLETE_FROZEN_C5_FAIL' if replication and r['all_controls_rejected'] and not r['C5_pass'] else 'AUDIT_FAIL_OR_BASELINE_MISMATCH'
    a.output.parent.mkdir(parents=True,exist_ok=True); text=json.dumps(r,indent=2)+'\n';a.output.write_text(text,encoding='utf-8');print(text,end='')
    return 1 if r['audit_verdict']=='BOUNDED_REPLICATION_COMPLETE_FROZEN_C5_FAIL' else 2

if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc:
        import traceback
        print(json.dumps({'status':'FAIL_CLOSED','error':str(exc)}),file=sys.stderr);traceback.print_exc();sys.exit(2)
