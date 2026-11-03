-- In Supabase SQL Editor run once (no seed rerun).
-- Keep existing item contributions and profiles intact.
create table if not exists public.mod_chests (
 id uuid primary key default gen_random_uuid(),
 server_id text not null check (char_length(server_id) between 3 and 100),
 dimension text not null check (char_length(dimension) between 3 and 128),
 x int not null, y int not null, z int not null,
 label text not null default 'OuterQueens Abgabe',
 created_by uuid not null references public.profiles(id),
 created_at timestamptz not null default now(),
 unique(server_id, dimension, x, y, z)
);
create table if not exists public.mod_delivery_events (
 event_id uuid primary key,
 user_id uuid not null references public.profiles(id),
 chest_id uuid not null references public.mod_chests(id),
 item_id uuid not null references public.items(id),
 amount bigint not null check (amount > 0 and amount <= 2304),
 created_at timestamptz not null default now()
);
create index if not exists mod_delivery_events_user_idx on public.mod_delivery_events(user_id);
alter table public.mod_chests enable row level security;
alter table public.mod_delivery_events enable row level security;
-- All team members may read the registered drop-off points.
drop policy if exists mod_chests_read_team on public.mod_chests;
create policy mod_chests_read_team on public.mod_chests for select to authenticated using (true);
drop policy if exists mod_events_read_team on public.mod_delivery_events;
create policy mod_events_read_team on public.mod_delivery_events for select to authenticated using (true);
-- Direct writes blocked; mutations go through checked RPCs.
revoke insert, update, delete on public.mod_chests from authenticated, anon;
revoke insert, update, delete on public.mod_delivery_events from authenticated, anon;
grant select on public.mod_chests, public.mod_delivery_events to authenticated;

create or replace function public.register_mod_chest(
 p_server_id text, p_dimension text, p_x int, p_y int, p_z int, p_label text default 'OuterQueens Abgabe'
) returns uuid language plpgsql security definer set search_path=public as $$
declare v_id uuid;
begin
 if auth.uid() is null then raise exception 'Login erforderlich'; end if;
 if p_server_id is null or char_length(p_server_id) not between 3 and 100
   or p_dimension is null or char_length(p_dimension) not between 3 and 128
   or p_label is null or char_length(p_label) not between 1 and 80 then
   raise exception 'Ungültige Abgabekiste';
 end if;
 insert into public.mod_chests(server_id,dimension,x,y,z,label,created_by)
 values(p_server_id,p_dimension,p_x,p_y,p_z,p_label,auth.uid())
 on conflict(server_id,dimension,x,y,z) do update set label=excluded.label
 returning id into v_id;
 return v_id;
end $$;
revoke all on function public.register_mod_chest(text,text,int,int,int,text) from public;
grant execute on function public.register_mod_chest(text,text,int,int,int,text) to authenticated;

create or replace function public.record_mod_delivery(
 p_event_id uuid, p_chest_id uuid, p_item_id uuid, p_amount bigint
) returns text language plpgsql security definer set search_path=public as $$
declare v_goal bigint; v_collected bigint;
begin
 if auth.uid() is null then raise exception 'Login erforderlich'; end if;
 if p_amount is null or p_amount < 1 or p_amount > 2304 then raise exception 'Ungültige Anzahl'; end if;
 if not exists(select 1 from public.mod_chests where id=p_chest_id) then
   raise exception 'Abgabekiste nicht registriert';
 end if;
 -- Locks item row to serialize both concurrent mod submissions and existing safe RPC submissions.
 select required into v_goal from public.items where id=p_item_id for update;
 if not found then raise exception 'Item nicht in OuterQueens'; end if;
 -- Preserve idempotency after retries: no second contribution for the same delivery ID.
 if exists(select 1 from public.mod_delivery_events where event_id=p_event_id) then
   if exists(select 1 from public.mod_delivery_events where event_id=p_event_id and user_id=auth.uid()
       and chest_id=p_chest_id and item_id=p_item_id and amount=p_amount) then
     return 'already_recorded';
   end if;
   raise exception 'Lieferungs-ID bereits vergeben';
 end if;
 select coalesce(sum(amount),0) into v_collected from public.contributions where item_id=p_item_id;
 if v_collected + p_amount > v_goal then
   raise exception 'Zielmenge überschritten; fehlen noch %', greatest(v_goal - v_collected,0);
 end if;
 insert into public.mod_delivery_events(event_id,user_id,chest_id,item_id,amount)
 values(p_event_id,auth.uid(),p_chest_id,p_item_id,p_amount);
 insert into public.contributions(item_id,user_id,amount)
 values(p_item_id,auth.uid(),p_amount);
 return 'recorded';
end $$;
revoke all on function public.record_mod_delivery(uuid,uuid,uuid,bigint) from public;
grant execute on function public.record_mod_delivery(uuid,uuid,uuid,bigint) to authenticated;
