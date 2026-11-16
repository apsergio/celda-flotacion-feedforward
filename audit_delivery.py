"""Auditoría portable de archivos, imports y datos excluidos de una entrega."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
EXCLUDED={'.git','.venv','__pycache__','.pytest_cache','outputs','work'}
PATTERNS={
    'ruta_personal':r'(?i)(?:[A-Z]:[\\/]+Users[\\/]|/home/|/Users/)',
    'token_github':r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'clave_privada':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'access_key':r'AKIA[A-Z0-9]{16}',
}

def portable_junit(path):
    """Conserva resultados y elimina metadatos del equipo y logs con rutas."""
    tree=ET.parse(path)
    for elem in tree.iter():
        elem.attrib.pop('hostname',None)
        if 'file' in elem.attrib:
            elem.attrib['file']=elem.attrib['file'].replace('\\','/').split('/tests/')[-1]
        for child in list(elem):
            if child.tag in ('system-out','system-err'): elem.remove(child)
    tree.write(path,encoding='utf-8',xml_declaration=True)

def audit(root=ROOT):
    paths=[p for p in root.rglob('*') if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts)]
    issues=[]; files=[]; imports=set()
    for p in sorted(paths):
        rel=p.relative_to(root).as_posix()
        if rel=='validation/audit_inventory.json': continue
        if p.suffix in ('.zip','.bundle','.pyc') or p.name in ('secrets.toml','.env'):
            issues.append({'file':rel,'issue':'archivo excluido de distribución'})
        raw=p.read_bytes()
        text=raw.decode('utf-8',errors='replace')
        # El auditor contiene expresiones de detección, nunca credenciales reales.
        if p.name!='audit_delivery.py':
            for label,pattern in PATTERNS.items():
                if re.search(pattern,text): issues.append({'file':rel,'issue':label})
        if p.suffix=='.py':
            for node in ast.walk(ast.parse(text,filename=rel)):
                names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
                imports.update(n.split('.')[0] for n in names)
        files.append({'file':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    missing=[name for name in sorted(imports) if importlib.util.find_spec(name) is None]
    for rel in ('app.py','model.py','ui_modules.py','methodology.py','presentation.py','requirements.txt',
                'README.md','docs/MANUAL.md','docs/METODOLOGIA.md','docs/DICTAMEN_REPLICACION.md',
                'data/fig12_digitized.csv','.streamlit/config.toml'):
        if not (root/rel).is_file(): issues.append({'file':rel,'issue':'archivo requerido ausente'})
    return {'schema':1,'file_count':len(files),'files':files,'import_roots':sorted(imports),
            'missing_imports':missing,'issues':issues,'ok':not issues and not missing}

if __name__=='__main__':
    if '--sanitize-junit' in sys.argv:
        for path in (ROOT/'validation').glob('junit*.xml'): portable_junit(path)
    result=audit()
    (ROOT/'validation/audit_inventory.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2,ensure_ascii=False))
    raise SystemExit(0 if result['ok'] else 1)
