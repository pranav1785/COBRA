"""Optional Codex bundled compiler wrapper; ordinary users may run tectonic main.tex."""
from pathlib import Path
import subprocess,sys,json,re
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/'report/main.tex'
output=Path(sys.argv[2]) if len(sys.argv)>2 else root/'report'
plugins=Path.home()/'.codex/plugins/cache/openai-bundled/latex'
scripts=sorted(plugins.glob('*/scripts/compile_latex.py'))
if not scripts:raise SystemExit('Use a standard LaTeX installation: tectonic main.tex')
p=subprocess.run([sys.executable,str(scripts[-1]),str(source),'--compiler','tectonic','--output-directory',str(output),'--json'],capture_output=True,text=True)
try:
    d=json.loads(p.stdout);log='\n'.join(a.get('log','') for a in d.get('attempts',[]))
except Exception:log=p.stdout+p.stderr;d={}
output.mkdir(parents=True,exist_ok=True);(output/'compile_log.txt').write_text(log,encoding='utf-8')
print(json.dumps(dict(exit=p.returncode,pdf=d.get('pdfPath'),issues=[x for x in log.splitlines() if any(v in x for v in ('Overfull','Undefined control','error:','Misplaced','Output written','Output saved'))]),indent=2))
sys.exit(p.returncode)
