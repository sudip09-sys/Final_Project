import io,json,sys,time,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
parser=argparse.ArgumentParser(description='Optional real-model smoke test with two provided public fixture photos')
parser.add_argument('face',type=Path)
parser.add_argument('other',type=Path)
args=parser.parse_args()
from PIL import Image,ImageEnhance
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash
from app import create_app
from recognition import encode_image,nearest
face=args.face.read_bytes()
other=args.other.read_bytes()
image=Image.open(io.BytesIO(face)).convert('RGB')
b=io.BytesIO();ImageEnhance.Brightness(image).enhance(.85).save(b,format='JPEG')
variation=b.getvalue()
blank=io.BytesIO();Image.new('RGB',(500,500),'white').save(blank,format='PNG')
multi=Image.new('RGB',(image.width*2,image.height));multi.paste(image,(0,0));multi.paste(image,(image.width,0));buf=io.BytesIO();multi.save(buf,format='JPEG')
results={}
start=time.perf_counter();v=encode_image(face);results['encoding_seconds']=round(time.perf_counter()-start,3)
results['embedding_dimensions']=len(v)
results['changed_brightness_match']=nearest(encode_image(variation),[(1,v)])[0]==1
results['different_person_rejected']=nearest(encode_image(other),[(1,v)])[0] is None
for name,raw in [('blank',blank.getvalue()),('two_faces',buf.getvalue()),('corrupt',b'invalid')]:
 try:encode_image(raw);results[name+'_rejected']=False
 except ValueError as e:results[name+'_rejected']=True;results[name+'_message']=str(e)
app=create_app(dict(TESTING=True, SECRET_KEY='real-model-test',EMBEDDING_KEY=Fernet.generate_key().decode(),ADMIN_PASSWORD_HASH=generate_password_hash('test-password'),DATABASE_URL='sqlite:///:memory:'))
c=app.test_client();c.get('/login')
with c.session_transaction() as s:token=s['csrf']
c.post('/login',data={'csrf':token,'password':'test-password'})
def post(url,data):
 with c.session_transaction() as s:token=s['csrf']
 return c.post(url,data=data,headers={'X-CSRF-Token':token})
r=post('/api/people',dict(student_id='FIXTURE-1',name='Public image test fixture',cohort='Test',consent='yes',image=(io.BytesIO(face),'face.jpg')));assert r.status_code==201,r.text
sid=post('/api/sessions',dict(title='Model integration test',cohort='Test')).json['id']
r=post('/api/recognize',dict(session_id=sid,image=(io.BytesIO(variation),'changed.jpg')));assert r.status_code==201,r.text
results['real_enrollment_to_attendance']='PASS'
results['distance_for_brightness_variation']=round(r.json['distance'],5)
r=post('/api/recognize',dict(session_id=sid,image=(io.BytesIO(other),'other.jpg')));assert r.status_code==422,r.text
results['real_unknown_api_rejection']='PASS'
assert all(v for k,v in results.items() if k.endswith('_rejected') or k.endswith('_match'))
results['scope']='Two public image fixtures, one brightness variation. Functional smoke tests only, not accuracy or demographic validation.'
(root/'docs/evidence/model-smoke.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
