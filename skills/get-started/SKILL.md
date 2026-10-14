---
name: get-started
description: First steps after connecting Tavilio. Confirms which venue is connected, summarizes what it runs, and suggests a few useful things to do next.
---

# Get started with Tavilio

Run this right after the user connects Tavilio.

1. Call `venue_overview`. If it fails because the user is not signed in, ask
   them to connect Tavilio again and approve their venue on the sign-in page.
2. Tell the user, in a few lines and in their language:
   - which venue is connected (its name and address);
   - what it runs: table booking or timeframe booking, events, the menu,
     products;
   - its opening hours, or that none are set.
3. If the venue takes bookings, call `list_bookings` for today and the next
   seven days, and say how many there are and how many are waiting for an
   answer. If it runs events, call `list_events` and name the next one.
4. Offer two or three next steps that fit what the venue runs, for example:
   - "Show me this weekend's bookings."
   - "Add a dish to the menu."
   - "Close the venue on a public holiday."
   - "Create an event and put it on the website."

Do not change anything during setup. Only read, summarize and suggest.
