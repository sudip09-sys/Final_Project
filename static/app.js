'use strict';
const $ = s => document.querySelector(s);
let state = {people: [], sessions: [], attendance: []};
let selected = sessionStorage.getItem('selectedSession') || '';
let stream = null;
let enrollmentImage = null;
const csrf = $('meta[name="csrf-token"]').content;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const initials = n => n.split(/\s+/).slice(0,2).map(x=>x[0]).join('').toUpperCase();
const clock = d => new Date(d).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
function notify(message, error=false) { $('#notice').textContent=message; $('#notice').hidden=false; $('#notice').className='notice'+(error?' error':''); }
async function api(url, data) {
  const response = await fetch(url, data ? {method:'POST',body:data,headers:{'X-CSRF-Token':csrf}} : {});
  if (response.status===401) { location.href='/login'; throw new Error('Please sign in again.'); }
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Request failed.');
  return result;
}
function fields(obj) { const f=new FormData(); for(const [k,v] of Object.entries(obj)) f.append(k,v); return f; }
async function refresh() {
  state=await api('/api/state');
  if(!state.sessions.some(s=>String(s.id)===selected)) selected=String(state.sessions.find(s=>s.is_open)?.id || '');
  $('#active-session').innerHTML='<option value="">Choose a session</option>'+state.sessions.map(s=>`<option value="${s.id}" ${String(s.id)===selected?'selected':''}>${esc(s.title)} · ${esc(s.cohort)}${s.is_open?'':' (closed)'}</option>`).join('');
  render();
}
function render() {
  const cls=state.sessions.find(s=>String(s.id)===selected);
  const roster=state.people.filter(p=>p.cohort===cls?.cohort);
  const entries=state.attendance.filter(a=>String(a.session_id)===selected);
  const checked=new Map(entries.map(a=>[a.person_id,a]));
  $('#stat-students').textContent=state.people.length;
  $('#stat-face').textContent=state.people.filter(p=>p.has_face).length;
  $('#stat-present').textContent=entries.length;
  $('#stat-waiting').textContent=roster.filter(p=>!checked.has(p.id)).length;
  $('#stat-session').textContent=cls?.title || 'Choose a class session';
  $('#activity-subtitle').textContent=cls?cls.title+(cls.is_open?' · Open':' · Closed'):'Your latest check-ins appear here.';
  $('#register-subtitle').textContent=cls?`${cls.cohort} · ${roster.length} students`:'Choose a session to see its roster.';
  $('#activity-list').innerHTML=entries.slice(0,5).map(a=>`<div class="activity-row"><span class="avatar">${esc(initials(a.name))}</span><div><p>${esc(a.name)}</p><small>${esc(a.student_id)} · ${a.method==='face'?'Face recognized':'Manual check-in'}</small></div><span class="activity-time">${esc(clock(a.at))}</span></div>`).join('') || '<p class="empty">No check-ins yet.<br>Your first arrival will appear here.</p>';
  $('#register-body').innerHTML=roster.map(p=>{const a=checked.get(p.id);return `<tr><td><span class="student-cell"><span class="avatar">${esc(initials(p.name))}</span>${esc(p.name)}</span></td><td>${esc(p.student_id)}</td><td><span class="status ${a?'':'unmarked'}">${a?'Present':'Unmarked'}</span></td><td>${a?esc(clock(a.at)):'—'}</td><td>${a?esc(a.method):'—'}</td></tr>`;}).join('') || '<tr><td colspan="5" class="empty">Add students and open a session for their cohort to get started.</td></tr>';
  renderStudents();
  $('#session-list').innerHTML=state.sessions.map(s=>`<div class="session-row"><div><p>${esc(s.title)}</p><small>${esc(s.cohort)} · ${s.is_open?'Open':'Closed'}</small></div><div class="actions"><button class="row-action" data-select="${s.id}">View</button>${s.is_open?`<button class="row-action danger" data-close-session="${s.id}">Close</button>`:''}</div></div>`).join('') || '<p class="empty">No class sessions yet.</p>';
  $('#capture').disabled=!stream || !cls?.is_open;
}
function renderStudents(){
  const query=$('#search').value.toLowerCase();
  $('#students-body').innerHTML=state.people.filter(p=>(p.name+' '+p.student_id).toLowerCase().includes(query)).map(p=>`<tr><td><span class="student-cell"><span class="avatar">${esc(initials(p.name))}</span>${esc(p.name)}</span></td><td>${esc(p.student_id)}</td><td>${esc(p.cohort)}</td><td><span class="status ${p.has_face?'':'unmarked'}">${p.has_face?'Enrolled':'Manual only'}</span></td><td>${p.has_face?`<button class="row-action" data-withdraw="${p.id}">Remove face</button>`:''}<button class="row-action danger" data-delete="${p.id}">Delete student</button></td></tr>`).join('') || '<tr><td colspan="5" class="empty">No matching students.</td></tr>';
}
function view(name) {
  document.querySelectorAll('.view').forEach(el=>el.hidden=el.id!=='view-'+name);
  document.querySelectorAll('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===name));
  const titles={overview:['Overview','Your classroom, at a glance.','Open a session, welcome your students, and let class begin.'],students:['Students','A place for everyone.','Enroll participants with consent, or use manual attendance.'],sessions:['Class sessions','Every class starts here.','Open a session for a cohort and keep its attendance together.']};
  $('#breadcrumb').textContent=titles[name][0]; $('#page-title').textContent=titles[name][1]; $('#page-subtitle').textContent=titles[name][2];
}
async function imageFrame() {
  if(!stream || !$('#camera').videoWidth) throw new Error('Start the camera in the check-in station first.');
  const canvas=$('#canvas'), video=$('#camera'); canvas.width=video.videoWidth; canvas.height=video.videoHeight;
  canvas.getContext('2d').drawImage(video,0,0); return new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.88));
}
function stopCamera(){if(stream) stream.getTracks().forEach(t=>t.stop()); stream=null; $('#camera').srcObject=null;$('#camera').hidden=true;$('#camera-placeholder').hidden=false;$('#start-camera').hidden=false;$('#stop-camera').hidden=true;$('#camera-status').textContent='Camera off';$('#camera-status').className='tag';render();}
$('#start-camera').addEventListener('click',async()=>{try{if(!navigator.mediaDevices) throw new Error('Camera requires HTTPS or localhost. You can also upload an image.');stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:960},facingMode:'user'},audio:false});$('#camera').srcObject=stream;await $('#camera').play();$('#camera').hidden=false;$('#camera-placeholder').hidden=true;$('#start-camera').hidden=true;$('#stop-camera').hidden=false;$('#camera-status').textContent='Camera live';$('#camera-status').className='tag live';render();}catch(e){notify('Camera unavailable: '+e.message,true);}});
$('#stop-camera').addEventListener('click',stopCamera);window.addEventListener('pagehide',stopCamera);
$('#capture').addEventListener('click',async()=>{const button=$('#capture');button.disabled=true;try{const data=fields({session_id:selected});data.append('image',await imageFrame(),'capture.jpg');const r=await api('/api/recognize',data);notify(r.message);await refresh();}catch(e){notify(e.message,true);}finally{render();}});
$('#capture-enrollment').addEventListener('click',async()=>{try{enrollmentImage=await imageFrame();$('#enrollment-capture-status').textContent='Camera frame captured for enrollment.';$('#enroll-image').value='';}catch(e){$('#enrollment-capture-status').textContent=e.message;}});
$('#enroll-image').addEventListener('change',()=>{enrollmentImage=null;$('#enrollment-capture-status').textContent='';});
$('#recognize-form').addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,button=form.querySelector('button');button.disabled=true;try{const data=new FormData(form);data.append('session_id',selected);const r=await api('/api/recognize',data);notify(r.message);await refresh();}catch(e){notify(e.message,true);}finally{button.disabled=false;}});
for(const [id,url] of [['enroll-form','/api/people'],['session-form','/api/sessions'],['manual-form','/api/manual']]){
  $('#'+id).addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,button=form.querySelector('button.primary'),error=form.querySelector('.form-error');button.disabled=true;if(error)error.textContent='';try{const data=new FormData(form);if(id==='manual-form')data.append('session_id',selected);if(id==='enroll-form'&&enrollmentImage)data.set('image',enrollmentImage,'enroll.jpg');const r=await api(url,data);if(id==='session-form')selected=String(r.id);form.reset();enrollmentImage=null;$('#enrollment-capture-status').textContent='';form.closest('dialog')?.close();notify(r.message);await refresh();}catch(e){if(error)error.textContent=e.message;else notify(e.message,true);}finally{button.disabled=false;}});
}
$('#open-enroll').addEventListener('click',()=>$('#enroll-dialog').showModal());$('#open-manual').addEventListener('click',()=>$('#manual-dialog').showModal());
document.addEventListener('click',async event=>{const b=event.target.closest('button');if(!b)return;if(b.dataset.view)view(b.dataset.view);if(b.dataset.close)$('#'+b.dataset.close).close();if(b.dataset.select){selected=b.dataset.select;$('#active-session').value=selected;sessionStorage.setItem('selectedSession',selected);render();view('overview');}let url='',prompt='';if(b.dataset.withdraw){url=`/api/people/${b.dataset.withdraw}/withdraw`;prompt='Remove this face template? Manual attendance and past records remain.';}if(b.dataset.delete){url=`/api/people/${b.dataset.delete}/delete`;prompt='Delete this student, their face template and all their attendance records? This cannot be undone.';}if(b.dataset.closeSession){url=`/api/sessions/${b.dataset.closeSession}/close`;prompt='Close this session? Further check-ins will be blocked.';}if(url&&confirm(prompt)){try{const r=await api(url,new FormData());notify(r.message);await refresh();}catch(e){notify(e.message,true);}}});
$('#active-session').addEventListener('change',e=>{selected=e.target.value;sessionStorage.setItem('selectedSession',selected);render();});$('#search').addEventListener('input',renderStudents);$('#refresh').addEventListener('click',()=>refresh().catch(e=>notify(e.message,true)));$('#export').addEventListener('click',()=>{if(!selected)return notify('Choose a session first.',true);location.href='/api/export?session_id='+encodeURIComponent(selected);});refresh().catch(e=>notify(e.message,true));

$('#enroll-dialog').addEventListener('close',()=>{enrollmentImage=null;$('#enroll-form').reset();$('#enrollment-capture-status').textContent='';$('#enroll-form .form-error').textContent='';});
