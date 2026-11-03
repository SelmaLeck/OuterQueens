import { NextResponse } from 'next/server';
import { modAuth } from '../../../../lib/mod-auth';
export const runtime='nodejs';
export async function POST(request:Request){
 const session=await modAuth(request);if(!session)return NextResponse.json({error:'Nicht angemeldet'},{status:401});
 try {
  const b=await request.json();
  if(typeof b.serverId!=='string'||typeof b.dimension!=='string'||typeof b.label!=='string'||
    ![b.x,b.y,b.z].every(v=>Number.isSafeInteger(v))) return NextResponse.json({error:'Ungültige Koordinaten'},{status:400});
  const {data,error}=await session.supabase.rpc('register_mod_chest',{
    p_server_id:b.serverId,p_dimension:b.dimension,p_x:b.x,p_y:b.y,p_z:b.z,p_label:b.label
  });
  if(error)return NextResponse.json({error:error.message},{status:400});
  return NextResponse.json({chestId:data});
 }catch{return NextResponse.json({error:'Ungültige Anfrage'},{status:400});}
}
