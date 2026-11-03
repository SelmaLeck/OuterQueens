import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { usernameLoginEmail } from '../../../../lib/username';
export const runtime = 'nodejs';
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const email = typeof body.username === 'string' ? usernameLoginEmail(body.username) : null;
    if (!email || typeof body.password !== 'string' || body.password.length > 256) {
      return NextResponse.json({error:'Ungültiger Login'}, {status:400});
    }
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!url || !key) return NextResponse.json({error:'Server nicht konfiguriert'}, {status:500});
    const client = createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});
    const {data,error}=await client.auth.signInWithPassword({email,password:body.password});
    if(error || !data.session) return NextResponse.json({error:'Login fehlgeschlagen'}, {status:401});
    return NextResponse.json({accessToken:data.session.access_token, refreshToken:data.session.refresh_token, expiresIn:data.session.expires_in},
      {headers:{'Cache-Control':'no-store'}});
  } catch {return NextResponse.json({error:'Ungültige Anfrage'}, {status:400});}
}
