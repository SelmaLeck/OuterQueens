import {NextResponse} from 'next/server';
import {createClient} from '@supabase/supabase-js';

export const runtime = 'nodejs';
const pattern = /^[A-Za-z0-9_]{2,20}$/;
const usernameEmail = (name:string)=>`${name.toLowerCase()}@players.blockforge.invalid`;

export async function POST(request:Request){
 try {
  const url=process.env.NEXT_PUBLIC_SUPABASE_URL;
  const pub=process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  const secret=process.env.SUPABASE_SERVICE_ROLE_KEY;
  if(!url||!pub||!secret)return NextResponse.json({error:'Server-Konfiguration fehlt (SUPABASE_SERVICE_ROLE_KEY).'}, {status:503});
  const token=request.headers.get('authorization')?.match(/^Bearer (.+)$/i)?.[1];
  if(!token)return NextResponse.json({error:'Nicht angemeldet.'},{status:401});
  const authClient=createClient(url,pub,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:who,error:authError}=await authClient.auth.getUser(token);
  if(authError||!who.user)return NextResponse.json({error:'Sitzung abgelaufen.'},{status:401});
  const admin=createClient(url,secret,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:profile,error:profileError}=await admin.from('profiles').select('is_admin').eq('id',who.user.id).single();
  if(profileError||!profile?.is_admin)return NextResponse.json({error:'Nur Admins dürfen Accounts anlegen.'},{status:403});
  const body=await request.json().catch(()=>null);
  const username=String(body?.username??'').trim();
  const password=String(body?.password??'');
  const role=body?.role;
  if(!pattern.test(username))return NextResponse.json({error:'Username: 2–20 Buchstaben, Zahlen oder _.'},{status:400});
  if(password.length<12||password.length>128)return NextResponse.json({error:'Passwort muss 12–128 Zeichen haben.'},{status:400});
  if(role!=='builder'&&role!=='farmer')return NextResponse.json({error:'Ungültige Team-Rolle.'},{status:400});
  const {data:existing}=await admin.from('profiles').select('id').ilike('username',username).limit(1);
  if(existing?.length)return NextResponse.json({error:'Username ist bereits vergeben.'},{status:409});
  const {data:created,error:createError}=await admin.auth.admin.createUser({
   email:usernameEmail(username),password,email_confirm:true,
   user_metadata:{username:username.toLowerCase(),display_name:username}
  });
  if(createError||!created.user)return NextResponse.json({error:createError?.message||'Account konnte nicht erstellt werden.'},{status:400});
  // Der vorhandene auth.users-Trigger erzeugt das Profil automatisch.
  const {error:roleError}=await admin.from('profiles').update({team_role:role}).eq('id',created.user.id);
  if(roleError)return NextResponse.json({error:'Account angelegt, aber Rolle konnte nicht gespeichert werden. Bitte Rolle im Team-Tab ändern.'},{status:500});
  return NextResponse.json({ok:true,username:username.toLowerCase()},{status:201});
 } catch {return NextResponse.json({error:'Anfrage konnte nicht verarbeitet werden.'},{status:400});}
}
