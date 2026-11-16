import {readFileSync,existsSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
const root=resolve(import.meta.dirname,'..'),file=join(root,'features/inventory/verified-items.json');
const items=JSON.parse(readFileSync(file,'utf8'));
if(!Array.isArray(items))throw Error('verified-items.json must be an array');
const ids=new Set();
const required=['id','model_id','manufacturer','product_line','series','character','figure_condition','box_condition','accessories','missing_parts','observed_defects','photos','photo_rights','inspection_evidence','status'];
const validStatuses=new Set(['draft','awaiting_review','approved_for_catalog']);
for(const item of items){
 if(!item||typeof item!=='object')throw Error('Inventory record must be an object');
 for(const key of required)if(!(key in item))throw Error(`Item ${item.id||'<unnamed>'} missing ${key}`);
 if(typeof item.id!=='string'||!(/^[a-z0-9][a-z0-9-]{3,90}$/.test(item.id)))throw Error('Inventory id must be URL-safe');
 if(ids.has(item.id))throw Error('Duplicate item id '+item.id);ids.add(item.id);
 if(!validStatuses.has(item.status))throw Error('Unrecognized stock approval status');
 for(const field of ['accessories','missing_parts','observed_defects','photos'])if(!Array.isArray(item[field]))throw Error(`Item ${item.id}: ${field} must be an array`);
 if(item.status==='approved_for_catalog'){
   if(!item.photos.length||!item.inspection_evidence||!item.photo_rights)throw Error(`${item.id}: missing approved photos/inspection evidence`);
   if(!Number.isFinite(item.price)||item.price<=0||!item.currency||!Number.isInteger(item.quantity)||item.quantity<0)throw Error(`${item.id}: approved item lacks verified price/currency/quantity`);
   if(!item.shipping_origin||!item.policy_ref)throw Error(`${item.id}: approved item lacks shipping origin/policy reference`);
 }
 for(const photo of item.photos){if(typeof photo!=='string'||!photo.startsWith('assets/items/')||photo.includes('..')||!existsSync(join(root,photo)))throw Error(`${item.id}: missing/unsafe photo ${photo}`)}
}
console.log(`Verified inventory schema checked: ${items.length} physical item records (${items.filter(x=>x.status==='approved_for_catalog').length} approved)`);
