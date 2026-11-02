-- Existing installations only: run once (or again safely) in Supabase SQL Editor.
-- Do NOT run schema.sql a second time on an existing installation.
create or replace function public.create_profile() returns trigger
language plpgsql security definer set search_path=public as $$
declare
 chosen_username text;
begin
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
-- A team member may customize their name/color, never the login username.
revoke update on public.profiles from authenticated;
grant update (display_name, avatar_color) on public.profiles to authenticated;
