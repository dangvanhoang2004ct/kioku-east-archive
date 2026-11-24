from pathlib import Path
import json,base64,re,subprocess
root=Path(__file__).resolve().parent.parent
subprocess.run(['node', 'scripts/build.mjs'], cwd=root, check=True)
pages=['index','collection','finder','work','condition-guide','journal','about']
css=(root/'assets/site.css').read_text()+'\n'+(root/'assets/dragon-stage.css').read_text()
css=re.sub(r'@import[^\n]*\n','',css)
files={n:(root/n).read_text() for n in [
 'data/browser-storage.js','features/storefront/favorites.js','features/catalog/records.js','features/shared/site.js',
 'features/storefront/compare.js','features/storefront/catalog.js','features/storefront/detail.js',
 'features/discovery/finder.js','features/condition/notes.js']}

def src_data(s):
 for pattern,mime in [('*.webp','image/webp'),('*.svg','image/svg+xml')]:
  for p in (root/'assets/img').glob(pattern):
   s=s.replace('./assets/img/'+p.name,'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode())
 return s

def combined_js(page):
 names=['data/browser-storage.js','features/storefront/favorites.js','features/catalog/records.js','features/shared/site.js']
 if page=='collection':names.extend(['features/storefront/compare.js','features/storefront/catalog.js'])
 if page=='finder':names.append('features/discovery/finder.js')
 if page=='work':names.append('features/storefront/detail.js')
 if page=='condition-guide':names.append('features/condition/notes.js')
 js='\n'.join(re.sub(r'\bexport\s+(?=(?:const|function|class))','',re.sub(r'^import[^\n]*\n','',files[name],flags=re.M)) for name in names)
 js=js.replace('location.search','(window.KIOKU_PREVIEW_QUERY||location.search)')
 return src_data(js)

def page_html(page):
 s=(root/'dist'/(page+'.html')).read_text()
 s=re.sub(r'<link[^>]*rel="stylesheet"[^>]*>','',s)
 s=re.sub(r'<script type="module"[^>]*></script>','',s)
 for directory,prefix,suffix,mime in [(root/'assets/img','./assets/img/','*.webp','image/webp'),(root/'assets/img','./assets/img/','*.svg','image/svg+xml'),(root/'assets/icons','./assets/icons/','*.svg','image/svg+xml'),(root/'brand','./brand/','*.svg','image/svg+xml')]:
  for p in directory.glob(suffix):
   s=s.replace(prefix+p.name,'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode())
 intercept="""document.addEventListener('click',function(e){const link=e.target.closest('a[href]');if(!link)return;const href=link.getAttribute('href')||'';const match=href.match(/^\\.\\/(index|collection|finder|work|condition-guide|journal|about)\\.html(\\?[^#]*)?/);if(match){e.preventDefault();parent.postMessage({type:'kioku-nav',page:match[1],query:match[2]||''},'*');}});"""
 s=s.replace('</head>','<style>'+css+'</style></head>')
 s=s.replace('</body>','<script>'+combined_js(page)+intercept+'</script></body>')
 return s
payload={name:base64.b64encode(page_html(name).encode('utf-8')).decode('ascii') for name in pages}
controls=''.join(f'<button type="button" data-page="{n}">{t}</button>' for n,t in zip(pages,['Home','Collection','Finder','Detail','Condition','Journal','About']))
ui='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KIOKU V6 — Interactive Website Preview</title><style>*{box-sizing:border-box}body{margin:0;background:#142026;color:white;font:14px system-ui,Arial,sans-serif}.preview-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid #51616a}.preview-bar strong{letter-spacing:.11em}.preview-nav{display:flex;gap:5px;overflow:auto;max-width:100%}.preview-nav button{background:transparent;border:1px solid #657675;color:#f2f2ec;padding:9px 11px;font-size:12px;min-height:42px;white-space:nowrap;cursor:pointer}.preview-nav button.active{background:#eff0e9;color:#152527}.note{font-size:11px;opacity:.78}.frame{width:100%;border:0;height:calc(100vh - 67px);min-height:620px;display:block;background:#f3f1eb}@media(max-width:800px){.preview-bar{display:block}.preview-nav{margin:9px 0}.frame{height:calc(100vh - 116px)}.note{display:none}}</style></head><body><div class="preview-bar"><strong>KIOKU V6 / FUNCTIONAL DESIGN PREVIEW</strong><div class="preview-nav">__CONTROLS__</div><div class="note">Original editorial images / No live merchandise</div></div><iframe class="frame" id="kioku-frame" title="Interactive KIOKU website preview"></iframe><script>
const PAGES=__PAYLOAD__;
const frame=document.getElementById('kioku-frame');
function render(page='index',query=''){const bin=atob(PAGES[page]||PAGES.index);const bytes=Uint8Array.from(bin,c=>c.charCodeAt(0));let html=new TextDecoder().decode(bytes);html=html.replace('<script>',`<script>window.KIOKU_PREVIEW_QUERY=${JSON.stringify(query)};`);frame.srcdoc=html;document.querySelectorAll('[data-page]').forEach(b=>{const active=b.dataset.page===page;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});history.replaceState(null,'','#'+page);}
document.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>render(b.dataset.page,b.dataset.page==='work'?'?ref=ichiban-kuji':'')));
window.addEventListener('message',e=>{if(e.source!==frame.contentWindow)return;if(e.data?.type==='kioku-nav'&&Object.hasOwn(PAGES,e.data.page))render(e.data.page,e.data.query||'')});
render(Object.hasOwn(PAGES,location.hash.slice(1))?location.hash.slice(1):'index');
</script></body></html>'''.replace('__CONTROLS__',controls).replace('__PAYLOAD__',json.dumps(payload))
out=root/'KIOKU-V6-Interactive-Website-Preview.html';out.write_text(ui,encoding='utf-8')
print('Built standalone Kioku V6 preview',out.stat().st_size,'bytes for',len(pages),'routes')
