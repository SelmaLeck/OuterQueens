-- Run in Supabase SQL Editor. Account creation: Authentication > Users > Add user.
create extension if not exists pgcrypto;
create table if not exists public.profiles (
 id uuid primary key references auth.users(id) on delete cascade,
 username text not null unique check (username ~ '^[a-zA-Z0-9_]{2,20}$'),
 display_name text not null check (char_length(display_name) between 1 and 32),
 avatar_color text not null default '#38bdf8' check (avatar_color ~ '^#[0-9a-fA-F]{6}$'),
 created_at timestamptz not null default now()
);
create table if not exists public.farms (
 id uuid primary key default gen_random_uuid(), name text not null,
 description text, materials text, schematic_url text,
 status text not null default 'planned' check (status in ('planned','building','ready')),
 created_at timestamptz not null default now()
);
create table if not exists public.items (
 id uuid primary key default gen_random_uuid(),name_de text not null,name_en text not null,
 required bigint not null default 0 check(required>=0),stack_size int not null default 64 check(stack_size between 1 and 64),
 ingredient_name text,ingredient_per_craft int check(ingredient_per_craft>0),output_per_craft int check(output_per_craft>0),
 farm_id uuid references public.farms(id) on delete set null,source_hint text,
 created_at timestamptz not null default now()
);
create table if not exists public.assignments (
 id uuid primary key default gen_random_uuid(),target_type text not null check(target_type in ('item','farm')),
 target_id uuid not null,user_id uuid not null references public.profiles(id) on delete cascade,
 created_at timestamptz not null default now(),unique(target_type,target_id,user_id)
);
create table if not exists public.contributions (
 id uuid primary key default gen_random_uuid(),item_id uuid not null references public.items(id) on delete cascade,
 user_id uuid not null references public.profiles(id) on delete cascade,
 amount bigint not null check(amount>0),created_at timestamptz not null default now()
);
create index if not exists idx_contributions_item on public.contributions(item_id);
create index if not exists idx_contributions_user on public.contributions(user_id);
create index if not exists idx_assignments_target on public.assignments(target_type,target_id);
-- A profile is automatically created when an account is created in Supabase Auth.
create or replace function public.create_profile() returns trigger language plpgsql security definer set search_path=public as $$
declare
 chosen_username text;
begin
 -- Only accept usernames supplied through our admin-created internal login alias.
 chosen_username := lower(coalesce(new.raw_user_meta_data->>'username',''));
 if chosen_username !~ '^[a-z0-9_]{2,20}$'
    or lower(coalesce(new.email,'')) <> chosen_username || '@players.blockforge.invalid' then
   chosen_username := 'player_' || substr(replace(new.id::text,'-',''),1,12);
 end if;
 insert into public.profiles(id,username,display_name)
 values(new.id, chosen_username,
   coalesce(nullif(left(new.raw_user_meta_data->>'display_name',32),''),chosen_username));
 return new;
end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.create_profile();
-- Block anonymous access; authenticated team members share one project.
alter table public.profiles enable row level security;
alter table public.farms enable row level security;
alter table public.items enable row level security;
alter table public.assignments enable row level security;
alter table public.contributions enable row level security;
create policy "profiles read team" on public.profiles for select to authenticated using (true);
create policy "profiles update self" on public.profiles for update to authenticated using (id=(select auth.uid())) with check (id=(select auth.uid()));
-- Display name and avatar may change, but the immutable login username may not.
revoke update on public.profiles from authenticated;
grant update (display_name, avatar_color) on public.profiles to authenticated;
create policy "farms read team" on public.farms for select to authenticated using (true);
create policy "farms add team" on public.farms for insert to authenticated with check (true);
create policy "farms edit team" on public.farms for update to authenticated using (true) with check (true);
create policy "farms delete team" on public.farms for delete to authenticated using (true);
create policy "items read team" on public.items for select to authenticated using (true);
create policy "items add team" on public.items for insert to authenticated with check (true);
create policy "items edit team" on public.items for update to authenticated using (true) with check (true);
create policy "items delete team" on public.items for delete to authenticated using (true);
create policy "assignments read team" on public.assignments for select to authenticated using (true);
create policy "assignments add self" on public.assignments for insert to authenticated with check (user_id=(select auth.uid()));
create policy "assignments delete self" on public.assignments for delete to authenticated using (user_id=(select auth.uid()));
create policy "contributions read team" on public.contributions for select to authenticated using (true);
create policy "contributions add self" on public.contributions for insert to authenticated with check (user_id=(select auth.uid()));
-- Contributions are immutable audit entries: no UPDATE/DELETE policy.
-- Use a public schematics bucket with authenticated uploads.
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('schematics','schematics',true,10485760,null)
on conflict(id) do nothing;
create policy "schematics read" on storage.objects for select to authenticated using(bucket_id='schematics');
create policy "schematics upload" on storage.objects for insert to authenticated with check(bucket_id='schematics');
-- Prevent concurrent farm submissions from exceeding the project's target amount.
-- Safe for both new and existing BLOCKFORGE databases.
create or replace function public.add_contribution_safe(p_item_id uuid, p_amount bigint)
returns void
language plpgsql security definer set search_path=public
as $$
declare
  goal bigint;
  current_total bigint;
begin
  if auth.uid() is null then
    raise exception 'Nur angemeldete Spieler dürfen Beiträge eintragen.';
  end if;
  if p_amount is null or p_amount <= 0 then
    raise exception 'Die Anzahl muss positiv sein.';
  end if;
  -- Serialize submissions for the SAME item to prevent over-collection.
  select required into goal from public.items where id = p_item_id for update;
  if not found then
    raise exception 'Item nicht gefunden.';
  end if;
  select coalesce(sum(amount),0) into current_total from public.contributions where item_id = p_item_id;
  if current_total + p_amount > goal then
    raise exception 'Nur noch % Items fehlen.', greatest(goal - current_total,0);
  end if;
  insert into public.contributions(item_id,user_id,amount) values(p_item_id,auth.uid(),p_amount);
end;
$$;
revoke all on function public.add_contribution_safe(uuid,bigint) from public;
grant execute on function public.add_contribution_safe(uuid,bigint) to authenticated;
