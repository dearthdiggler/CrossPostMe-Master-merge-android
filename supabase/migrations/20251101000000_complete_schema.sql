-- Enable the UUID extension
create extension if not exists "uuid-ossp" with schema "extensions";

--
-- Users Table (extends auth.users with additional fields)
--
create table "public"."users" (
    "id" "uuid" not null,
    "email" "text" not null,
    "username" "text",
    "is_active" boolean not null default true,
    "created_at" timestamp with time zone not null default "now"(),
    "updated_at" timestamp with time zone not null default "now"()
);

alter table "public"."users" enable row level security;
alter table "public"."users" add constraint "users_pkey" primary key ("id");
alter table "public"."users" add constraint "users_id_fkey" foreign key ("id") references "auth"."users" ("id") on delete cascade;
alter table "public"."users" add constraint "users_email_key" unique ("email");
alter table "public"."users" add constraint "users_username_key" unique ("username");

-- Allow users to view their own data
create policy "Users can view their own data." on "public"."users"
  for select using (auth.uid() = id);

-- Allow users to update their own data
create policy "Users can update their own data." on "public"."users"
  for update using (auth.uid() = id);

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
-- User Business Profiles Table
--
create table "public"."user_business_profiles" (
    "id" "uuid" not null default "extensions"."uuid_generate_v4"(),
    "user_id" "uuid" not null,
    "company_name" "text",
    "industry" "text",
    "monthly_revenue" "text",
    "employee_count" "text",
    "business_description" "text",
    "created_at" timestamp with time zone not null default "now"(),
    "updated_at" timestamp with time zone not null default "now"()
);

alter table "public"."user_business_profiles" enable row level security;
alter table "public"."user_business_profiles" add constraint "user_business_profiles_pkey" primary key ("id");
alter table "public"."user_business_profiles" add constraint "user_business_profiles_user_id_fkey" foreign key ("user_id") references "public"."users" ("id") on delete cascade;
alter table "public"."user_business_profiles" add constraint "user_business_profiles_user_id_key" unique ("user_id");

-- Allow users to manage their own business profile
create policy "Users can manage their own business profile." on "public"."user_business_profiles"
  for all using (auth.uid() = user_id);

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
alter table "public"."ads" add constraint "ads_user_id_fkey" foreign key ("user_id") references "public"."users" ("id") on delete cascade;

-- Allow users to perform all operations on their own ads.
create policy "Users can manage their own ads." on "public"."ads"
  for all using (auth.uid() = user_id);

--
-- Listings Table (separate from ads for marketplace functionality)
--
create table "public"."listings" (
    "id" "uuid" not null default "extensions"."uuid_generate_v4"(),
    "user_id" "uuid" not null,
    "title" "text" not null,
    "description" "text",
    "price" "numeric",
    "category" "text",
    "status" "text" default 'draft',
    "images" "jsonb",
    "location" "text",
    "condition" "text",
    "created_at" timestamp with time zone not null default "now"(),
    "updated_at" timestamp with time zone not null default "now"()
);

alter table "public"."listings" enable row level security;
alter table "public"."listings" add constraint "listings_pkey" primary key ("id");
alter table "public"."listings" add constraint "listings_user_id_fkey" foreign key ("user_id") references "public"."users" ("id") on delete cascade;

-- Allow users to manage their own listings
create policy "Users can manage their own listings." on "public"."listings"
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
    "status" "text",
    "external_id" "text",
    "external_url" "text"
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

--
-- Platform Connections Table
--
create table "public"."platform_connections" (
    "id" "uuid" not null default "extensions"."uuid_generate_v4"(),
    "user_id" "uuid" not null,
    "platform" "text" not null,
    "access_token" "text",
    "refresh_token" "text",
    "token_expires_at" timestamp with time zone,
    "account_id" "text",
    "account_name" "text",
    "status" "text" default 'active',
    "created_at" timestamp with time zone not null default "now"(),
    "updated_at" timestamp with time zone not null default "now"()
);

alter table "public"."platform_connections" enable row level security;
alter table "public"."platform_connections" add constraint "platform_connections_pkey" primary key ("id");
alter table "public"."platform_connections" add constraint "platform_connections_user_id_fkey" foreign key ("user_id") references "public"."users" ("id") on delete cascade;
alter table "public"."platform_connections" add constraint "platform_connections_user_platform_key" unique ("user_id", "platform");

-- Allow users to manage their own platform connections
create policy "Users can manage their own platform connections." on "public"."platform_connections"
  for all using (auth.uid() = user_id);

--
-- Business Intelligence Table
--
create table "public"."business_intelligence" (
    "id" "uuid" not null default "extensions"."uuid_generate_v4"(),
    "user_id" "uuid",
    "event_type" "text" not null,
    "event_data" "jsonb",
    "timestamp" timestamp with time zone not null default "now"()
);

alter table "public"."business_intelligence" enable row level security;
alter table "public"."business_intelligence" add constraint "business_intelligence_pkey" primary key ("id");

-- Allow users to view their own events, allow inserts for all (for anonymous tracking)
create policy "Users can view their own events." on "public"."business_intelligence"
  for select using (auth.uid() = user_id);

create policy "Allow event inserts." on "public"."business_intelligence"
  for insert with check (true);

--
-- Analytics Views
--

-- Industry breakdown view
create view "industry_breakdown" as
select
    industry,
    count(*) as count
from "public"."user_business_profiles"
where industry is not null
group by industry
order by count desc;

-- User stats view
create view "user_stats" as
select
    u.id,
    u.email,
    u.username,
    u.created_at,
    p.full_name,
    b.company_name,
    b.industry,
    b.monthly_revenue,
    (select count(*) from "public"."ads" a where a.user_id = u.id) as ads_count,
    (select count(*) from "public"."listings" l where l.user_id = u.id) as listings_count,
    (select count(*) from "public"."platform_connections" pc where pc.user_id = u.id) as platforms_connected
from "public"."users" u
left join "public"."profiles" p on u.id = p.id
left join "public"."user_business_profiles" b on u.id = b.user_id
order by u.created_at desc;

-- Function to increment listing views (for analytics)
create or replace function increment_listing_views(listing_id uuid, platform_name text)
returns void
language plpgsql
security definer
as $$
begin
  -- Log the view event
  insert into "public"."business_intelligence" (event_type, event_data)
  values ('listing_view', jsonb_build_object('listing_id', listing_id, 'platform', platform_name));

  -- Could also maintain a separate views counter table if needed
end;
$$;

-- This function is called every time a new user signs up.
-- It creates a corresponding row in the public.users and profiles tables.
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  -- Insert into users table
  insert into public.users (id, email, username)
  values (new.id, new.email, new.raw_user_meta_data->>'username');

  -- Insert into profiles table
  insert into public.profiles (id, full_name, avatar_url)
  values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');

  return new;
end;
$$;

-- Trigger the function after a new user is created.
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();