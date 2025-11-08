-- Enable the UUID extension
create extension if not exists "uuid-ossp" with schema "extensions";

--
-- Profiles Table
-- Holds public user data, linked to the auth.users table.
--
create table "public"."profiles" (
    "id" "uuid" not null,
    "updated_at" timestamp with time zone,
    "username" "text",
    "full_name" "text",
    "avatar_url" "text",
    "website" "text"
);

alter table "public"."profiles" enable row level security;
alter table "public"."profiles" add constraint "profiles_pkey" primary key ("id");
alter table "public"."profiles" add constraint "profiles_id_fkey" foreign key ("id") references "auth"."users" ("id") on delete cascade;

-- Allow users to view their own profile.
create policy "Users can view their own profile." on "public"."profiles"
  for select using (auth.uid() = id);

-- Allow users to update their own profile.
create policy "Users can update their own profile." on "public"."profiles"
  for update using (auth.uid() = id);

--
-- Ads Table
-- Stores the core ad data.
--
create table "public"."ads" (
    "id" "uuid" not null default "extensions"."uuid_generate_v4"(),
    "user_id" "uuid" not null,
    "created_at" timestamp with time zone not null default "now"(),
    "title" "text" not null,
    "description" "text",
    "price" "numeric",
    "category" "text",
    "status" "text" default 'draft',
    "images" "jsonb"
);

alter table "public"."ads" enable row level security;
alter table "public"."ads" add constraint "ads_pkey" primary key ("id");
alter table "public"."ads" add constraint "ads_user_id_fkey" foreign key ("user_id") references "auth"."users" ("id") on delete cascade;

-- Allow users to perform all operations on their own ads.
create policy "Users can manage their own ads." on "public"."ads"
  for all using (auth.uid() = user_id);

--
-- Posted Ads Table
-- Tracks which ads have been posted to which platforms.
--
create table "public"."posted_ads" (
    "id" "uuid" not null default "extensions"."uuid_generate_v4"(),
    "ad_id" "uuid" not null,
    "platform" "text" not null,
    "posted_at" timestamp with time zone not null default "now"(),
    "status" "text"
);

alter table "public"."posted_ads" enable row level security;
alter table "public"."posted_ads" add constraint "posted_ads_pkey" primary key ("id");
alter table "public"."posted_ads" add constraint "posted_ads_ad_id_fkey" foreign key ("ad_id") references "public"."ads" ("id") on delete cascade;

-- Allow users to view their own posted ads (via a join with the ads table).
create policy "Users can view their own posted ads." on "public"."posted_ads"
  for select using (
    exists (
      select 1
      from "public"."ads"
      where "ads"."id" = "posted_ads"."ad_id"
      and "ads"."user_id" = auth.uid()
    )
  );

-- This function is called every time a new user signs up.
-- It creates a corresponding row in the public.profiles table.
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');
  return new;
end;
$$;

-- Trigger the function after a new user is created.
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
