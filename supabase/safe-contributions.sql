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
