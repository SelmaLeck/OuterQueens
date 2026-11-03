import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
export const runtime='nodejs';
export async function POST(request:Request){
  try {
    const body=await request.json();
    if(typeof body.refreshToken!=='string'||body.refreshToken.length<12||body.refreshToken.length>4096)
      return NextResponse.json({error:'Ungültiger Token'},{status:400});
    const url=process.env.NEXT_PUBLIC_SUPABASE_URL,key=process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if(!url||!key)return NextResponse.json({error:'Nicht konfiguriert'},{status:500});
    const auth=createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});
    const {data,error}=await auth.auth.refreshSession({refresh_token:body.refreshToken});
    if(error||!data.session)return NextResponse.json({error:'Sitzung abgelaufen'},{status:401});
    return NextResponse.json({accessToken:data.session.access_token,refreshToken:data.session.refresh_token},{headers:{'Cache-Control':'no-store'}});
  }catch{return NextResponse.json({error:'Ungültige Anfrage'},{status:400});}
}
