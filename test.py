"""ShelfTrack smoke test: python3 test.py  (needs playwright + Chrome). Writes screenshot.png and mobile.png."""
from playwright.sync_api import sync_playwright
import os, json, re, tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); SRC=open(os.path.join(HERE,'index.html'),encoding='utf-8').read()
URL='file://'+os.path.join(HERE,'index.html')
p=sync_playwright().start();b=p.chromium.launch(executable_path='/usr/bin/google-chrome')

def page(vp=(1280,900),touch=False):
    ctx=b.new_context(viewport={'width':vp[0],'height':vp[1]},has_touch=touch,is_mobile=touch)
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text));return pg,errs

# ---- core tracker (desktop)
pg,errs=page();pg.on('dialog',lambda d:d.accept());pg.goto(URL)
assert pg.text_content('#sCount')=='2'
assert 'Free action figure collection tracker' in pg.get_attribute('meta[name=description]','content')
pg.click('#addBtn');assert pg.evaluate("document.activeElement.name")=='name','focus not on Name'
pg.keyboard.press('Escape');assert not pg.is_visible('#modal .card');assert pg.evaluate("document.activeElement.id")=='addBtn'
pg.click('#addBtn');pg.mouse.click(5,5);assert not pg.is_visible('#modal .card'),'backdrop close'
pg.click('#addBtn');pg.fill('[name=name]','   ');pg.click('#saveBtn');assert pg.is_visible('#modal .card'),'blank name saved';assert pg.text_content('#sCount')=='2'
pg.fill('[name=name]','Boba Fett');pg.fill('[name=line]','Star Wars Black Series');pg.fill('[name=paid]','25');pg.fill('[name=value]','60');pg.click('#saveBtn')
assert pg.text_content('#sCount')=='3', pg.text_content('#sCount')
assert pg.text_content('#sGain')=='+$42', pg.text_content('#sGain')
pg.fill('#q','boba');assert pg.locator('#tbody tr').count()==1
assert pg.get_attribute('[data-edit]','aria-label')=='Edit Boba Fett' and pg.get_attribute('[data-del]','aria-label')=='Delete Boba Fett'
pg.fill('#q','')
pg.click('[data-edit]');pg.fill('[name=value]','30');pg.click('#saveBtn')
pg.locator('[data-del]').last.click()
assert pg.text_content('#sCount')=='2'
n=pg.evaluate("ShelfTrack.importCSV('name,line,paid,value,list\\n\"He-Man, Origins\",MOTU,15,20,owned\\nGrogu,SW,,30,wish')");assert n==2
pg.click('[data-tab=wish]');assert pg.locator('#tbody tr').count()==2
assert pg.get_attribute('[data-tab=wish]','aria-pressed')=='true' and pg.get_attribute('[data-tab=owned]','aria-pressed')=='false'
pg.click('[data-tab=owned]')
# re-import own export: no duplicates
before=pg.evaluate("ShelfTrack.figs.length");n=pg.evaluate("ShelfTrack.importCSV(ShelfTrack.toCSV())");assert n==0 and pg.evaluate("ShelfTrack.figs.length")==before,(n,before)
# sanitising: $12 -> 12, abc -> skipped, blank name skipped
n=pg.evaluate("ShelfTrack.importCSV('name,paid,value\\nRobin,$12,\"1,050\"\\nBad,abc,5\\n   ,3,3')");li=pg.evaluate("ShelfTrack.lastImport")
assert n==1 and li['skipped']==2,(n,li);rb=pg.evaluate("ShelfTrack.figs.find(f=>f.name==='Robin')");assert rb['paid']==12 and rb['value']==1050,rb
# formula injection
pg.evaluate("ShelfTrack.importCSV('name,line\\n=HYPERLINK(1),@x')");csv=pg.evaluate("ShelfTrack.toCSV()");assert "\"'=HYPERLINK(1)\"" in csv and "\"'@x\"" in csv
n=pg.evaluate("ShelfTrack.importCSV(ShelfTrack.toCSV())");assert n==0
assert pg.evaluate("ShelfTrack.figs.some(f=>f.name==='=HYPERLINK(1)')"),'round-trip strip'
# replace mode
cnt=pg.evaluate("ShelfTrack.importCSV('name\\nOnly One','replace')");assert cnt==1 and pg.evaluate("ShelfTrack.figs.length")==1
# import button is keyboard reachable and opens merge/replace dialog
assert pg.evaluate("document.querySelector('#impBtn').tagName")=='BUTTON'
tmp=tempfile.NamedTemporaryFile('w',suffix='.csv',delete=False);tmp.write('name\nFoo\n');tmp.close()
with pg.expect_file_chooser() as fc: pg.click('#impBtn')
fc.value.set_files(tmp.name);pg.wait_for_selector('#impModal.on');pg.click('#iMerge');pg.wait_for_function("ShelfTrack.figs.length===2")
# waitlist: endpoint empty -> honest message, nothing stored, no network
reqs=[];pg.on('request',lambda r:r.url.startswith('http') and reqs.append(r.url))
pg.fill('#waitEmail','a@b.com');pg.click('#waitBtn')
assert 'opening soon' in pg.text_content('#waitMsg').lower(); assert "on the list" not in pg.text_content('#waitMsg')
assert pg.evaluate("localStorage.getItem('shelftrack.waitlist')") is None and not reqs
pg.reload();assert pg.text_content('#sCount')=='2'
# photo placeholder / broken url
pg.evaluate("ShelfTrack.importCSV('name,photo\\nPic,http://127.0.0.1:9/nope.png')");pg.wait_for_timeout(500)
assert pg.locator('#tbody img').count()==0 and pg.locator('#tbody .ph').count()>=3
errs[:]=[e for e in errs if 'ERR_CONNECTION_REFUSED' not in e and 'Failed to load resource' not in e]
# corrupt storage does not blank the app
pg.evaluate("localStorage.setItem('shelftrack.figures','{bad json')");pg.reload();assert pg.text_content('#sCount')=='2'
assert not errs, errs
pg.evaluate("localStorage.clear()");pg.reload();pg.screenshot(path=os.path.join(HERE,'screenshot.png'),full_page=True)
print('core OK')

# ---- waitlist with endpoint set (mocked): 2xx success, 500 error
for status,expect in [(200,"on the list"),(500,"didn't go through")]:
    d=tempfile.mkdtemp();f=os.path.join(d,'index.html')
    open(f,'w',encoding='utf-8').write(SRC.replace("const WAITLIST_ENDPOINT = '';","const WAITLIST_ENDPOINT = 'https://formspree.io/f/test';"))
    pg,errs=page();got=[]
    pg.route('https://formspree.io/**',lambda r:(got.append(r.request.post_data),r.fulfill(status=status,body='{}',content_type='application/json')))
    pg.goto('file://'+f);pg.fill('#waitEmail','x@y.com');pg.click('#waitBtn');pg.wait_for_function("!document.querySelector('#waitMsg').textContent.includes('Sending')")
    m=pg.text_content('#waitMsg');assert expect in m,(status,m);assert got and json.loads(got[0])['email']=='x@y.com'
    stored=pg.evaluate("localStorage.getItem('shelftrack.waitlist')");assert (stored is not None)==(status==200)
print('waitlist endpoint OK')

# ---- mobile 390
pg,errs=page((390,844),touch=True);pg.goto(URL)
sw=pg.evaluate("document.documentElement.scrollWidth");assert sw<=390,('scrollWidth',sw)
pg.click('[data-tab=wish]');assert pg.evaluate("document.documentElement.scrollWidth")<=390
pg.click('[data-tab=owned]');pg.click('#addBtn')
for s in ['#saveBtn','#cancel']:
    bb=pg.locator(s).bounding_box();assert bb['x']>=0 and bb['x']+bb['width']<=390 and bb['y']+bb['height']<=844,(s,bb)
pg.screenshot(path=os.path.join(HERE,'mobile-modal.png'))
pg.click('#cancel');sizes=pg.evaluate("[...document.querySelectorAll('.btn,nav a')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.textContent.trim(),Math.round(r.width),Math.round(r.height)]}).filter(x=>x[1]<44||x[2]<44)")
assert not sizes,sizes
pg.screenshot(path=os.path.join(HERE,'mobile.png'),full_page=True)
assert not errs,errs
print('mobile OK: scrollWidth',sw)
print('ALL OK');b.close();p.stop()
