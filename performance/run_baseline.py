"""Three reproducible, paced rounds per endpoint, with raw monitoring and evidence."""
import argparse
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

import psutil

from database_fixture import DATABASE, SNAPSHOT, connect, data_state, fingerprint

PERF = Path(__file__).resolve().parent
REPO = PERF.parent
TZ = dt.timezone(dt.timedelta(hours=8))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def code_manifest():
    paths = list((REPO / '后端flask').rglob('*.py'))
    paths = [p for p in paths if not any(x.startswith('.') or x in ('venv','__pycache__') for x in p.relative_to(REPO).parts)]
    for pattern in ['*.py', '*.ps1', '*.groovy', '*.jmx', 'tools-lock.json', 'schema.sql']:
        paths.extend(p for p in PERF.rglob(pattern) if '.local' not in p.parts)
    return {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def restore():
    p = subprocess.run([sys.executable, str(PERF / 'database_fixture.py'), 'reset'],
                       capture_output=True, text=True, encoding='utf-8', check=True)
    return json.loads(p.stdout.strip().splitlines()[-1])


def public_state():
    with connect(DATABASE) as conn:
        state = data_state(conn)
        return {'sha256': fingerprint(state), 'counts': {t: len(v['rows']) for t, v in state.items()}}


def monitored_run(scenario, loops, destination, args, backend_pid, mysql_pid):
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(PERF / 'run-jmeter.ps1'),
               '-Scenario', scenario, '-Threads', str(args.threads), '-Loops', str(loops),
               '-Ramp', str(args.ramp), '-ThinkMs', str(args.think_ms), '-Port', str(args.port),
               '-OutputDirectory', str(destination)]
    # Wrapper must create a NEW directory; console log stays in its parent initially.
    console = destination.parent / (destination.name + '-console.log')
    processes = {'backend': psutil.Process(backend_pid), 'mysql': psutil.Process(mysql_pid)}
    for process in processes.values(): process.cpu_percent()
    psutil.cpu_percent()
    columns = ['timestamp_ms', 'system_cpu_pct', 'system_memory_pct', 'system_used_mib']
    for role in ['backend','mysql','jmeter']:
        columns += [role + '_cpu_pct_one_core', role + '_cpu_pct_host', role + '_rss_mib']
    monitor_path = destination.parent / (destination.name + '-monitor.csv')
    samples = []
    with console.open('w', encoding='utf-8') as output, monitor_path.open('w', newline='', encoding='utf-8') as monitor:
        writer = csv.DictWriter(monitor, fieldnames=columns); writer.writeheader()
        child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT,
                                 env={**os.environ, 'PYTHONIOENCODING':'utf-8'})
        while child.poll() is None:
            if 'jmeter' not in processes:
                try:
                    for descendant in psutil.Process(child.pid).children(recursive=True):
                        if descendant.name().lower() == 'java.exe':
                            descendant.cpu_percent(); processes['jmeter'] = descendant; break
                except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            memory = psutil.virtual_memory()
            row = {'timestamp_ms': int(time.time()*1000), 'system_cpu_pct': psutil.cpu_percent(),
                   'system_memory_pct': memory.percent, 'system_used_mib': memory.used / 1048576}
            for role, process in processes.items():
                try:
                    cpu = process.cpu_percent()
                    row[role+'_cpu_pct_one_core'] = cpu
                    row[role+'_cpu_pct_host'] = cpu / psutil.cpu_count()
                    row[role+'_rss_mib'] = process.memory_info().rss / 1048576
                except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            writer.writerow(row); monitor.flush(); samples.append(row)
            time.sleep(1)
        code = child.wait()
    destination.mkdir(exist_ok=True)
    console.replace(destination / 'console.log'); monitor_path.replace(destination / 'monitor.csv')
    if code:
        raise RuntimeError(f'{scenario} failed with exit={code}; inspect {destination}')
    with (destination / 'results.jtl').open(encoding='utf-8-sig') as handle:
        rows = list(csv.DictReader(handle))
    business = [r for r in rows if r['label'] == 'business-'+scenario]
    assert len(business) == args.threads * loops
    assert all(r['success'] == 'true' for r in rows)
    stats = json.loads((destination / 'html/statistics.json').read_text(encoding='utf-8'))['business-'+scenario]
    # Resource summary is restricted to HTTP business first-start..last-finish, not HTML generation.
    start = min(int(r['timeStamp']) for r in business)
    end = max(int(r['timeStamp'])+int(r['elapsed']) for r in business)
    measured = [r for r in samples if start <= r['timestamp_ms'] <= end]
    assert measured, 'No monitoring during business samples'
    monitoring = {}
    for key in columns[1:]:
        values = [float(r[key]) for r in measured if key in r]
        if values: monitoring[key] = {'mean':statistics.mean(values), 'max':max(values)}
    summary = {'scenario':scenario,'threads':args.threads,'loops':loops,'business_samples':len(business),
               'all_samples':len(rows),'all_failures':0,'p95_ms':stats['pct2ResTime'],
               'throughput_rps':stats['throughput'],'error_pct':stats['errorPct'],
               'business_window_seconds':(end-start)/1000,'monitor_samples':len(measured),'resources':monitoring}
    write_json(destination/'summary.json',summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--threads',type=int,default=2)
    parser.add_argument('--loops',type=int,default=20)
    parser.add_argument('--warmup-loops',type=int,default=3)
    parser.add_argument('--rounds',type=int,default=3)
    parser.add_argument('--ramp',type=int,default=1)
    parser.add_argument('--think-ms',type=int,default=1500)
    parser.add_argument('--port',type=int,default=5001)
    args = parser.parse_args()
    if args.threads < 1 or args.loops < 1 or args.rounds < 1 or args.warmup_loops < 1:
        parser.error('All counts must be positive')
    if args.think_ms < args.threads * 750:
        parser.error('Pacing must allow shared 100/min IP limit: think-ms >= threads*750')
    process_info=json.loads((PERF/'.local'/f'backend-process-{args.port}.json').read_text(encoding='utf-8-sig'))
    assert process_info['database'] == DATABASE and process_info['tunnel'] and not process_info['debug']
    backend_pid=process_info['pid']
    assert psutil.pid_exists(backend_pid)
    with connect(DATABASE) as conn, conn.cursor() as q:
        q.execute('SELECT VERSION()'); mysql_version=q.fetchone()[0]
        q.execute("SHOW VARIABLES LIKE 'pid_file'"); pid_path=Path(q.fetchone()[1])
        mysql_pid=int(pid_path.read_text().strip())
        q.execute('SELECT @@character_set_database, @@collation_database'); charset,collation=q.fetchone()
    now=dt.datetime.now(TZ)
    target=REPO/'基线报告'/'baseline'/now.strftime('%Y%m%d-%H%M%S')
    target.mkdir(parents=True,exist_ok=False)
    cpu_info=subprocess.check_output(['powershell','-NoProfile','-Command',
        'Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json -Compress'],text=True)
    source=code_manifest()
    write_json(target/'source-manifest.json',source)
    patch=subprocess.check_output(['git','-C',str(REPO),'diff','HEAD','--','后端flask'])
    (target/'backend-working-tree.patch').write_bytes(patch)
    environment={'checked_at':now.isoformat(),'base_commit':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
        'platform':platform.platform(),'cpu':json.loads(cpu_info),'physical_cores':psutil.cpu_count(logical=False),
        'logical_cores':psutil.cpu_count(),'memory_gib':psutil.virtual_memory().total/1073741824,
        'python':sys.version,'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
        'mysql_version':mysql_version,'charset':charset,'collation':collation,
        'backend_pid':backend_pid,'mysql_pid':mysql_pid,'database':DATABASE,
        'server':'Flask built-in threaded server, debug/reloader off',
        'endpoint':f'http://127.0.0.1:{args.port}','tls':False,'tunnel':'SM2 + SM4-CBC enabled for login',
        'rate_limit':'login decorator disabled in existing code; cart/order/readback share 100 requests/IP/60s',
        'pool':{'pool_size':10,'max_overflow':20,'pool_timeout':30,'pool_recycle':1800,'pool_pre_ping':True},
        'tools':json.loads((PERF/'tools-lock.json').read_text()),'parameters':vars(args),
        'initial_snapshot_sha256':json.loads(SNAPSHOT.read_text())['sha256'],
        'monitoring':'psutil 1s; CPU one-core percent and host-normalized percent; RSS MiB; localhost shared load generator',
        'source_sha256':fingerprint(source)}
    write_json(target/'environment.json',environment)
    print('EVIDENCE',target,flush=True)
    results=[]
    for scenario in ['login','products','order']:
        for round_no in range(1,args.rounds+1):
            assert code_manifest()==source,'Code changed during baseline; aborting'
            directory=target/scenario/f'run{round_no}'
            directory.mkdir(parents=True)
            write_json(directory/'before-warmup.json',restore())
            print(f'START {scenario} round {round_no}: warmup',flush=True)
            monitored_run(scenario,args.warmup_loops,directory/'warmup',args,backend_pid,mysql_pid)
            write_json(directory/'before-measurement.json',restore())
            print(f'START {scenario} round {round_no}: measurement',flush=True)
            summary=monitored_run(scenario,args.loops,directory/'measurement',args,backend_pid,mysql_pid)
            summary['round']=round_no
            after=public_state();write_json(directory/'after-measurement.json',after)
            if scenario=='order':
                assert after['counts']['order']==args.threads*args.loops
                assert after['counts']['order_item']==args.threads*args.loops
                assert after['counts']['cart_item']==0
            results.append(summary);write_json(target/'summary.json',results)
            print(f"PASS {scenario} round {round_no}: n={summary['business_samples']}, p95={summary['p95_ms']:.2f}ms, error=0%",flush=True)
    assert code_manifest()==source
    with (target/'metrics.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        fields=['scenario','round','threads','loops','business_samples','throughput_rps','p95_ms','error_pct','all_failures','monitor_samples']
        writer=csv.DictWriter(handle,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(results)
    write_json(target/'completion.json',{'status':'complete','finished_at':dt.datetime.now(TZ).isoformat(),
        'runs':len(results),'business_samples':sum(r['business_samples'] for r in results),
        'code_unchanged':True,'original_database':'not modified; dedicated perf9_baseline used'})
    print('COMPLETE',target,flush=True)


if __name__=='__main__':main()
