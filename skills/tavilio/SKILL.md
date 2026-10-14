---
name: tavilio
description: Run a restaurant, café, studio or event venue on Tavilio — its bookings, events, menu and products, opening hours and website — through the Tavilio MCP server. Use when the user asks about their Tavilio venue or wants to change something in it.
---

# Running a venue on Tavilio

Tavilio is the booking system and website of one venue: a restaurant, café,
bar, studio or a place that runs classes and events. The Tavilio MCP server
acts on the venue the user approved when they signed in, with the powers of
one of its admins. It never reaches another venue, the plan or billing, or the
team's accounts.

## Start here

Call `venue_overview` first. It returns the venue's name, languages, time zone,
what it runs (table booking, timeframe booking, events, menu, products), its
booking rules and its opening hours. Read it before answering, and use its
facts rather than assumptions.

## Things to know

- **Times are the venue's local time.** Dates are `YYYY-MM-DD`, times `HH:MM`,
  in the time zone `venue_overview` names. Convert anything the user says
  ("next Friday", "tonight") to the venue's dates before calling a tool.
- **Text in several languages.** A translatable field takes a plain string in
  the venue's own language, or an object such as `{"hu": "…", "en": "…"}`.
  Keep the languages the venue publishes; `venue_overview` lists them.
- **Read before you write.** Look a thing up (`list_bookings`, `list_events`,
  `get_menu`, `list_site_pages`) before changing it, and pass the ids those
  return. Editing an item changes only the fields you send.
- **Some actions reach guests.** Approving, declining or cancelling a booking
  emails the guest; cancelling an event emails everyone signed up and cannot
  be undone. Say what will happen and get the user's go-ahead before these.
- **Pictures.** The website shows only pictures stored with the venue. Bring a
  picture from a public link in with `import_image`, then use the `src` it
  returns.
- **Personal data.** Guests' names, emails, phone numbers and signup answers
  are for the venue's own use. Show them to the user when asked; do not copy
  them anywhere else.

## Common tasks

| The user wants to… | Tools |
| --- | --- |
| See who is coming | `list_bookings`, `get_booking` |
| Answer a booking request | `approve_booking`, `decline_booking` |
| Take a booking by phone | `check_availability`, then `create_booking` |
| Plan an event or a course | `save_event`, `set_event_published`, `list_event_signups` |
| Update the menu or products | `get_menu`, `save_menu_item`, `create_menu_category` |
| Change opening hours or close a day | `set_opening_hours`, `add_closed_day` |
| Edit the website | `list_site_pages`, `get_site_page`, `save_site_page`, `set_site_style` |
| See how it is going | `venue_stats` |

If a request needs something the tools do not offer (payments, refunds, the
plan, inviting people to the team), say so and point the user to the Tavilio
admin.
