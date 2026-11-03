import { NextResponse } from 'next/server';
import { modAuth } from '../../../../lib/mod-auth';
export const runtime='nodejs';
const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export async function POST(request:Request){
 const session=await modAuth(request);if(!session)return NextResponse.json({error:'Nicht angemeldet'},{status:401});
 try{
  const b=await request.json();
  if(![b.eventId,b.chestId,b.itemId].every(v=>typeof v==='string'&&UUID.test(v))||
     !Number.isSafeInteger(b.amount)||b.amount<1||b.amount>2304)
    return NextResponse.json({error:'Ungültige Lieferung'},{status:400});
  const {data,error}=await session.supabase.rpc('record_mod_delivery',{
   p_event_id:b.eventId,p_chest_id:b.chestId,p_item_id:b.itemId,p_amount:b.amount
  });
  if(error)return NextResponse.json({error:error.message},{status:400});
  return NextResponse.json({status:data},{headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({error:'Ungültige Anfrage'},{status:400});}
}
