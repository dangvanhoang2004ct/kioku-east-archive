const form=document.querySelector('[data-condition-form]'),out=document.querySelector('[data-condition-result]');
if(form){let last='';
const value=s=>String(s||'').replace(/[\r\n]+/g,' ').trim();
form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const v=Object.fromEntries(new FormData(form).entries());
 last=[`MY COLLECTION CONDITION NOTE`,`Item: ${value(v.item)}`,`Maker: ${value(v.maker)}`,`Figure: ${value(v.figure)}`,`Box: ${value(v.box)}`,`Accessories: ${value(v.accessories)}`,`Observed defects: ${value(v.defects)}`,`Other observations: ${value(v.notes)||'No notes entered'}`,'','Personal visual checklist only. Not authenticated, certified or submitted to KIOKU.'].join('\n');
 out.querySelector('[data-condition-output]').textContent=last;out.hidden=false;out.querySelector('[data-condition-feedback]').textContent='Draft generated locally. No information was sent.';
});
form.addEventListener('reset',()=>{out.hidden=true;last=''});
out.querySelector('[data-copy-condition]').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(last);out.querySelector('[data-condition-feedback]').textContent='Notes copied.'}catch{out.querySelector('[data-condition-feedback]').textContent='Select the text above to copy it manually.'}});
out.querySelector('[data-download-condition]').addEventListener('click',()=>{const blob=new Blob([last],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='kioku-personal-condition-note.txt';a.click();URL.revokeObjectURL(url);out.querySelector('[data-condition-feedback]').textContent='Text file created on this device.'});
}
