import {NextResponse} from 'next/server';
import {createClient} from '@supabase/supabase-js';
export const runtime='nodejs';
export async function PATCH(request:Request){
 try{
  const url=process.env.NEXT_PUBLIC_SUPABASE_URL;
  const pub=process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  const secret=process.env.SUPABASE_SERVICE_ROLE_KEY;
  if(!url||!pub||!secret)return NextResponse.json({error:'Server-Konfiguration fehlt.'},{status:503});
  const token=request.headers.get('authorization')?.match(/^Bearer (.+)$/i)?.[1];
  if(!token)return NextResponse.json({error:'Nicht angemeldet.'},{status:401});
  const publicClient=createClient(url,pub,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:who,error:authError}=await publicClient.auth.getUser(token);
  if(authError||!who.user)return NextResponse.json({error:'Sitzung abgelaufen.'},{status:401});
  const body=await request.json().catch(()=>null);
  const targetId=String(body?.userId??'');
  const role=body?.role;
  if(!/^[0-9a-f-]{36}$/i.test(targetId)||!['builder','farmer'].includes(role))return NextResponse.json({error:'Ungültige Angaben.'},{status:400});
  const admin=createClient(url,secret,{auth:{persistSession:false,autoRefreshToken:false}});
  if(targetId!==who.user.id){
   const {data:profile}=await admin.from('profiles').select('is_admin').eq('id',who.user.id).single();
   if(!profile?.is_admin)return NextResponse.json({error:'Du kannst nur deine eigene Rolle ändern.'},{status:403});
  }
  const {data,error}=await admin.from('profiles').update({team_role:role}).eq('id',targetId).select('id').single();
  if(error||!data)return NextResponse.json({error:'Rolle konnte nicht gespeichert werden.'},{status:400});
  return NextResponse.json({ok:true});
 } catch {return NextResponse.json({error:'Anfrage fehlgeschlagen.'},{status:400});}
}
