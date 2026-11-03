import { NextResponse } from 'next/server';
import { modAuth } from '../../../../lib/mod-auth';
export const runtime='nodejs';
export async function GET(request:Request){
 const session=await modAuth(request);
 if(!session) return NextResponse.json({error:'Nicht angemeldet'}, {status:401});
 const {supabase,user}=session;
 const [items,contributions,chests]=await Promise.all([
   supabase.from('items').select('id,name_de,name_en,required,stack_size').order('required',{ascending:false}),
   supabase.from('contributions').select('item_id,user_id,amount'),
   supabase.from('mod_chests').select('id,server_id,dimension,x,y,z,label')
 ]);
 if(items.error||contributions.error||chests.error) return NextResponse.json({error:'Datenbankfehler'}, {status:500});
 const totals=new Map<string,number>(); const mine=new Map<string,number>();
 for(const c of contributions.data||[]){totals.set(c.item_id,(totals.get(c.item_id)||0)+Number(c.amount));if(c.user_id===user.id)mine.set(c.item_id,(mine.get(c.item_id)||0)+Number(c.amount));}
 return NextResponse.json({userId:user.id,items:(items.data||[]).map(i=>({...i,collected:totals.get(i.id)||0,mine:mine.get(i.id)||0})),chests:chests.data||[]},{headers:{'Cache-Control':'no-store'}});
}
