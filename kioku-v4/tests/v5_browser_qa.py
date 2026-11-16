from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
preview=(root/'KIOKU-V5-Interactive-Website-Preview.html').read_text()
report=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'] if Path('/usr/bin/chromium').exists() else [])
 for width in [320,375,390,768,1440]:
  page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(preview,wait_until='domcontentloaded',timeout=30000)
  frame=page.frame_locator('#kioku-frame')
  assert 'Hold the' in frame.locator('h1').first.inner_text(timeout=12000)
  page.wait_for_timeout(650)
  overflow=frame.locator('body').evaluate('e=>({doc:document.documentElement.scrollWidth,viewport:innerWidth})')
  assert overflow['doc'] <= overflow['viewport']+2,(width,'home overflow',overflow)
  bad=frame.locator('img').evaluate_all("(images)=>images.filter(x=>x.loading!=='lazy'&&(!x.complete||x.naturalWidth===0)).map(x=>x.outerHTML.slice(0,130))")
  assert not bad,(width,'images',bad)
  if width<=768:
   frame.locator('[data-menu-toggle]').click()
   assert frame.locator('nav.nav-links').evaluate('(e)=>e.classList.contains("is-open")')
   frame.locator('[data-menu-toggle]').click()
   assert not frame.locator('nav.nav-links').evaluate('(e)=>e.classList.contains("is-open")')
  frame.locator('[data-open-search]').click()
  frame.locator('[data-global-search]').fill('MegaHouse')
  assert frame.locator('.search-hit').count()>=2,('search',width)
  frame.locator('[data-close-search]').click()
  page.locator('[data-page="collection"]').click();page.wait_for_timeout(500)
  assert frame.locator('[data-grid] .catalog-card').count()==6
  frame.locator('[data-maker]').select_option('MegaHouse')
  assert frame.locator('[data-grid] .catalog-card').count()==3
  frame.locator('[data-maker]').select_option('')
  frame.locator('[data-search]').fill('G.E.M.')
  assert frame.locator('[data-grid] .catalog-card').count()==1
  frame.locator('[data-reset]').click()
  for b in frame.locator('[data-compare]').all()[:2]:b.click()
  assert frame.locator('[data-compare-bar]').is_visible()
  frame.locator('[data-open-compare]').click()
  assert frame.locator('[data-compare-dialog]').is_visible()
  assert frame.locator('.comparison-table tr').count()>=6
  frame.locator('[data-close-compare]').click()
  page.locator('[data-page="finder"]').click();page.wait_for_timeout(550)
  for field,value in [('maker','MegaHouse'),('style','portrait'),('box','flexible')]:frame.locator(f'input[name="{field}"][value="{value}"]').check()
  frame.locator('[data-finder-form] button[type=submit]').click()
  assert frame.locator('[data-finder-recommendations] a').count()>=2
  assert 'No-box' in frame.locator('[data-finder-box-guide]').inner_text() or 'no-box' in frame.locator('[data-finder-box-guide]').inner_text()
  page.locator('[data-page="condition-guide"]').click();page.wait_for_timeout(550)
  frame.locator('[data-condition-form] input[name=item]').fill('My figure')
  frame.locator('[data-condition-form] select[name=box]').select_option('No box')
  frame.locator('[data-condition-form] button[type=submit]').click()
  assert 'My figure' in frame.locator('[data-condition-output]').inner_text()
  assert 'No box' in frame.locator('[data-condition-output]').inner_text()
  page.locator('[data-page="work"]').click();page.wait_for_timeout(650)
  assert 'ICHIBAN KUJI' in frame.locator('.detail-copy h1').inner_text().upper()
  frame.locator('[data-zoom]').click()
  assert frame.locator('[data-lightbox]').is_visible()
  frame.locator('[data-zoom-close]').click()
  assert not frame.locator('[data-lightbox]').is_visible()
  assert not errors,(width,'page errors',errors)
  report.append({'width':width,'overflow':overflow,'errors':errors,'search':True,'filter':True,'compare':True,'finder':True,'condition':True,'detail':True})
  page.close()
 browser.close()
print(json.dumps(report,indent=2))
